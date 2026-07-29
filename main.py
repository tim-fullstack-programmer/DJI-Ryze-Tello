from djitellopy import tello
import json, pyaudio
import keyboard
import cv2
import time
import mediapipe as mp
from utils.PlotModule import LivePlot
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox,QGridLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from vosk import Model, KaldiRecognizer
import numpy as np

gui = None
gui_loaded_event = threading.Event() # создаю событие
photo_button_pressed = threading.Event()

def thread(my_func):
    def wrapper():
        my_thread = threading.Thread(target=my_func)
        my_thread.daemon = True
        my_thread.start()
    return wrapper

drone = tello.Tello()


def folow(self):
    print(1)

    width, height = 640, 480

    xPID, yPID, zPID = [0.21, 0, 0.1], [0.27, 0, 0.1], [0.0021, 0, 0.1]
    xTarget, yTarget, zTarget = width // 2, height // 2, 11500
    pError, pTime, I = 0, 0, 0
    myPlotX = LivePlot(yLimit=[-width // 2, width // 2], char='X')
    myPlotY = LivePlot(yLimit=[-height // 2, height // 2], char='Y')
    myPlotZ = LivePlot(yLimit=[-100, 100], char='z')

    mpFaces = mp.solutions.face_detection
    Faces = mpFaces.FaceDetection(min_detection_confidence=0.5, model_selection=1)
    mpDraw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)



    def PIDController(PID, img, target, cVal, limit=[-100, 100], pTime=0, pError=0, I=0, draw=False):

        t = time.time() - pTime
        error = target - cVal
        P = PID[0] * error
        I = I + (PID[1] * error * t)
        D = PID[2] * (error - pError) / t

        val = P + I + D
        val = float(np.clip(val, limit[0], limit[1]))
        if draw:
            cv2.putText(img, str(int(val)), (50, 70), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 255), 3)

        return int(val)

    while True:
        img = drone.get_frame_read().frame
        img = cv2.resize(img, (width, height))
        xVal, yVal, zVal = 0, 0, 0

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = Faces.process(imgRGB)

        bboxs = []
        if results.detections:

            for id, detection in enumerate(results.detections):
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                cx, cy = bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2
                bboxInfo = {'id': id, 'bbox': bbox, 'score': detection.score, 'center': (cx, cy)}
                bboxs.append(bboxInfo)

                cv2.rectangle(img, bbox, (0, 255, 0), 2)
            cv2.putText(img, str(int(bboxs[0]['score'][0] * 100)) + ' %', (bbox[0] + 5, bbox[1] - 10),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            cx, cy = bboxs[0]['center']
            x, y, w, h = bboxs[0]['bbox']
            area = w * h
            cv2.putText(img, str(area), (50, 200), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 5, (255, 255, 0), cv2.FILLED)

            cv2.line(img, (width // 2, 0), (width // 2, height), (255, 255, 255), 1)
            cv2.line(img, (width // 2, cy), (cx, cy), (255, 255, 255), 1)

            cv2.line(img, (0, height // 2), (width, height // 2), (255, 255, 255), 1)
            cv2.line(img, (cx, height // 2), (cx, cy), (255, 255, 255), 1)

            xVal = PIDController(xPID, img, xTarget, cx)
            yVal = PIDController(yPID, img, yTarget, cy)
            zVal = PIDController(zPID, img, zTarget, area, limit=[-20, 15], draw=True)

            imgPlotX = myPlotX.update(xVal)
            imgPlotY = myPlotY.update(yVal)
            imgPlotZ = myPlotZ.update(zVal)

            stackImg1 = np.hstack((img, imgPlotX))
            stackImg2 = np.hstack((imgPlotY, imgPlotZ))
            stackImg = np.vstack((stackImg1, stackImg2))
        else:
            blank = np.zeros((height, width, 3), np.uint8)
            stackImg1 = np.hstack((img, blank))
            stackImg2 = np.hstack((blank, blank))
            stackImg = np.vstack((stackImg1, stackImg2))

        drone.send_rc_control(0, zVal, yVal, -xVal)
        cv2.imshow('Image', stackImg)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            break

keyboard.on_press_key("space", lambda x: main("посадка"))
keyboard.on_press_key("f", lambda x: main("взлёт"))
keyboard.on_press_key("w", lambda x: main("вперёд"))
keyboard.on_press_key("s", lambda x: main("назад"))
keyboard.on_press_key("a", lambda x: main("влево"))
keyboard.on_press_key("d", lambda x: main("вправо"))
keyboard.on_press_key("shift", lambda x: main("вверх"))
keyboard.on_press_key("ctrl", lambda x: main("вниз"))
keyboard.on_press_key("q", lambda x: drone.rotate_counter_clockwise(30))
keyboard.on_press_key("e", lambda x: drone.rotate_clockwise(30))
keyboard.on_press_key("p", lambda x: photo_button_pressed.set())
keyboard.on_press_key("U", lambda x: folow(1))


count = 0

def main(text):
    x = 50
    y = 50
    if text == "взлёт":
        drone.takeoff()
        print(drone.get_battery())
        print(text)

    if text == "посадка":
        print(text)
        drone.land()
        print(drone.get_battery())
        drone.streamoff()
        drone.end()
        exit()

    if text in ["вверх", "в верх", "верх"]:
        print(text)
        drone.move_up(y)
        print(drone.get_battery())

    if text in ["вниз", "в низ", "низ"]:
        print(text)
        drone.move_down(y)
        print(drone.get_battery())

    if text in ["вперёд", "перед", "вперед"]:
        print(text)
        drone.move_forward(x)
        print(drone.get_battery())

    if text in ["назад", "зад"]:
        drone.move_back(x)
        print(drone.get_battery())

    if text in ["в лево", "влево", "лево"]:
        print(text)
        drone.move_left(x)
        print(drone.get_battery())

    if text in ["в право", "вправо", "право", "в правом", "правом", "права", "праву"]:
        print(text)
        drone.move_right(x)
        print(drone.get_battery())

def listen():
    model = Model('vosk-model-small-ru-0.4')
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data) > 0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']

class DroneControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_mic_on = True
        self.initUI()
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video)
        self.video_timer.start(30)

    def initUI(self):
        self.setWindowTitle("Drone Control")
        self.setGeometry(100, 100, 900, 700)

        self.setStyleSheet("background-color: #87cefa;")

        layout = QGridLayout()

        self.battery_label = QLabel("Заряд батареи: 100%", self)
        self.battery_label.setStyleSheet("font-size: 18px; color: #008000;")
        layout.addWidget(self.battery_label, 0, 0, 1, 3, Qt.AlignCenter)

        self.altitude_label = QLabel("Высота: 0 м", self)
        self.altitude_label.setStyleSheet("font-size: 18px; color: blue;")
        layout.addWidget(self.altitude_label, 4, 0, 1, 3, Qt.AlignCenter)

        buttons = {
            "Взлёт" "\U0001F6EB": (5, 0, lambda: main("взлёт")),
            "Посадка" "\U0001f6ec": (5, 2, lambda: main("посадка")),
            "Вверх" "\u23EB": (6, 1, lambda: main("вверх")),
            "Вниз" "\u23EC": (7, 1, lambda: main("вниз")),
            "Влево ⬅️": (9, 0, lambda: main("влево")),
            "Вперёд ⬆️": (8, 1, lambda: main("вперёд")),
            "Вправо ➡️": (9, 2, lambda: main("вправо")),
            "Назад ⬇️": (9, 1, lambda: main("назад")),
            "Вращение влево" "\U0001f504": (12, 0, lambda: drone.rotate_counter_clockwise(30)),
            "Вращение вправо" "\U0001f503": (12, 2, lambda: drone.rotate_clockwise(30)),
            "⚪": (13, 2, lambda:photo_button_pressed.set()),

        }

        for label, (row, col, action) in buttons.items():
            btn = QPushButton(label, self)
            btn.clicked.connect(action)
            btn.setStyleSheet(
                "font-size: 20px; padding: 15px; background-color: #FF6F61; color: white; border-radius: 10px;"
            )
            layout.addWidget(btn, row, col)

        enable_mic_button = QPushButton("Включить микрофон", self)
        enable_mic_button.clicked.connect(self.enable_mic)
        enable_mic_button.setStyleSheet(
            "font-size: 20px; padding: 10px; background-color: #008000; color: white; border-radius: 10px;"
        )
        layout.addWidget(enable_mic_button, 11, 0, 1, 3, Qt.AlignCenter)

        disable_mic_button = QPushButton("Выключить микрофон", self)
        disable_mic_button.clicked.connect(self.disable_mic)
        disable_mic_button.setStyleSheet(
            "font-size: 20px; padding: 10px; background-color: #ff0000; color: white; border-radius: 10px;"
        )
        layout.addWidget(disable_mic_button, 12, 0, 1, 3, Qt.AlignCenter)

        help_button = QPushButton("Справка", self)
        help_button.clicked.connect(self.show_help)
        help_button.setStyleSheet(
            "font-size: 20px; padding: 10px; background-color: #008b8b; color: white; border-radius: 10px;"
        )
        layout.addWidget(help_button, 13, 0, 1, 3, Qt.AlignCenter)

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #000;")
        layout.addWidget(self.video_label, 14, 0, 1, 3, Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_video(self):
        global count
        try:
            frame = drone.get_frame_read().frame
            if frame is not None:
                #     frame_conv = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB) # цветовой
                #        cv2.imwrite("frame_conv.png", frame_conv)  # картинка ок
                height, width, channel = frame.shape
                qimg = QImage(frame.data, width, height, channel * width, QImage.Format_RGB888)

                if photo_button_pressed.is_set():
                    qimg.save(f"frame_qimg{count}.png", "PNG", -1) #запись фото
                    count += 1
                    photo_button_pressed.clear()

                self.video_label.setPixmap(QPixmap.fromImage(qimg))
                if drone.is_flying:
                    bat = drone.get_battery()
                    self.battery_label.setText(f"Заряд батареи: {bat}%")
                    alt = drone.get_height()
                    self.altitude_label.setText(f"Высота:{alt/100}м")


        except Exception as e:
            print("Ошибка при обновлении видео: ", e)


    def enable_mic(self):
        self.is_mic_on = True
        print("Голосовое управление включено.")

    def disable_mic(self):
        self.is_mic_on = False
        print("Голосовое управление отключено.")

    def show_help(self):
        help_message = """
        Управление дроном:
        - Взлёт: Поднимает дрон в воздух.
        - Посадка: Приземляет дрон.
        - Вперёд, Назад, Влево, Вправо: Направления движения.
        - Вверх, Вниз: Управляют высотой.
        - Включить/Выключить микрофон: Активировать или деактивировать голосовое управление.
        ⚪ - сделать снимок
        
        
        f- взлёт
        space - посадка
        w - вперёд
        s - назад
        a - вправо 
        d - вправо 
        a - влево
        q - вращение влево 
        e - вращение вправо 
        shift - вверх
        cntrl - вниз
        U - режим следование за лицом(для выхода из режима нажать в окне кнопку посадки, после чего дрон сядет)
        
        
                                        Голосвые комады
        взлёт
        посадка
        вперёд
        назад
        вправо 
        влево
        вверх 
        вниз
        """
        QMessageBox.information(self, "Справка", help_message)

@thread
def start_gui():
    global gui
    app = QApplication([])
    gui = DroneControlGUI()
    gui_loaded_event.set() # запустить событие
    gui.show()
    app.exec()

if __name__ == "__main__":
    drone.connect()
    drone.streamon()
    start_gui()
    gui_loaded_event.wait() # ждем пока триггернет событие
    while True:
        #if gui is None:
         #  continue # прекращаем работать

        try:
            if gui.is_mic_on:
                command = next(listen())
                main(command)
        except Exception as e:
            print(f"Ошибка в основном цикле: {e}")