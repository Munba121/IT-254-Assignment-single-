#define BUTTON_PIN 2
#define LED1 8
#define LED2 9
#define LED3 10
#define BUZZER 5
#define POT_PIN A0


#define TRIG_PIN 7
#define ECHO_PIN 6

int buttonState = 0;
int potValue = 0;
int moodLevel = 0;
int recommendations = 0;

long duration;
int distance;

void setup() {
  Serial.begin(9600);

  pinMode(BUTTON_PIN, INPUT);
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {

  // Read potentiometer (0–1023)
  potValue = analogRead(POT_PIN);

  if (potValue < 341) moodLevel = 0;
  else if (potValue < 682) moodLevel = 1;
  else moodLevel = 2;

  // Ultrasonic sensor
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  // Button
  buttonState = digitalRead(BUTTON_PIN);

  // Trigger scan (button OR object close)
  if (buttonState == HIGH || distance < 15) {
    Serial.print("SCAN:");
    Serial.println(moodLevel);

    tone(BUZZER, 1000, 200);
    delay(1000); // prevent spam
  }

  // Receive result from Python
  if (Serial.available() > 0) {
    recommendations = Serial.parseInt();

    digitalWrite(LED1, LOW);
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);

    if (recommendations >= 1) digitalWrite(LED1, HIGH);
    if (recommendations >= 2) digitalWrite(LED2, HIGH);
    if (recommendations >= 3) digitalWrite(LED3, HIGH);

    tone(BUZZER, 2000, 300);
  }
}
