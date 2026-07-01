import json
import threading
import webbrowser

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import paho.mqtt.client as mqtt


BROKER = "test.mosquitto.org"
PORT = 1883
WEB_ADDRESS = "127.0.0.1"
WEB_PORT = 8080

TOPIC_WOHNZIMMER = "easyHome/Wohnung/Wohnzimmer/Licht"
TOPIC_KUECHE = "easyHome/Wohnung/Kueche/Licht"
TOPIC_FLUR = "easyHome/Wohnung/Flur/Licht"
TOPIC_ROLLO = "easyHome/Wohnung/Wohnzimmer/Rollo"
TOPIC_TEMP = "easyHome/Wohnung/Flur/Temperatur"
TOPIC_LUFT = "easyHome/Wohnung/Flur/Luftfeuchtigkeit"
TOPIC_BEWEGUNG = "easyHome/Wohnung/Flur/Bewegung"


class Dashboard:

    def __init__(self):
        self.lock = threading.Lock()

        self.status = {
            "mqtt": "GETRENNT",
            "wohnzimmer": "AUS",
            "kueche": "AUS",
            "flur": "AUS",
            "rollo": "OFFEN",
            "temperatur": "--",
            "luft": "--",
            "bewegung": "Keine Bewegung",
            "geste": "-",
            "mediapipe": "-",
            "letzte_aktion": "-"
        }

        self.server = None
        self.server_thread = None

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.start_webserver()
        self.connect_mqtt()

    def connect_mqtt(self):
        try:
            self.client.connect(BROKER, PORT)
            self.client.loop_start()
        except Exception as error:
            print(f"MQTT-Verbindung fehlgeschlagen: {error}")

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties
    ):
        with self.lock:
            if reason_code == 0:
                self.status["mqtt"] = "VERBUNDEN"
            else:
                self.status["mqtt"] = "GETRENNT"
                return

        topics = [
            TOPIC_WOHNZIMMER,
            TOPIC_KUECHE,
            TOPIC_FLUR,
            TOPIC_ROLLO,
            TOPIC_TEMP,
            TOPIC_LUFT,
            TOPIC_BEWEGUNG
        ]

        for topic in topics:
            client.subscribe(topic)

    def on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties
    ):
        with self.lock:
            self.status["mqtt"] = "GETRENNT"

    def on_message(self, client, userdata, message):
        value = message.payload.decode(
            "utf-8",
            errors="replace"
        )

        with self.lock:
            if message.topic == TOPIC_WOHNZIMMER:
                self.status["wohnzimmer"] = value.upper()

            elif message.topic == TOPIC_KUECHE:
                self.status["kueche"] = value.upper()

            elif message.topic == TOPIC_FLUR:
                self.status["flur"] = value.upper()

            elif message.topic == TOPIC_ROLLO:
                self.status["rollo"] = value.upper()

            elif message.topic == TOPIC_TEMP:
                self.status["temperatur"] = value

            elif message.topic == TOPIC_LUFT:
                self.status["luft"] = value

            elif message.topic == TOPIC_BEWEGUNG:
                self.status["bewegung"] = value

    def update_gesture(self, gesture, mediapipe_gesture):
        with self.lock:
            self.status["geste"] = gesture if gesture else "-"
            self.status["mediapipe"] = (
                mediapipe_gesture
                if mediapipe_gesture
                else "-"
            )

    def set_last_action(self, action):
        with self.lock:
            self.status["letzte_aktion"] = action

    def get_status(self):
        with self.lock:
            return self.status.copy()

    def start_webserver(self):
        dashboard = self
        html_path = Path(__file__).with_name(
            "dashboard.html"
        )

        class DashboardHandler(BaseHTTPRequestHandler):

            def do_GET(self):
                if self.path in ["/", "/index.html"]:
                    try:
                        content = html_path.read_bytes()

                        self.send_response(200)
                        self.send_header(
                            "Content-Type",
                            "text/html; charset=utf-8"
                        )
                        self.send_header(
                            "Content-Length",
                            str(len(content))
                        )
                        self.end_headers()
                        self.wfile.write(content)

                    except FileNotFoundError:
                        self.send_error(
                            404,
                            "dashboard.html wurde nicht gefunden"
                        )

                elif self.path == "/api/status":
                    content = json.dumps(
                        dashboard.get_status(),
                        ensure_ascii=False
                    ).encode("utf-8")

                    self.send_response(200)
                    self.send_header(
                        "Content-Type",
                        "application/json; charset=utf-8"
                    )
                    self.send_header(
                        "Cache-Control",
                        "no-store"
                    )
                    self.send_header(
                        "Content-Length",
                        str(len(content))
                    )
                    self.end_headers()
                    self.wfile.write(content)

                else:
                    self.send_error(404)

            def log_message(self, format, *args):
                return

        try:
            self.server = ThreadingHTTPServer(
                (WEB_ADDRESS, WEB_PORT),
                DashboardHandler
            )

            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True
            )

            self.server_thread.start()

            url = f"http://{WEB_ADDRESS}:{WEB_PORT}"

            print(f"Web-Dashboard: {url}")

            threading.Timer(
                1.0,
                lambda: webbrowser.open(url)
            ).start()

        except OSError as error:
            print(
                f"Webserver konnte nicht gestartet werden: "
                f"{error}"
            )

    def close(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass

        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()