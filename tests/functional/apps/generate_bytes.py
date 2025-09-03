import os
import sys
random_bytes = os.urandom(int(sys.argv[1]))
hex_string = random_bytes.hex()
print(hex_string)
