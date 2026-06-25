class GestureDetector:

    def detect_gesture(self, hand_landmarks):

        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]

        offene_finger = 0

        # Offene Finger zählen
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks[tip].y < hand_landmarks[pip].y:
                offene_finger += 1

        # Hand offen → Licht AN
        if offene_finger >= 4:
            return "LICHT AN"

        # Faust → Licht AUS
        if offene_finger == 0:
            return "LICHT AUS"

        # Ein Finger → Rollladen AUF
        if offene_finger == 1:
            return "ROLLLADEN AUF"

        # Zwei Finger → Rollladen ZU
        if offene_finger == 2:
            return "ROLLLADEN ZU"

        return ""