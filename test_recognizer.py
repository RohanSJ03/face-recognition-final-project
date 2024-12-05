import requests

url = "http://127.0.0.1:5000/real_time_recognition"
image_path = "/Users/rohansijujacob/Desktop/attendance_system/dataset/Rohan/image1.jpg"
with open(image_path, "rb") as f:
    response = requests.post(url, files={"image": f})

print(response.json())
