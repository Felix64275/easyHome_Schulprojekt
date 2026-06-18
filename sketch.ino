#include <ESP32Servo.h>
#include <DHTesp.h>

// =====================================================
// PIN-BELEGUNG
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

// Zeitsteuerung für DHT22
unsigned long letzteMessung = 0;
const unsigned long messIntervall = 5000;


// =====================================================
// SETUP
// Wird einmal beim Start ausgeführt
// =====================================================

void setup() {

  Serial.begin(115200);

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
// Läuft dauerhaft
// =====================================================

void loop() {

  // =====================================================
  // TASTER + LED
  // =====================================================

  if (digitalRead(BUTTON_PIN) == LOW) {

    ledStatus = !ledStatus;

    digitalWrite(LED_PIN, ledStatus);

    Serial.println("Taster gedrueckt");

    delay(250);   // Entprellen des Tasters
  }


  // =====================================================
  // PIR SENSOR
  // Nur bei Zustandsänderung melden
  // =====================================================

 bool aktuelleBewegung = digitalRead(PIR_PIN);

if (aktuelleBewegung != letzteBewegung) {

  if (aktuelleBewegung) {
    Serial.println("Bewegung erkannt!");
  } else {
    Serial.println("Keine Bewegung mehr");
  }

  letzteBewegung = aktuelleBewegung;
}


  // =====================================================
  // DHT22 SENSOR
  // Nur alle 2 Sekunden messen
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

    letzteMessung = millis();
  }


  // =====================================================
  // SERVO / ROLLO
  // Aktuell auf 180° fest eingestellt
  // MQTT-Steuerung folgt später
  // =====================================================

}