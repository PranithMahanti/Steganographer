import numpy as np
from PIL import Image
import math
import random
import cmath

TOKENS = "".join(chr(i) for i in range(128))
TOKEN_TO_INDEX = {c:i for i,c in enumerate(TOKENS)}
INDEX_TO_TOKEN = {i:c for i,c in enumerate(TOKENS)}

STEP_RADIUS = 30
MAX_VECTOR = 110

# Precompute 128 integer step vectors
STEP_VECTORS = []

for i in range(128):
    theta = 2*math.pi*i/128
    step = STEP_RADIUS * cmath.exp(1j*theta)
    step = complex(round(step.real), round(step.imag))
    STEP_VECTORS.append(step)


def encode_message(message):

    width = len(message)
    img = np.zeros((1,width,3),dtype=np.uint8)

    prev = 0+0j

    for i,ch in enumerate(message):

        step = STEP_VECTORS[TOKEN_TO_INDEX[ch]]

        v = prev + step

        if abs(v.real) > MAX_VECTOR or abs(v.imag) > MAX_VECTOR:
            prev = 0+0j
            v = step

        R = int(128 + v.real)
        G = int(128 + v.imag)
        B = random.randint(0,255)

        img[0,i] = (R,G,B)

        prev = v

    return Image.fromarray(img)


def decode_image(image):

    img = np.array(image)

    prev = 0+0j
    message = ""

    for R,G,B in img[0]:

        v = complex(int(R)-128, int(G)-128)

        step = v - prev

        # find closest step vector
        token_index = min(
            range(len(STEP_VECTORS)),
            key=lambda i: abs(step - STEP_VECTORS[i])
        )

        message += INDEX_TO_TOKEN[token_index]

        prev = v

    return message


def check():

    msg = "PROMETHEUS"

    img = encode_message(msg)
    img.save("encoded.png")

    decoded = decode_image(img)

    print("Decoded:",decoded)


if __name__ == "__main__":
    check()