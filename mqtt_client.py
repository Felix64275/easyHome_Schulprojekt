import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883

TOPIC_LIGHT = "easyHome/Wohnung/Wohnzimmer/Licht"
TOPIC_ROLLO = "easyHome/Wohnung/Wohnzimmer/Rollo"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
client.loop_start()


def send_gesture(gesture):
    if gesture == "LICHT AN":
        client.publish(TOPIC_LIGHT, "Ein")
        print("MQTT: Licht AN")

    elif gesture == "LICHT AUS":
        client.publish(TOPIC_LIGHT, "Aus")
        print("MQTT: Licht AUS")

    elif gesture == "ROLLLADEN AUF":
        client.publish(TOPIC_ROLLO, "Offen")
        print("MQTT: Rollladen AUF")

    elif gesture == "ROLLLADEN ZU":
        client.publish(TOPIC_ROLLO, "Geschlossen")
        print("MQTT: Rollladen ZU")