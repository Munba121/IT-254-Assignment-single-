# IT-254-Assignment-single-
This project is an interactive book recommendation system that integrates an Arduino-based hardware setup with a computer vision and machine learning program on a laptop. The Arduino uses a potentiometer to capture the user’s mood (low, medium, or high) and a button to trigger a scan. When activated, it sends this mood data to the laptop through serial communication and provides audio feedback using a buzzer.

On the software side, a Python program uses the laptop camera along with OpenCV and a TensorFlow Lite model to identify the book shown in front of the camera. Based on the detected book and the user’s mood, the program generates a list of recommended books. It then sends the number of recommendations back to the Arduino, which displays the result using LEDs and a buzzer for visual and audio feedback.

Overall, the project demonstrates how hardware input and machine learning can work together to create a responsive, real-time recommendation system. My Part in my groups project was maaking the circuit and the arduino code.

Arduino code:
Arduino
#define BUTTON_PIN 2
#define LED1 8
#define LED2 9
#define LED3 10
#define BUZZER 5
#define POT_PIN A0

int buttonState = 0;
int potValue = 0;
int moodLevel = 0;
int recommendations = 0;

void setup() {
  Serial.begin(9600);

  pinMode(BUTTON_PIN, INPUT);   // change to INPUT_PULLUP if needed
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(BUZZER, OUTPUT);
}

void loop() {

  // Read potentiometer → mood
  potValue = analogRead(POT_PIN);

  if (potValue < 341) moodLevel = 0;
  else if (potValue < 682) moodLevel = 1;
  else moodLevel = 2;

  // Read button
  buttonState = digitalRead(BUTTON_PIN);

  // Send scan request
  if (buttonState == HIGH) {
    Serial.print("SCAN:");
    Serial.println(moodLevel);

    tone(BUZZER, 1000, 200);
    delay(1000); // prevent spam
  }

  // Receive result from Python
  if (Serial.available() > 0) {
    recommendations = Serial.parseInt();

    // Turn off all LEDs
    digitalWrite(LED1, LOW);
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);

    // Turn on based on number
    if (recommendations >= 1) digitalWrite(LED1, HIGH);
    if (recommendations >= 2) digitalWrite(LED2, HIGH);
    if (recommendations >= 3) digitalWrite(LED3, HIGH);

    tone(BUZZER, 2000, 300);
  }
}


Python Code:
import cv2
import numpy as np
import tensorflow as tf
import serial
import time

print("Starting program...")

# -----------------------------
# Connect to Arduino
# -----------------------------
try:
    arduino = serial.Serial('COM3', 9600)  # CHANGE if needed
    time.sleep(2)
    print("Arduino connected")
except Exception as e:
    print("ERROR connecting to Arduino:", e)
    exit()

# -----------------------------
# Load TFLite Model
# -----------------------------
try:
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    print("Model loaded successfully")
except Exception as e:
    print("ERROR loading model:", e)
    exit()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

labels = ["Hunger Games", "Percy Jackson"]

# -----------------------------
# Open Camera
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera failed")
    exit()

print("Camera ready")

# -----------------------------
# Prediction Function
# -----------------------------
def predict_book(frame):
    img = cv2.resize(frame, (224, 224))
    img = np.expand_dims(img, axis=0).astype(np.float32)

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])
    index = np.argmax(output)

    print("Raw prediction:", output)

    return labels[index]

# -----------------------------
# Recommendation Logic
# -----------------------------
def recommend(book, mood):

    if book == "Hunger Games":
        if mood == 0:
            return ["Percy Jackson"]
        elif mood == 1:
            return ["Narnia"]
        else:
            return ["Maze Runner"]

    elif book == "Percy Jackson":
        if mood == 0:
            return ["Harry Potter"]
        elif mood == 1:
            return ["Narnia"]
        else:
            return ["Hunger Games"]

    return ["None"]

# -----------------------------
# MAIN LOOP
# -----------------------------
print("Waiting for Arduino...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("Camera", frame)

    # Read from Arduino
    if arduino.in_waiting > 0:
        data = arduino.readline().decode().strip()
        print("Arduino:", data)

        if data.startswith("SCAN"):
            mood = int(data.split(":")[1])

            print("Scanning... Mood:", mood)

            book = predict_book(frame)
            print("Detected:", book)

            results = recommend(book, mood)
            print("Recommendations:", results)

            # Send number back
            arduino.write((str(len(results)) + "\n").encode())

    if cv2.waitKey(1) == ord('q'):
        print("Quitting...")
        break

# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
arduino.close()
print("Program ended")
