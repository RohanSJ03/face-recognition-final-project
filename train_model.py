import cv2
import os
import numpy as np
import pickle

# Paths
dataset_path = "/Users/rohansijujacob/Desktop/attendance_system/dataset"
model_path = "models/face_model.yml"
names_path = "models/names.pkl"
cascade_path = "models/haarcascade_frontalface_default.xml"

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier(cascade_path)

# Initialize variables
faces = []
labels = []
names = {}
label_id = 0

# Process the Rohan folder
rohan_folder = os.path.join(dataset_path, "Rohan")
print(f"Processing folder: {rohan_folder}")

# Map the label to the folder
names[label_id] = "Rohan"

# Iterate through the images
for filename in os.listdir(rohan_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(rohan_folder, filename)
        print(f"Processing image: {image_path}")

        # Load and convert the image to grayscale
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        face_rects = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in face_rects:
            face = gray[y:y+h, x:x+w]
            faces.append(face)
            labels.append(label_id)

print(f"Found {len(faces)} face(s) for training.")

# Train the LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(labels))

# Save the trained model and names mapping
recognizer.save(model_path)
with open(names_path, "wb") as f:
    pickle.dump(names, f)

print(f"Model saved to {model_path}")
print(f"Name mappings saved to {names_path}")
