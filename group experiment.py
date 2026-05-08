# Group Experiment
import cv2
import numpy as np
import tensorflow as tf
import time


print("Starting program...")


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


# Labels (must match your model exactly)
labels = ["Hunger Games", "Percy Jackson"]


# -----------------------------
# Open Camera
# -----------------------------
print("Opening camera...")
cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print("ERROR: Camera did not open")
    exit()


print("Camera opened successfully")


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
mood = 1  # simulate Arduino input


print("Press SPACE to scan, Q to quit")


while True:
    ret, frame = cap.read()


    if not ret:
        print("ERROR: Failed to grab frame")
        break


    cv2.imshow("Camera", frame)


    key = cv2.waitKey(1)


    # SPACE = scan
    if key == ord(' '):
        print("Scanning... Mood:", mood)


        book = predict_book(frame)
        print("Detected:", book)


        results = recommend(book, mood)
        print("Recommendations:", results)


        time.sleep(1)


    # Q = quit
    elif key == ord('q'):
        print("Quitting...")
        break


# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
print("Program ended")