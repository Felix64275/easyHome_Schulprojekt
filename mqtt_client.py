import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883

TOPIC_WOHNZIMMER = "easyHome/Wohnung/Wohnzimmer/Licht"
TOPIC_KUECHE = "easyHome/Wohnung/Kueche/Licht"
TOPIC_FLUR = "easyHome/Wohnung/Flur/Licht"
TOPIC_ROLLO = "easyHome/Wohnung/Wohnzimmer/Rollo"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.connect(BROKER, PORT)
client.loop_start()


def send_gesture(gesture):

    if gesture == "WOHNZIMMER LICHT AN":
        client.publish(TOPIC_WOHNZIMMER, "Ein")
        print("MQTT: Wohnzimmer Licht AN")

    elif gesture == "KUECHE LICHT AN":
        client.publish(TOPIC_KUECHE, "Ein")
        print("MQTT: Kueche Licht AN")

    elif gesture == "FLUR LICHT AN":
        client.publish(TOPIC_FLUR, "Ein")
        print("MQTT: Flur Licht AN")

    elif gesture == "ALLE LICHTER AUS":
        client.publish(TOPIC_WOHNZIMMER, "Aus")
        client.publish(TOPIC_KUECHE, "Aus")
        client.publish(TOPIC_FLUR, "Aus")
        print("MQTT: Alle Lichter AUS")

    elif gesture == "ROLLLADEN AUF":
        client.publish(TOPIC_ROLLO, "Offen")
        print("MQTT: Rollladen AUF")

    elif gesture == "ROLLLADEN ZU":
        client.publish(TOPIC_ROLLO, "Geschlossen")
        print("MQTT: Rollladen ZU")