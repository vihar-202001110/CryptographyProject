import os
import sys
from PIL import Image
from datetime import datetime
from module import Support, AES, DoublePendulum

if len(sys.argv) < 2:
    print(f"Error: Missing Arguements\n[Usage]: {sys.argv[0]} <encrypted_image_name> <key_file_name>")
    exit(1)

DECRYTED_IMAGE_DIR = "Decrypted"
    
encrytedImg = sys.argv[1]  # encryted image
keyFile = sys.argv[2]  # keyFile


if not os.path.isfile(keyFile) or not os.path.isfile(encrytedImg):
    print(f"Error: Invalid Arguements\narg[1] and arg[2] must be existing files")
    exit(1)

if not os.path.isdir(DECRYTED_IMAGE_DIR):
    os.mkdir(DECRYTED_IMAGE_DIR)
    
total_time, total_samples, theta1_initial, angularVelocity_initial_1, theta2_intial, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity = Support.readKey(keyFile)
x1, x2, y1, y2 = DoublePendulum.getCoordinates(total_time, int(total_samples), theta1_initial, angularVelocity_initial_1, theta2_intial, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity)

masterKey = AES.masterKey(x1, x2, y1, y2)

responseBody = {}

# try:   
decryptedBytes = AES.decryptFromImage(encrytedImg, masterKey)
data_type = decryptedBytes[0]

try:
    if data_type == 1: # image
        imageFileName = Support.bytesToImage(decryptedBytes[1:], DECRYTED_IMAGE_DIR)
        responseBody["filepath"] = imageFileName
        responseBody["success"] = True
    elif data_type == 0: # text
        responseBody["data"] = decryptedBytes.__str__()
        responseBody["success"] = True
    else:
        responseBody["message"] = "Something Invalid Happened"
        responseBody["success"] = False
except Exception as eobj:
    print(eobj)
    responseBody["message"] = f"Exeption ocurred with message {eobj}"
    responseBody["success"] = False
    
print(responseBody)

# res = requests.post('http://127.0.0.1:3000/pythonRes', json=responseBody) 