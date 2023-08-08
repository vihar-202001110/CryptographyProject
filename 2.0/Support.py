
import random
from datetime import datetime
from math import pi
from PIL import Image
import struct


def __addPadding(data: bytes, block_size: int) -> bytes:
    return data + b"\x00" * (block_size - len(data) % block_size)


def __removePadding(data: bytes) -> bytes:
    return data.rstrip(b"\x00")


def generateInitialConditions() -> tuple[float, float, float, float, float, float, float, float, float, float, float]:
    """randomly generates and returns total_time, theta1_initial, theta2_intial, angularVelocity_initial_1, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity

    Returns:
        tuple[int,float, float, float, float, float, float, float, float, float]: 
            total_time, theta1_initial, theta2_intial, angularVelocity_initial_1, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity
    """
    random.seed(datetime.now().timestamp())
    total_time = random.randint(40, 100)                                # range - 40 to 100
    total_samples = random.randint(20, 500)                             # range - 20 to 500
    theta1_initial = (random.random() * 2 * pi) - pi	                # range - -pi to pi
    theta2_initial = (random.random() * 2 * pi) - pi   	                # range - -pi to pi
    angularVelocity_initial_1 = (random.random() * 10 * pi) - (5 * pi)  # range - -5pi to 5pi
    angularVelocity_initial_2 = (random.random() * 10 * pi) - (5 * pi)  # range - -5pi to 5pi
    mass1 = (random.random() * 9) + 1                                   # range - [1,10)
    mass2 = (random.random() * 9) + 1                                   # range - [1,10)
    length_1 = (random.random() * 3) + 1                                # range - [1,4)
    length_2 = (random.random() * 3) + 1                                # range - [1,4)
    gravity = (random.random() * 2) + 8                                 # range - [8,10)
    return total_time, total_samples, theta1_initial, theta2_initial, angularVelocity_initial_1, angularVelocity_initial_2, mass1, mass2, length_1, length_2, gravity


def sizeToByte(size: tuple[int, int]) -> bytes:
    """Returns 4 bytes containing the dimensions provided

    Args:
        size (tuple[int, int]): size to convert to bytes

    Returns:
        bytes: height appended with width in bytes (total 4 bytes)
    """
    height, width = size
    height1, height2 = height // 256, height % 256
    width1, width2 = width // 256, width % 256
    return bytes([height1, height2, width1, width2])


def byteToSize(size: bytes) -> tuple[int, int]:
    height1, height2, width1, width2 = size
    height = height1 * 256 + height2
    width = width1 * 256 + width2
    return height, width


def imageToBytes(filepath: str) -> bytes:
    """converts image to bytes sequence

    Args:
        filepath (str): path of the image to convert

    Returns:
        bytes: image bytes prepended image extension (6 bytes) prepended with image mode (8 Bytes) prepended with image size (4 bytes)
    """
    img = Image.open(filepath)
    ext = __addPadding(bytes(filepath.rsplit('.', 1)[-1], 'utf-8'), 6)
    size = sizeToByte(img.size)
    mode = __addPadding(bytes(img.mode, 'utf-8'), 8)
    
    return size + mode + ext + img.tobytes()


def bytesToImage(imgData: bytes) -> tuple[Image.Image, str]:
    """converts the given byte data to image by splitting it into mode, size, extension and image data

    Args:
        imgData (bytes): bytes containing size, mode, extension and data
        imageDir (str): directory path to store the  image in

    Returns:
        str : returns the image object with its extension
    """
    size, mode, ext, img_bytes = imgData[0:4], imgData[4:12], imgData[12:18], imgData[18:]

    size = byteToSize(size)
    mode = str(__removePadding(mode), "utf-8")
    ext = str(__removePadding(ext), "utf-8")
    
    img = Image.frombytes(mode=mode, size=size, data=img_bytes)
    return img, ext


# total_time: float = 40
# total_samples=1001
# theta1_initial=1
# angularVelocity_initial_1=-3
# theta2_intial=-1
# angularVelocity_initial_2=5
# mass1=2
# mass2=1
# length_1=2
# length_2=1
# gravity=9.81

def writeKey(keyFileName, total_time, total_samples, theta1_intial, angularVelocity_initial_1, theta2_intial, angularVelocity_initial_2, mass1, mass2, length1, length2, gravity):
    lines = list(map( str, [
            total_time, total_samples, theta1_intial, angularVelocity_initial_1, 
            theta2_intial, angularVelocity_initial_2, mass1, mass2, length1, length2, gravity
        ] ))
    with open(keyFileName, "w") as keyFile:
        keyFile.write("\n".join(lines))
        keyFile.close()


def readKey(keyFileName: str):
    with open(keyFileName, "r") as keyFile:
        return list( map(float, keyFile.readlines()) )


if __name__ == "__main__":
    # print(generateInitialConditions())
    # print(byteToSize(sizeToByte([252, 842])))
    
    total_time, theta1_initial, theta2_intial, angularVelocity_initial_1, angular_velocity_initial_2, mass1, mass2, length_1, length_2, gravity = generateInitialConditions()
    writeKey()
