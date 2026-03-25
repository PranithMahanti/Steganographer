import numpy as np
from PIL import Image
import math
import random

# Used 37 tokens instead of 36 (included character for space)
TOKENS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
TOKEN_TO_INDEX = {c: i for i, c in enumerate(TOKENS)}
INDEX_TO_TOKEN = {i: c for i, c in enumerate(TOKENS)}

ANGLE_STEP = 360 / len(TOKENS)

def encode_message(message):

    message = message.upper()
    width = len(message)
    height = 1

    img = np.zeros((height, width, 3), dtype=np.uint8)

    for i, ch in enumerate(message):

        token_index = TOKEN_TO_INDEX[ch]

        base_angle = token_index * ANGLE_STEP
        noise = random.uniform(-4, 4)

        theta = math.radians(base_angle + noise)

        r = random.uniform(40, 100)

        vx = r * math.cos(theta)
        vy = r * math.sin(theta)

        R = int(np.clip(128 + vx, 0, 255))
        G = int(np.clip(128 + vy, 0, 255))
        B = random.randint(0,255)

        img[0, i] = (R, G, B)

    return Image.fromarray(img)

def decode_image(image):

    img = np.array(image)
    message = ""

    for R, G, B in img[0]:

        vx = int(R) - 128
        vy = int(G) - 128

        theta = math.degrees(math.atan2(vy, vx))

        if theta < 0:
            theta += 360

        token_index = round(theta / ANGLE_STEP) % len(TOKENS)

        message += INDEX_TO_TOKEN[token_index]

    return message


def check():
    msg = "PROMETHEUS"

    img = encode_message(msg)
    img.save("img/encoded.png")

    decoded = decode_image(img)

    print("Decoded:", decoded)

    # Generating a random long message to analyse angle clustering in analysis
    msg_analysis = "".join(random.choice(TOKENS) for i in range(5000))

    img = encode_message(msg_analysis)
    img.save("img/enc1.png")

if __name__ == "__main__":
    check()