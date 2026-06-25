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
        self.last_gesture = ""

        base_options = python.BaseOptions(
            model_asset_path="hand_landmarker.task"
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

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

            result = self.detector.detect_for_video(
                mp_image,
                timestamp_ms
            )

            if result.hand_landmarks:
                for hand_landmarks in result.hand_landmarks:
                    self.draw_landmarks(frame, hand_landmarks)

                    gesture = self.gesture_detector.detect_gesture(hand_landmarks)

                    if gesture != "" and gesture != self.last_gesture:
                        send_gesture(gesture)
                        self.last_gesture = gesture

                    cv2.putText(
                        frame,
                        gesture,
                        (30, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
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

            cv2.imshow("SmartHome - Handerkennung", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()