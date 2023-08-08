"""
AES master key generation along with encryption and decryption
"""

import AESRoundFunc
import random


class InsufficientSamplesException(Exception):
    """Custom Exception that can be called when the samples of provided variable are not enough to perform the required task

    Args:
        Exception (class): Extends the Exception class
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def __toBinary(val: float) -> bytes:
    if val <= -8 or val >= 8:
        raise ValueError("floating value must be  in range (-8, 8)")

    val += 8  # converting the range to (0, 16) from (-8, 8)

    integer = int(val)  # will range in 0,1,2,...,15  --> 4 bits required
    fraction = val - integer  # will range in [0, 1)   --> 12 bits used
    """ 
    16 bits = 2 Bytes
    Byte 1 --> 4 bit integer + first 4 bits of fraction
    Byte 2 --> last 8 bits of fraction
    """
    # scaling fraction to (0, 2**12) for 12 bits
    scaled_fraction = int((2**12) * fraction)

    # shifting bytes by 4 positions to combine with first 4 bits of fraction to form a byte
    byte1 = (integer << 4) | (scaled_fraction >> 8)
    # extracting last 8 bits of scaled_fraction
    byte2 = scaled_fraction & 0xFF

    # returns 16 bit (2 byte) equivalent of the input floating value
    return bytes([byte1, byte2])


def __addPadding(data: bytes, block_size: int) -> bytes:
    """pads the data with \x00 byte at end so that it is becomes a multiple of block_size where block_size is in bytes"""
    return data + b"\x00" * (block_size - len(data) % block_size)


def __removePadding(data: bytes) -> bytes:
    """removes the trailing \x00 bytes at the end of the data"""
    return data.rstrip(b"\x00")


def generateRoundKeys(
    x1: list[float], x2: list[float], y1: list[float], y2: list[float], rounds: int = 10
) -> list[bytes]:
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

    totalSamples = len(x1)
    """
    1 round-key = 128 bits = 16 bytes
    n round-keys = 16 * n bytes
    if 1 sample = 2 bytes, 1 sample for 4 variables = 8 bytes
    samples req per variable = total bytes / 8 = 16 * n / 8 = 2 * n
    """
    samplesReq = 2 * rounds

    if totalSamples < samplesReq:
        raise InsufficientSamplesException(
            f"Minimum {samplesReq} Samples per variable required!"
        )

    reSamplingSpace = totalSamples // samplesReq

    # sampling `samplesReq` samples from from all the samples
    x1_new = x1[reSamplingSpace - 1 : totalSamples : reSamplingSpace]
    x2_new = x2[reSamplingSpace - 1 : totalSamples : reSamplingSpace]
    y1_new = y1[reSamplingSpace - 1 : totalSamples : reSamplingSpace]
    y2_new = y2[reSamplingSpace - 1 : totalSamples : reSamplingSpace]

    # converting the samples to binary sequence
    x1_new = [__toBinary(i) for i in x1_new]
    y1_new = [__toBinary(i) for i in y1_new]
    x2_new = [__toBinary(i) for i in x2_new]
    y2_new = [__toBinary(i) for i in y2_new]

    # concatenating all the bytes into a 16*n byte long key
    initialKey = (
        b"".join(x1_new) + b"".join(y1_new) + b"".join(x2_new) + b"".join(y2_new)
    )
    roundKeys = [initialKey[i : i + 16] for i in range(0, len(initialKey), 16)]
    return roundKeys


def encrypt(msg: bytes, roundKeys: list[bytes]) -> bytes:
    msg = __addPadding(msg, 16)
    msg_blocks = [msg[i : i+16] for i in range(0, len(msg), 16)]

    cipher_blocks = []

    for block in msg_blocks:
        state = AESRoundFunc.blockToState(block)

        state = AESRoundFunc.addRoundKey(state, AESRoundFunc.blockToState(roundKeys[0]))
        for i in range(1, len(roundKeys) - 1):
            state = AESRoundFunc.subBytes(state)
            state = AESRoundFunc.shiftRows(state)
            state = AESRoundFunc.mixColumns(state)
            state = AESRoundFunc.addRoundKey(state, AESRoundFunc.blockToState(roundKeys[i]))

        state = AESRoundFunc.subBytes(state)
        state = AESRoundFunc.shiftRows(state)
        state = AESRoundFunc.addRoundKey(state, AESRoundFunc.blockToState(roundKeys[-1]))
        cipher_blocks.append( AESRoundFunc.stateToBlock(state) )
    
    return b''.join(cipher_blocks)


def decrypt(cipherMsg: bytes, roundKeys: list[bytes]) -> bytes:
    cipher_blocks = [cipherMsg[i : i+16] for i in range(0, len(cipherMsg), 16)]
    msg_blocks = []
    
    for block in cipher_blocks:
        state = AESRoundFunc.blockToState(block)

        state = AESRoundFunc.addRoundKey(state, AESRoundFunc.blockToState(roundKeys[-1]) )
        
        for i in range(len(roundKeys) - 1, 0, -1):
            state = AESRoundFunc.invShiftRows(state)
            state = AESRoundFunc.invSubBytes(state)
            state = AESRoundFunc.addRoundKey(state, AESRoundFunc.blockToState(roundKeys[i]) )
            state = AESRoundFunc.invMixColumns(state)
            
        state = AESRoundFunc.invShiftRows(state)
        state = AESRoundFunc.invSubBytes(state)
        state = AESRoundFunc.addRoundKey(state, AESRoundFunc.blockToState(roundKeys[0]) )
        msg_blocks.append( AESRoundFunc.stateToBlock(state) )

    return __removePadding( b''.join(msg_blocks) )
    

def __main():
    n = 20
    start, end = -5, 5
    samples = [((end - start) * random.random() + start) for i in range(n)]
    roundkeys = generateRoundKeys(samples, samples, samples, samples)

    message = b'hello world'
    print(len(message), message)
    message = encrypt(message, roundkeys)
    print(len(message), message)
    message = decrypt(message, roundkeys)
    print(len(message), message)
    


if __name__ == "__main__":
    __main()
