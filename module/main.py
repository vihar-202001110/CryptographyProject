from DoublePendulum import getCoordinates
from AES import masterKey

x1,y1,x2,y2 = getCoordinates()

print("Total samples per variable: ", len(x1))

key = masterKey(x1,x2,y1,y2)
print(f"AES Master Key Length (Bytes): {len(key)}")
print(f"AES Master Key Length (bits): {len(key) * 8}")
