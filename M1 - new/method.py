import numpy as np
from PIL import Image
import math
import random

TOKENS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
TOKEN_TO_INDEX = {c: i for i, c in enumerate(TOKENS)}
INDEX_TO_TOKEN = {i: c for i, c in enumerate(TOKENS)}

N = len(TOKENS)
ANGLE_STEP = 360 / N           # ~9.73 degrees per token
MIN_R = 30                     # minimum vector magnitude after modification


def _encode_pixel(R, G, token_index):
    """
    Modify R and G of an existing pixel to encode token_index.

    Strategy: preserve the original vector magnitude as closely as possible.
    Only the direction is forced toward the target angle.
    B is left completely untouched.
    """
    base_angle = token_index * ANGLE_STEP
    noise = random.uniform(-4, 4)
    theta = math.radians(base_angle + noise)

    # Use the original pixel's magnitude, but floor it at MIN_R
    # so we never encode a near-zero vector that decodes unreliably
    orig_vx = int(R) - 128
    orig_vy = int(G) - 128
    orig_r = math.hypot(orig_vx, orig_vy)
    r = max(orig_r, MIN_R)

    new_vx = r * math.cos(theta)
    new_vy = r * math.sin(theta)

    new_R = int(np.clip(round(128 + new_vx), 0, 255))
    new_G = int(np.clip(round(128 + new_vy), 0, 255))

    return new_R, new_G


def encode_into_cover(message, cover_image_path, output_path,
                      start_pixel=(0, 0)):
    """
    Embed a message into an existing cover image by modifying the
    R and G channels of selected pixels.  B is never touched.

    Pixels are selected in raster order starting from start_pixel.
    The image must have at least len(message) pixels available from
    that point onward.

    Parameters
    ----------
    message          : str  - plaintext to embed (A-Z, 0-9, space)
    cover_image_path : str  - path to the carrier image (any RGB format)
    output_path      : str  - where to save the stego image
    start_pixel      : (row, col) - where to begin writing
    """
    message = message.upper()
    img = np.array(Image.open(cover_image_path).convert("RGB"))
    h, w, _ = img.shape

    start_row, start_col = start_pixel
    flat_start = start_row * w + start_col

    if flat_start + len(message) > h * w:
        raise ValueError(
            f"Message length {len(message)} exceeds available pixels "
            f"({h * w - flat_start}) from start_pixel {start_pixel}."
        )

    pixels = img.reshape(-1, 3)   # flatten to list of pixels

    for i, ch in enumerate(message):
        idx = flat_start + i
        R, G, B = int(pixels[idx, 0]), int(pixels[idx, 1]), int(pixels[idx, 2])
        new_R, new_G = _encode_pixel(R, G, TOKEN_TO_INDEX[ch])
        pixels[idx, 0] = new_R
        pixels[idx, 1] = new_G
        # pixels[idx, 2] = B, B is unchanged

    stego = Image.fromarray(pixels.reshape(h, w, 3))
    stego.save(output_path)
    print(f"Encoded {len(message)} tokens into '{output_path}'.")


def decode_from_cover(stego_image_path, message_length,
                      start_pixel=(0, 0)):
    """
    Recover a message from a stego image.

    Parameters
    ----------
    stego_image_path : str       - path to the stego image
    message_length   : int       - number of characters to recover
    start_pixel      : (row, col) - must match the value used during encoding

    Returns
    -------
    str - decoded message
    """
    img = np.array(Image.open(stego_image_path).convert("RGB"))
    h, w, _ = img.shape

    start_row, start_col = start_pixel
    flat_start = start_row * w + start_col
    pixels = img.reshape(-1, 3)

    message = ""

    for i in range(message_length):
        idx = flat_start + i
        R, G = int(pixels[idx, 0]), int(pixels[idx, 1])

        vx = R - 128
        vy = G - 128

        if vx == 0 and vy == 0:
            # Zero vector; magnitude was too low to encode reliably
            message += "?"
            continue

        theta = math.degrees(math.atan2(vy, vx))
        if theta < 0:
            theta += 360

        token_index = round(theta / ANGLE_STEP) % N
        message    += INDEX_TO_TOKEN[token_index]

    return message


def check(cover_path):
    msg = "".join(random.choice(TOKENS) for i in range(5000))

    encode_into_cover(msg, cover_path, "img/stego.png", start_pixel=(0, 0))
    decoded = decode_from_cover("img/stego.png", len(msg), start_pixel=(0, 0))

    print(f"Original : {msg}")
    print(f"Decoded  : {decoded}")
    assert msg == decoded, f"Mismatch: {decoded}"
    print("OK.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python method1_cover.py <cover_image_path>")
    else:
        check(sys.argv[1])