#include <ESP32Servo.h>
#include <DHTesp.h>
#include <WiFi.h>
#include <PubSubClient.h>

// =====================================================
// WLAN + MQTT
// =====================================================

const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* mqtt_server = "test.mosquitto.org";

WiFiClient espClient;
PubSubClient client(espClient);

// =====================================================
// PIN-BELEGUNG, ESP 32
// =====================================================

// LED
const int LED_PIN = 2;

// PIR-Bewegungsmelder
const int PIR_PIN = 5;

// Taster
const int BUTTON_PIN = 13;

// DHT22 Temperatur- und Luftfeuchtigkeitssensor
const int DHT_PIN = 16;

// Servo (Rollo)
const int SERVO_PIN = 18;

// =====================================================
// OBJEKTE ERSTELLEN
// =====================================================

Servo rollo;
DHTesp dht;

// =====================================================
// VARIABLEN
// =====================================================

// LED Status speichern
bool ledStatus = false;

// PIR Status speichern
bool letzteBewegung = false;

// Rollo Status speichern
String rolloStatus = "Offen";

// Zeitsteuerung für DHT22
unsigned long letzteMessung = 0;
const unsigned long messIntervall = 5000;

// =====================================================
// WLAN VERBINDEN
// =====================================================

void setupWifi() {

  Serial.println("Verbinde WLAN...");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WLAN verbunden!");
}

// =====================================================
// MQTT VERBINDEN
// =====================================================

void reconnectMQTT() {

  while (!client.connected()) {

    Serial.println("Verbinde MQTT...");

    if (client.connect("easyHomeESP32")) {

      Serial.println("MQTT verbunden!");

  client.subscribe("easyHome/Wohnung/Wohnzimmer/Licht");

  client.subscribe("easyHome/Wohnung/Wohnzimmer/Rollo");

      // Anfangswerte senden
  client.publish(
    "easyHome/Wohnung/Wohnzimmer/Licht",
    "Wohnzimmerlicht AUS"
  );

  client.publish(
    "easyHome/Wohnung/Flur/Bewegung",
    "Keine Bewegung"
  );


    } else {

      Serial.print("MQTT Fehler: ");
      Serial.println(client.state());

      delay(2000);
    }
  }
}
// =====================================================
// MQTT CALLBACK
// =====================================================

void callback(char* topic, byte* payload, unsigned int length) {

  String nachricht = "";

  for (int i = 0; i < length; i++) {
    nachricht += (char)payload[i];
  }

  Serial.print("Nachricht empfangen: ");
  Serial.println(nachricht);

  if (String(topic) == "easyHome/Wohnung/Wohnzimmer/Licht") {

    if (nachricht == "Ein") {
      digitalWrite(LED_PIN, HIGH);
      ledStatus = true;
    }

    else if (nachricht == "Aus") {
      digitalWrite(LED_PIN, LOW);
      ledStatus = false;
    }
  }

if (String(topic) == "easyHome/Wohnung/Wohnzimmer/Rollo") {

  if (nachricht == "Offen") {

    rollo.write(180);
    rolloStatus = "Offen";

    Serial.println("Rollo geöffnet");

  }

  else if (nachricht == "Geschlossen") {

    rollo.write(0);
    rolloStatus = "Geschlossen";

    Serial.println("Rollo geschlossen");

  }
}

}

// =====================================================
// SETUP
// =====================================================

void setup() {

  Serial.begin(115200);

  setupWifi();

  client.setServer(mqtt_server, 1883);

  client.setCallback(callback);

  // ---------- LED ----------
  pinMode(LED_PIN, OUTPUT);

  // ---------- PIR ----------
  pinMode(PIR_PIN, INPUT);

  // ---------- TASTER ----------
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // ---------- DHT22 ----------
  dht.setup(DHT_PIN, DHTesp::DHT22);

  // ---------- SERVO ----------
  rollo.attach(SERVO_PIN);

  // Rollo startet vollständig geöffnet
  rollo.write(180);

  Serial.println("Smart Home System gestartet");
}

// =====================================================
// LOOP
// =====================================================

void loop() {

  // MQTT Verbindung prüfen
  if (!client.connected()) {
    reconnectMQTT();
  }

  client.loop();

  // =====================================================
  // TASTER + LED/Licht
  // =====================================================

  if (digitalRead(BUTTON_PIN) == LOW) {

    ledStatus = !ledStatus;

    digitalWrite(LED_PIN, ledStatus);

    Serial.println("Wohnzimmerlichtschalter betätigt");

    if (ledStatus) {

      client.publish(
        "easyHome/Wohnung/Wohnzimmer/Licht",
        "Ein"
      );

      Serial.println("Wohnzimmerlicht: EIN");

    } else {

      client.publish(
        "easyHome/Wohnung/Wohnzimmer/Licht",
        "Aus"
      );

      Serial.println("Wohnzimmerlicht: AUS");
    }

    delay(250);
  }

  // =====================================================
  // PIR SENSOR/ Bewegungsmelder
  // =====================================================

  bool aktuelleBewegung = digitalRead(PIR_PIN);

  if (aktuelleBewegung != letzteBewegung) {

  if (aktuelleBewegung) {

    Serial.println("Bewegung im Flur erkannt");

    client.publish(
      "easyHome/Wohnung/Flur/Bewegung",
      "Bewegung erkannt"
    );

  } else {

    Serial.println("Keine Bewegung im Flur");

    client.publish(
      "easyHome/Wohnung/Flur/Bewegung",
      "Keine Bewegung"
    );
  }

  letzteBewegung = aktuelleBewegung;
}

  // =====================================================
  // DHT22 SENSOR/ Temperatursensor/ Luftfeuchtigkeitsensor
  // =====================================================

  if (millis() - letzteMessung >= messIntervall) {

    TempAndHumidity data = dht.getTempAndHumidity();

    Serial.print("Temperatur: ");
    Serial.print(data.temperature);
    Serial.println(" °C");

    Serial.print("Luftfeuchtigkeit: ");
    Serial.print(data.humidity);
    Serial.println(" %");

    Serial.println("--------------------------");
  // MQTT Temperatur senden
String temperatur = String(data.temperature);

client.publish(
  "easyHome/Wohnung/Flur/Temperatur",
  temperatur.c_str()
);

// MQTT Luftfeuchtigkeit senden
String luftfeuchtigkeit = String(data.humidity);

client.publish(
  "easyHome/Wohnung/Flur/Luftfeuchtigkeit",
  luftfeuchtigkeit.c_str()
);
    letzteMessung = millis();
  }
}
