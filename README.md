# easyHome – Smart-Home-Steuerung

easyHome ist ein Schulprojekt zur Steuerung eines Smart Homes mit Handgesten. Eine Kamera erkennt die Gesten mithilfe von MediaPipe. Die erkannten Befehle werden über MQTT an einen simulierten ESP32 in Wokwi gesendet.

Zusätzlich zeigt ein lokales Web-Dashboard den aktuellen Zustand der Lichter, des Rollladens und der Sensoren an.

## Funktionen

- Handgestenerkennung über Kamera und MediaPipe
- Steuerung von Lichtern und Rollladen über MQTT
- ESP32-Simulation in Wokwi
- Messung von Temperatur und Luftfeuchtigkeit mit einem DHT22
- Bewegungserkennung mit einem PIR-Sensor
- Bedienung des Wohnzimmerlichts über einen Taster
- Live-Dashboard im Browser
- Grafische Anzeige des erkannten Handskeletts

## Verwendete Komponenten

### Hardware in Wokwi

- ESP32 DevKit
- LED mit Vorwiderstand
- DHT22 Temperatur- und Luftfeuchtigkeitssensor
- PIR-Bewegungssensor
- Servo für den Rollladen
- Taster

### Software

- Python
- OpenCV
- MediaPipe
- Paho MQTT
- HTML, CSS und JavaScript
- Arduino / ESP32
- Wokwi
- öffentlicher MQTT-Broker `test.mosquitto.org`

## Gestensteuerung

| Geste | Aktion |
|---|---|
| Offene Hand | Wohnzimmerlicht einschalten |
| Zeigefinger nach oben | Küchenlicht einschalten |
| Victory-Zeichen | Flurlicht einschalten |
| Geschlossene Faust | Alle Lichter ausschalten |
| Daumen nach oben | Rollladen öffnen |
| Daumen nach unten | Rollladen schließen |

Eine Geste muss mehrere Kamerabilder lang erkannt werden, bevor ein Befehl gesendet wird. Dadurch werden versehentliche Aktionen reduziert.

## Projektaufbau

| Datei | Aufgabe |
|---|---|
| `main.py` | Startet die Handsteuerung |
| `hand_tracker.py` | Verarbeitet das Kamerabild und erkennt Handgesten |
| `gesture_detector.py` | Übersetzt MediaPipe-Gesten in Smart-Home-Befehle |
| `mqtt_client.py` | Sendet die Befehle über MQTT |
| `dashboard.py` | Startet das Dashboard und empfängt MQTT-Statuswerte |
| `dashboard.html` | Benutzeroberfläche des Web-Dashboards |
| `sketch.ino` | Programm für den simulierten ESP32 |
| `diagram.json` | Schaltung der Wokwi-Simulation |
| `gesture_recognizer.task` | MediaPipe-Modell zur Gestenerkennung |
| `libraries.txt` | Bibliotheken für die Wokwi-Simulation |

## Installation

Benötigt werden Python und eine angeschlossene beziehungsweise eingebaute Kamera. Die notwendigen Python-Bibliotheken können im Projektordner installiert werden:

```powershell
pip install opencv-python mediapipe paho-mqtt
```

## Projekt starten

1. Die [easyHome-Simulation auf Wokwi](https://wokwi.com/projects/467185188314510337) öffnen und starten.
2. Sicherstellen, dass die Kamera nicht von einem anderen Programm verwendet wird.
3. Im Projektordner folgenden Befehl ausführen:

```powershell
python main.py
```

Danach öffnen sich die Kameraansicht und das Web-Dashboard. Das Dashboard ist normalerweise unter [http://127.0.0.1:8080](http://127.0.0.1:8080) erreichbar.

Die Handsteuerung wird mit der Taste `Q` beendet.

## Ablauf

1. OpenCV liest das Bild der Kamera ein.
2. MediaPipe erkennt die Hand und die ausgeführte Geste.
3. Die Geste wird in einen Smart-Home-Befehl übersetzt.
4. Python veröffentlicht den Befehl über MQTT.
5. Der ESP32 empfängt den Befehl und steuert die entsprechende Komponente.
6. Sensor- und Statuswerte werden über MQTT an das Dashboard übertragen.

## Hinweise

- Für Wokwi und MQTT wird eine Internetverbindung benötigt.
- Da ein öffentlicher Test-Broker verwendet wird, dürfen keine vertraulichen Daten übertragen werden.
- In der aktuellen Wokwi-Schaltung ist nur das Wohnzimmerlicht als echte LED umgesetzt. Küche und Flur werden im Dashboard dargestellt, besitzen aber noch keine eigenen LEDs.
- Falls die Kamera nicht geöffnet werden kann, sollten die Kameraberechtigungen und andere geöffnete Kamera-Anwendungen geprüft werden.

## Autor

Schulprojekt im Bereich IT und Smart Home.
