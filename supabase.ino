#include <WiFiS3.h>
#include "WiFiSSLClient.h"
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>
#include <MatrixMiniR4.h>

const char ssid[] = "matrix";
const char pass[] = "matrix2024";

String serverAddress = "lweqgypqengrrymrkgao.supabase.co";  // Without "https://"
String key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx3ZXFneXBxZW5ncnJ5bXJrZ2FvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIzMDkzOTEsImV4cCI6MjA0Nzg4NTM5MX0.VIFgwdupjFDFi6bwu72VIX0PrcaY0WtCq_iDyy504PU";

int port = 443;
String path = "/rest/v1/sensor_data";  // Path to the table in supabase

WiFiSSLClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, port);

float voltage = 0.0;     // Read the Voltage of Matrix Mini R4
float percentage = 0.0;  // Battery percentage
float obstacle_distance = 0.0;

// Timing variables
unsigned long previousWiFiMillis = 0;
unsigned long wifiInterval = 3000;  // Send data every 3 seconds

void setup() {
  MiniR4.begin();
  Serial.begin(115200);
  MiniR4.PWR.setBattCell(2);  // 18650x2

  MiniR4.I2C1.MXLaser.begin();
  MiniR4.M1.setReverse(true);
  MiniR4.M2.setReverse(false);
  delay(100);

  printToOLED("Starting..");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    printToOLED("Connecting to wifi..");
    Serial.print(".");
    delay(500);
  }
  Serial.print("Connected to network.");
  printToOLED("Connected to network.");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    send_to_supabase();
  }
  autonomous_driving();
}

void send_to_supabase() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousWiFiMillis >= wifiInterval) {
    previousWiFiMillis = currentMillis;
    voltage = MiniR4.PWR.getBattVoltage();        // Read the Voltage of Matrix Mini R4
    percentage = MiniR4.PWR.getBattPercentage();  // Battery percentage

    MiniR4.OLED.clearDisplay();
    MiniR4.OLED.setCursor(5, 5);
    MiniR4.OLED.print("Vol:" + String(voltage) + "V");
    MiniR4.OLED.setCursor(5, 20);
    MiniR4.OLED.print("Per:" + String(percentage) + "%");
    MiniR4.OLED.display();

    StaticJsonDocument<200> doc;
    doc["voltage"] = voltage;
    doc["percentage"] = percentage;
    doc["distance"] = obstacle_distance;

    String output;
    serializeJson(doc, output);
    client.beginRequest();
    client.post(path);
    client.sendHeader("Content-Type", "application/json");
    client.sendHeader("apikey", key);  // Autorización
    client.sendHeader("Content-Length", output.length());
    client.beginBody();
    client.print(output);
    client.endRequest();
    int statusCode = client.responseStatusCode();

    if (statusCode == 201) {
      Serial.println("Data sent successfully!");
      MiniR4.LED.setColor(1, 0, 0, 255);  // Blue
      MiniR4.LED.setColor(2, 0, 0, 255);  // Blue
    } else {
      MiniR4.LED.setColor(1, 255, 0, 0);  // Red
      Serial.print("Error sending data. Status code: ");
      Serial.println(statusCode);
    }
    client.stop();
  }
}

void autonomous_driving() {
  // 100mm is equal
  // to 10cm
  if (MiniR4.I2C1.MXLaser.getDistance() > 100) {
    obstacle_distance = MiniR4.I2C1.MXLaser.getDistance();
    MiniR4.OLED.setCursor(10, 10);
    MiniR4.OLED.print(obstacle_distance);
    MiniR4.OLED.display();
    MiniR4.M1.setSpeed(3);
    MiniR4.M2.setSpeed(3);
    delay(250);
    MiniR4.OLED.clearDisplay();
  } else {
    reverseTone();
    // Left wheel rotate anticlockwise
    MiniR4.M1.setSpeed((-3));
    MiniR4.M2.setSpeed(0);
    delay(500);
  }
}

void printToOLED(String text) {
  MiniR4.OLED.clearDisplay();
  MiniR4.OLED.setTextSize(1);
  MiniR4.OLED.setCursor(5, 5);
  MiniR4.OLED.print(text);
  MiniR4.OLED.display();
}

void reverseTone() {
  int frequency = 1000;  // Adjust the frequency as needed (e.g., 800-1200 Hz)
  int duration = 100;    // Tone duration in milliseconds
  int pause = 100;       // Pause between tones

  MiniR4.LED.setColor(1, 255, 0, 0); 
  MiniR4.LED.setColor(2, 255, 0, 0);
  // Play the first reverse tone
  MiniR4.Buzzer.Tone(frequency, duration);
  delay(duration);  // Ensure the tone completes

  MiniR4.LED.setColor(2, 255, 165, 0);
  MiniR4.LED.setColor(2, 255, 165, 0);
  // Short pause between tones
  delay(pause);

  MiniR4.LED.setColor(1, 255, 0, 0);
  MiniR4.LED.setColor(2, 255, 0, 0);
  // Play the second reverse tone
  MiniR4.Buzzer.Tone(frequency, duration);
  delay(duration);  // Ensure the tone completes
}