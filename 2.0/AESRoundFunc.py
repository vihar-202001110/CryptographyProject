from AESMatrices import subBox, invSubBox, gfp2, gfp3, gfp9, gfp11, gfp13, gfp14, Rcon
from pprint import pprint

#################################### BLOCK - STATE CONVERSIONS ####################################
def blockToState(block: bytes) -> list[list[bytes]]:
    if len(block) != 16:
        raise ValueError("[AESRoundFunc]: [blockToState]: block size must be 16 bytes")
    state = []
    for i in range(4):
        state.append([])
        for j in range(4):
            state[-1].append(bytes([block[i * 4 + j]]))

    return state


def stateToBlock(state: list[list[bytes]]) -> bytes:
    if len(state) != 4:
        raise ValueError("[AESRoundFunc]: [stateToBlock]: state must be 4x4 byte-grid")

    block = b"".join([b"".join(row) for row in state])
    if len(block) != 16:
        raise ValueError("[AESRoundFunc]: [stateToBlock]: state must be 4x4 byte-grid")

    return block


###################################################################################################


##################################### ADD ROUND KEY OPERATION #####################################
def addRoundKey(
    state: list[list[bytes]], roundKey: list[list[bytes]]
) -> list[list[bytes]]:
    if len(roundKey) != 4 or len(state) != 4:
        raise ValueError("[AESRoundFunc]: [addRoundKey]: 4x4 byte-grid required for state and roundKey")

    xor = []
    for stateRow, rkRow in zip(state, roundKey):
        xor.append([])
        if len(rkRow) != 4 or len(stateRow) != 4:
            raise ValueError("[AESRoundFunc]: [addRoundKey]: 4x4 byte-grid required for state and roundKey")
        
        for byte1, byte2 in zip(stateRow, rkRow):
            xor[-1].append(bytes([int(byte1.hex(), 16) ^ int(byte2.hex(), 16)]))

    return xor


##################################################################################################


########################### SHIFT ROW AND INVERSE SHIFT ROW OPERATIONS ###########################
def shiftRows(state: list[list[bytes]]) -> list[list[bytes]]:
    if len(state) != 4:
        raise ValueError("[AESRoundFunc]: [shiftRows]: 4x4 byte-grid required for state")

    for i in range(4):
        if len(state[i]) != 4:
            raise ValueError("[AESRoundFunc]: [shiftRows]: 4x4 byte-grid required for state")
        state[i] = state[i][i:] + state[i][:i]

    return state


def invShiftRows(state: list[list[bytes]]) -> list[list[bytes]]:
    if len(state) != 4:
        raise ValueError("[AESRoundFunc]: [shiftRows]: 4x4 byte-grid required for state")

    for i in range(4):
        if len(state[i]) != 4:
            raise ValueError("[AESRoundFunc]: [shiftRows]: 4x4 byte-grid required for state")
        state[i] = state[i][4 - i :] + state[i][: 4 - i]

    return state


##################################################################################################


########################## MIX COLUMN AND INVERSE MIX COLUMN OPERATIONS ##########################
def mixColumns(state: list[list[bytes]]) -> list[list[bytes]]:
    if len(state) != 4:
        raise ValueError("[AESRoundFunc]: [mixColumns]: 4x4 byte-grid required for state")
    state2 = state.copy()
    for i in range(4):
        if len(state[i]) != 4:
            raise ValueError("[AESRoundFunc]: [mixColumns]: 4x4 byte-grid required for state")
        state2[i][0] = bytes([ gfp2[int(state[i][0].hex(), 16)] ^ gfp3[int(state[i][1].hex(), 16)] ^ int(state[i][2].hex(), 16) ^ int(state[i][3].hex(), 16) ])
        state2[i][1] = bytes([ gfp2[int(state[i][1].hex(), 16)] ^ gfp3[int(state[i][2].hex(), 16)] ^ int(state[i][0].hex(), 16) ^ int(state[i][3].hex(), 16) ])
        state2[i][2] = bytes([ gfp2[int(state[i][2].hex(), 16)] ^ gfp3[int(state[i][3].hex(), 16)] ^ int(state[i][0].hex(), 16) ^ int(state[i][1].hex(), 16) ])
        state2[i][3] = bytes([ gfp2[int(state[i][3].hex(), 16)] ^ gfp3[int(state[i][0].hex(), 16)] ^ int(state[i][1].hex(), 16) ^ int(state[i][2].hex(), 16) ])
    
    return state2


def invMixColumns(state: list[list[bytes]]) -> list[list[bytes]]:
    if len(state) != 4:
        raise ValueError("[AESRoundFunc]: [invMixColumns]: 4x4 byte-grid required for state")
    state2 = state.copy()
    for i in range(4):
        if len(state[i]) != 4:
            raise ValueError("[AESRoundFunc]: [invMixColumns]: 4x4 byte-grid required for state")
        state2[i][0] = bytes([ gfp9[int(state[i][3].hex(), 16)] ^ gfp11[int(state[i][1].hex(), 16)] ^ gfp13[int(state[i][2].hex(), 16)] ^ gfp14[int(state[i][0].hex(), 16)] ])
        state2[i][1] = bytes([ gfp9[int(state[i][0].hex(), 16)] ^ gfp11[int(state[i][2].hex(), 16)] ^ gfp13[int(state[i][3].hex(), 16)] ^ gfp14[int(state[i][1].hex(), 16)] ])
        state2[i][2] = bytes([ gfp9[int(state[i][1].hex(), 16)] ^ gfp11[int(state[i][3].hex(), 16)] ^ gfp13[int(state[i][0].hex(), 16)] ^ gfp14[int(state[i][2].hex(), 16)] ])
        state2[i][3] = bytes([ gfp9[int(state[i][2].hex(), 16)] ^ gfp11[int(state[i][0].hex(), 16)] ^ gfp13[int(state[i][1].hex(), 16)] ^ gfp14[int(state[i][3].hex(), 16)] ])

    return state2
##################################################################################################


########################### SUB BYTES AND INVERSE SUB BYTES OPERATIONS ###########################
def subBytes(state: list[list[bytes]]) -> list[list[bytes]]:
    if len(state) != 4:
        raise ValueError("[AESRoundFunc]: [subBytes]: 4x4 byte-grid required for state")
    
    for i in range(4):
        if len(state[i]) != 4:
            raise ValueError("[AESRoundFunc]: [subBytes]: 4x4 byte-grid required for state")
        state[i] = [ subBox[int(byte.hex(), 16)].to_bytes() for byte in state[i] ]
    
    return state
        


def invSubBytes(state: list[list[bytes]]) -> list[list[bytes]]:
    if len(state) != 4:
        raise ValueError("[AESRoundFunc]: [invSubBytes]: 4x4 byte-grid required for state")
    
    for i in range(4):
        if len(state[i]) != 4:
            raise ValueError("[AESRoundFunc]: [invSubBytes]: 4x4 byte-grid required for state")
        state[i] = [ invSubBox[int(byte.hex(), 16)].to_bytes() for byte in state[i] ]
    
    return state
##################################################################################################


def __main__():
    state = [
        [b"\x01", b"\x02", b"\x03", b"\x04"],
        [b"\x01", b"\x02", b"\x03", b"\x04"],
        [b"\x01", b"\x02", b"\x03", b"\x04"],
        [b"\x01", b"\x02", b"\x03", b"\x04"],
    ]
    roundKey = [
        [b"\x00", b"\x01", b"\x02", b"\x03"],
        [b"\x04", b"\x05", b"\x06", b"\x07"],
        [b"\x08", b"\x09", b"\x0a", b"\x0b"],
        [b"\x0c", b"\x0d", b"\x0e", b"\x0f"],
    ]
    
    print(1)
    pprint(state)
    print(2)
    state = mixColumns(state)
    pprint(state)
    print(3)
    state = invMixColumns(state)
    pprint(state)


if __name__ == "__main__":
    __main__()
