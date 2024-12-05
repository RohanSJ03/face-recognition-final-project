import os
import pickle

model_path = 'models/face_model.yml'
names_path = 'models/names.pkl'

if os.path.exists(model_path) and os.path.exists(names_path):
    print("Model and name mappings are present.")
    with open(names_path, "rb") as f:
        known_names = pickle.load(f)
    print(f"Known names: {known_names}")
else:
    print("Model or name mappings are missing. Retrain the model.")
