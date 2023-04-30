"""
AES master key generation along with encryption and decryption
"""
from Crypto.Cipher import AES
from PIL import Image, UnidentifiedImageError
from math import sqrt, floor

class InsufficientSamplesException(Exception):
    """Custom Exception that can be called when the samples of provided variable are not enough to perform the required task

    Args:
        Exception (class): Extends the Exception class
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def __addPadding(data: bytes, block_size: int) -> bytes:
    return data + b"\x00" * (block_size - len(data) % block_size)


def __removePadding(data: bytes) -> bytes:
    return data.rstrip(b"\x00")


def __toBinary(val: float) -> bytes:
    if val <= -8 or val >= 8:
        raise ValueError("floating value must be  in range (-8, 8)")

    # converting the range to (0, 16) from (-8, 8)
    val += 8

    integer = int(val)  # will range in 0,1,2,...,15  --> 4 bits required
    fraction = val - integer  # will range in [0, 1)   --> 12 bits used

    # 16 bits = 2 Bytes
    # Byte 1 --> 4 bit integer + first 4 bits of fraction
    # Byte 2 --> last 8 bits of fraction

    # scaling fraction to (0, 2**12) for 12 bits
    scaled_fraction = int((2**12) * fraction)

    # shifting bytes by 4 positions to combine with first 4 bits of fraction to form a byte
    byte1 = (integer << 4) | (scaled_fraction >> 8)
    # extracting last 8 bits of scaled_fraction
    byte2 = scaled_fraction & 0xFF

    # returns 16 bit (2 byte) equivalent of the input floating value
    return bytes([byte1, byte2])


def masterKey(
    x1: list[float], x2: list[float], y1: list[float], y2: list[float]
) -> bytes:
    """Generate the AES master key using the four co-ordinate samples generated using a chaotic function

    Args:
        x1 (list[float]): One of the co-ordinates generated via chaotic function map
        x2 (list[float]): One of the co-ordinates generated via chaotic function map
        y1 (list[float]): One of the co-ordinates generated via chaotic function map
        y2 (list[float]): One of the co-ordinates generated via chaotic function map

    Raises:
        InsufficientSamplesException: occurs if sample size is less than 4

    Returns:
        bytes: the key generated through the sample values. 256 bits = 32 Bytes => size of the bytes = 32
    """
    sampleSize = len(x1)
    if sampleSize <= 3:
        raise InsufficientSamplesException("Minimum 4 Samples required!")

    samplingLen = sampleSize // 4

    # sampling 4 samples from from all the samples
    x1_new = x1[samplingLen - 1 : sampleSize : samplingLen]
    x2_new = x2[samplingLen - 1 : sampleSize : samplingLen]
    y1_new = y1[samplingLen - 1 : sampleSize : samplingLen]
    y2_new = y2[samplingLen - 1 : sampleSize : samplingLen]

    # converting the samples to binary sequence
    x1_new = [__toBinary(i) for i in x1_new]
    y1_new = [__toBinary(i) for i in y1_new]
    x2_new = [__toBinary(i) for i in x2_new]
    y2_new = [__toBinary(i) for i in y2_new]

    # concatenating all the bytes into a 256-bit long key
    key = bytes()
    key += b''.join(x1_new) + b''.join(y1_new) + b''.join(x2_new) + b''.join(y2_new)

    return key


def encrypt(msg: bytes, masterKey: bytes) -> tuple[bytes, bytes]:
    """encrypts the message 'msg' using the AES key 'masterKey'.
    The message may be padded in case the message is not a multiple of the block size.

    Args:
        msg (bytes): message to be encrypted. can be any data in a byte like sequence
        masterKey (bytes): 128/192/256 bit long key used for AES encryption

    Returns:
        tuple[bytes, bytes]: initial vector and cipher text are returned as a tuple
    """
    cipher = AES.new(key=masterKey, mode=AES.MODE_CBC)
    cipherMsg = cipher.encrypt(__addPadding(msg, AES.block_size))
    print(f"AES.block_size: {AES.block_size}")
    print(f"message len: {len(msg)}")
    print(f"cipher length: {len(cipherMsg)}")
    return cipher.iv, cipherMsg


def decrypt(cipherMsg: bytes, masterKey: bytes, initial_vector: bytes) -> bytes:
    """decrypts the message 'cipherMsg' using AES key 'masterKey' and the given initial vector.

    Args:
        cipherMsg (bytes): the byte sequence to be decrypted
        masterKey (bytes): 128/192/256 bit long sequence used to encrypt the message
        initial_vector (bytes): initial vector returned during encryption

    Returns:
        bytes: decrypted message
    """
    cipher = AES.new(key=masterKey, mode=AES.MODE_CBC, iv=initial_vector)
    msg = __removePadding(cipher.decrypt(cipherMsg))
    return msg


def encryptToImage(msg: bytes, masterKey: bytes, filename: str) -> None:
    initial_vector, cipherMsg = encrypt(msg, masterKey)
    cipherMsg = initial_vector + cipherMsg
    totPixels = len(cipherMsg)
    height = floor(sqrt(totPixels))
    
     # finding image dimensions such that height * width = totPixels 
    while totPixels % height != 0:
        height -= 1
    
    img = Image.frombytes(mode="L", size=(totPixels//height, height), data=cipherMsg)
    img.save(filename)


def decryptFromImage(filename: str, masterKey: bytes) -> bytes:
    img = Image.open(filename)
    cipherMsg = bytes(img.getdata())
        
    initial_vector, cipherMsg = cipherMsg[0:16], cipherMsg[16:]
        
    return decrypt(cipherMsg, masterKey, initial_vector)


def imageToBytes(filepath):
    try:
        img = Image.open(filepath)
    except UnidentifiedImageError:
        return None


def __main():
    # x1, x2, y1, y2 = getCoordinates(total_samples=4)
    # key = masterKey(x1,x2,y1,y2, )
    # x1, x2, y1, y2 = getCoordinates(total_samples=4, length_1=2.0000000000000001)
    # key1 = masterKey(x1,x2,y1,y2)
    key = masterKey([0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3])

    print(f"master key length: {len(key)}")

    # with open("text.txt", "rb") as text:
    #     msg = text.read()
    
    
    with Image.open("image.jpg") as img:
        msg = img.tobytes()
        mode = img.mode
        
    print(f"testing on message of length {len(msg)}")
    encryptToImage(msg, key, "text.png")
    plain = decryptFromImage("text.png", key)
    print(mode.__sizeof__())
    print(len(bytes(mode, 'utf-8')))
    size = img.size[0].to_bytes() + img.size[1].to_bytes()
    
    img = Image.frombytes(mode=mode, size=img.size, data=plain)
    img.save("decrypted.png")
    
    if msg == plain:
        print("SUCCESSFUL ENCRYPTION AND DECRYTION!!")
    else:
        print("ERROR!!!!")
    

if __name__ == "__main__":
    __main()