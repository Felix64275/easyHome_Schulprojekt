class GestureDetector:

    def convert_gesture(self, mediapipe_gesture):

        if mediapipe_gesture == "Closed_Fist":
            return "ALLE LICHTER AUS"

        elif mediapipe_gesture == "Open_Palm":
            return "WOHNZIMMER LICHT AN"

        elif mediapipe_gesture == "Pointing_Up":
            return "KUECHE LICHT AN"

        elif mediapipe_gesture == "Victory":
            return "FLUR LICHT AN"

        elif mediapipe_gesture == "Thumb_Up":
            return "ROLLLADEN AUF"

        elif mediapipe_gesture == "Thumb_Down":
            return "ROLLLADEN ZU"

        return ""