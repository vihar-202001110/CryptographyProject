import json
import sys
import os
import requests
from datetime import datetime
from module import AES, DoublePendulum, Support


if len(sys.argv) < 2:
    print(f"Error: Missing Arguements\n[Usage]: {sys.argv[0]} <data_value> <data_type>")
    exit(1)
    
data_value = sys.argv[1]  # data to encrypt as text
data_type = sys.argv[2]  # data type image/text

if data_type == "image" and not os.path.isfile(data_value):
    print(f"Error: Invalid Arguements\nArg[1] must be a image file for Arg[2] = 'image'")
    exit(1)


ENCRYTED_IMAGE_DIR = "Encrypted"
KEY_DIR = "Keys"
if not os.path.isdir(ENCRYTED_IMAGE_DIR):
    os.mkdir(ENCRYTED_IMAGE_DIR)
if not os.path.isdir(KEY_DIR):
    os.mkdir(KEY_DIR)


keyFileName = f"./{KEY_DIR}/key_{datetime.now().timestamp()}"

total_time, total_samples, theta1_initial, theta2_intial, angularVelocity_initial_1, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity = Support.generateInitialConditions()
Support.writeKey(keyFileName, total_time, total_samples, theta1_initial,  angularVelocity_initial_1, theta2_intial, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity)

x1, x2, y1, y2 = DoublePendulum.getCoordinates(total_time, total_samples, theta1_initial,  angularVelocity_initial_1, theta2_intial, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity)


masterKey = AES.masterKey(x1, x2, y1, y2)

try:
    if data_type == "text":
        byteData = bytes([0]) + bytes(data_value, "utf-8")  # 0 to indicate type text
        filename = ""
    else:
        byteData = bytes([1]) + Support.imageToBytes(data_value)
        filename = data_value.rsplit(".", 1)[0].rsplit("/", 1)[-1]  # 1 to indicate type image and -1 to choose just the filename and not its path
    
    filename = f"./{ENCRYTED_IMAGE_DIR}/{filename}-{datetime.now().timestamp()}.png"
    AES.encryptToImage(byteData, masterKey, filename)
    
    responseBody = {
        "success": True,
        "filepath": filename,
        "key": keyFileName
    }
except Exception as eobj:
        print(eobj)
        responseBody = {
            "success": False
        }


print(responseBody)
# Output the dictionary as a JSON string
# res = requests.post('http://127.0.0.1:3000/pythonRes', json=responseBody) 
# print(json.dumps(data))
