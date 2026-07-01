import cv2
import time
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gesture_detector import GestureDetector
from mqtt_client import send_gesture
from dashboard import Dashboard


HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


class HandTracker:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        # Kameraauflösung anfordern
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.gesture_detector = GestureDetector()
        self.dashboard = Dashboard()

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

        self.recognizer = (
            vision.GestureRecognizer.create_from_options(
                options
            )
        )

    def crop_to_16_9(self, frame):
        """Schneidet das Bild auf 16:9 zu, ohne es zu verzerren."""

        height, width = frame.shape[:2]
        target_ratio = 16 / 9
        current_ratio = width / height

        if current_ratio > target_ratio:
            new_width = int(height * target_ratio)
            start_x = (width - new_width) // 2
            frame = frame[:, start_x:start_x + new_width]

        elif current_ratio < target_ratio:
            new_height = int(width / target_ratio)
            start_y = (height - new_height) // 2
            frame = frame[start_y:start_y + new_height, :]

        return cv2.resize(frame, (960, 540))

    def draw_rounded_rectangle(
        self,
        image,
        top_left,
        bottom_right,
        color,
        radius=18,
        thickness=-1
    ):
        x1, y1 = top_left
        x2, y2 = bottom_right

        if thickness != -1:
            cv2.rectangle(
                image,
                top_left,
                bottom_right,
                color,
                thickness
            )
            return

        cv2.rectangle(
            image,
            (x1 + radius, y1),
            (x2 - radius, y2),
            color,
            -1
        )

        cv2.rectangle(
            image,
            (x1, y1 + radius),
            (x2, y2 - radius),
            color,
            -1
        )

        cv2.circle(
            image,
            (x1 + radius, y1 + radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            image,
            (x2 - radius, y1 + radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            image,
            (x1 + radius, y2 - radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            image,
            (x2 - radius, y2 - radius),
            radius,
            color,
            -1
        )

    def draw_hand(self, frame, hand_landmarks):
        height, width = frame.shape[:2]
        points = []

        for landmark in hand_landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            points.append((x, y))

        # Leuchtender Schatten für die Linien
        for start, end in HAND_CONNECTIONS:
            cv2.line(
                frame,
                points[start],
                points[end],
                (20, 90, 70),
                7,
                cv2.LINE_AA
            )

        # Eigentliche Handskelett-Linien
        for start, end in HAND_CONNECTIONS:
            cv2.line(
                frame,
                points[start],
                points[end],
                (70, 255, 190),
                3,
                cv2.LINE_AA
            )

        # Handpunkte
        for index, point in enumerate(points):
            if index in [4, 8, 12, 16, 20]:
                radius = 7
                color = (0, 220, 255)
            else:
                radius = 5
                color = (70, 255, 190)

            cv2.circle(
                frame,
                point,
                radius + 3,
                (15, 70, 60),
                -1,
                cv2.LINE_AA
            )

            cv2.circle(
                frame,
                point,
                radius,
                color,
                -1,
                cv2.LINE_AA
            )

            cv2.circle(
                frame,
                point,
                radius,
                (240, 255, 250),
                1,
                cv2.LINE_AA
            )

    def draw_camera_interface(
        self,
        frame,
        gesture,
        mediapipe_gesture,
        confidence
    ):
        overlay = frame.copy()

        # Dunkle obere Statusleiste
        self.draw_rounded_rectangle(
            overlay,
            (18, 18),
            (942, 112),
            (10, 20, 32),
            radius=20
        )

        cv2.addWeighted(
            overlay,
            0.78,
            frame,
            0.22,
            0,
            frame
        )

        # easyHome-Titel
        cv2.putText(
            frame,
            "easyHome",
            (40, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "HANDSTEUERUNG",
            (40, 82),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (145, 165, 185),
            1,
            cv2.LINE_AA
        )

        # Kamera-Live-Anzeige
        cv2.circle(
            frame,
            (215, 49),
            6,
            (70, 255, 170),
            -1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "LIVE",
            (230, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (70, 255, 170),
            1,
            cv2.LINE_AA
        )

        shown_gesture = (
            gesture if gesture else "Keine Aktion"
        )

        gesture_color = (
            (70, 255, 190)
            if gesture
            else (160, 175, 190)
        )

        cv2.putText(
            frame,
            shown_gesture,
            (340, 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            gesture_color,
            2,
            cv2.LINE_AA
        )

        media_text = (
            f"MediaPipe: {mediapipe_gesture}"
            if mediapipe_gesture
            else "MediaPipe: Keine Hand erkannt"
        )

        cv2.putText(
            frame,
            media_text,
            (340, 88),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.44,
            (165, 185, 205),
            1,
            cv2.LINE_AA
        )

        if mediapipe_gesture:
            confidence_text = (
                f"{int(confidence * 100)}%"
            )

            cv2.putText(
                frame,
                confidence_text,
                (865, 72),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 220, 255),
                2,
                cv2.LINE_AA
            )

        # Untere Hilfeleiste
        bottom_overlay = frame.copy()

        self.draw_rounded_rectangle(
            bottom_overlay,
            (270, 490),
            (690, 526),
            (10, 20, 32),
            radius=16
        )

        cv2.addWeighted(
            bottom_overlay,
            0.72,
            frame,
            0.28,
            0,
            frame
        )

        cv2.putText(
            frame,
            "Q druecken zum Beenden",
            (360, 514),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.43,
            (190, 205, 220),
            1,
            cv2.LINE_AA
        )

    def start(self):
        if not self.cap.isOpened():
            print("Kamera konnte nicht geöffnet werden.")
            self.dashboard.close()
            return

        cv2.namedWindow(
            "easyHome - Handsteuerung",
            cv2.WINDOW_NORMAL
        )

        cv2.resizeWindow(
            "easyHome - Handsteuerung",
            960,
            540
        )

        try:
            while True:
                success, frame = self.cap.read()

                if not success:
                    print(
                        "Kamerabild konnte nicht gelesen werden."
                    )
                    break

                frame = cv2.flip(frame, 1)

                # Format verbessern, ohne Verzerrung
                frame = self.crop_to_16_9(frame)

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

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
                mediapipe_gesture = ""
                confidence = 0.0

                if result.gestures:
                    detected_gesture = result.gestures[0][0]

                    mediapipe_gesture = (
                        detected_gesture.category_name
                    )

                    confidence = detected_gesture.score

                    gesture = (
                        self.gesture_detector.convert_gesture(
                            mediapipe_gesture
                        )
                    )

                    if result.hand_landmarks:
                        for hand_landmarks in result.hand_landmarks:
                            self.draw_hand(
                                frame,
                                hand_landmarks
                            )

                    if (
                        gesture
                        and gesture == self.current_gesture
                    ):
                        self.gesture_counter += 1

                    elif gesture:
                        self.current_gesture = gesture
                        self.gesture_counter = 1

                    else:
                        self.current_gesture = ""
                        self.gesture_counter = 0

                    current_time = time.time()

                    if (
                        gesture
                        and self.gesture_counter
                        >= self.required_frames
                        and current_time - self.last_send_time
                        >= self.cooldown_seconds
                    ):
                        send_gesture(gesture)

                        self.dashboard.set_last_action(
                            gesture
                        )

                        self.last_send_time = current_time
                        self.gesture_counter = 0

                else:
                    self.current_gesture = ""
                    self.gesture_counter = 0

                self.dashboard.update_gesture(
                    gesture,
                    mediapipe_gesture
                )

                self.draw_camera_interface(
                    frame,
                    gesture,
                    mediapipe_gesture,
                    confidence
                )

                cv2.imshow(
                    "easyHome - Handsteuerung",
                    frame
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            self.cap.release()
            self.recognizer.close()
            self.dashboard.close()
            cv2.destroyAllWindows()