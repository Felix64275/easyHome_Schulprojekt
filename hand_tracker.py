import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gesture_detector import GestureDetector
from mqtt_client import send_gesture


class HandTracker:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        self.gesture_detector = GestureDetector()

        self.last_sent_gesture = ""
        self.current_gesture = ""
        self.gesture_counter = 0
        self.required_frames = 5
        self.last_send_time = 0
        self.cooldown_seconds = 1.5

        base_options = python.BaseOptions(
            model_asset_path="gesture_recognizer.task"
        )

        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )

        self.recognizer = vision.GestureRecognizer.create_from_options(options)

    def draw_landmarks(self, frame, hand_landmarks):
        height, width, _ = frame.shape

        for landmark in hand_landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    def start(self):
        while True:
            success, frame = self.cap.read()

            if not success:
                print("Kamera konnte nicht geöffnet werden.")
                break

            frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            timestamp_ms = int(time.time() * 1000)

            result = self.recognizer.recognize_for_video(
                mp_image,
                timestamp_ms
            )

            gesture = ""

            if result.gestures:
                mediapipe_gesture = result.gestures[0][0].category_name
                gesture = self.gesture_detector.convert_gesture(mediapipe_gesture)

                if result.hand_landmarks:
                    for hand_landmarks in result.hand_landmarks:
                        self.draw_landmarks(frame, hand_landmarks)

                if gesture == self.current_gesture:
                    self.gesture_counter += 1
                else:
                    self.current_gesture = gesture
                    self.gesture_counter = 0

                current_time = time.time()

                if (
                    gesture != ""
                    and self.gesture_counter >= self.required_frames
                    and current_time - self.last_send_time >= self.cooldown_seconds
                ):
                    send_gesture(gesture)
                    self.last_sent_gesture = gesture
                    self.last_send_time = current_time
                    self.gesture_counter = 0

                cv2.putText(
                    frame,
                    gesture,
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 0, 0),
                    2
                )

                cv2.putText(
                    frame,
                    "MediaPipe: " + mediapipe_gesture,
                    (30, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Hand erkannt",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

            cv2.imshow("SmartHome - Gestenerkennung", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()