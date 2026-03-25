import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import math


def extract_angles(image_path):

    img = np.array(Image.open(image_path))
    angles = []

    for row in img:
        for R, G, B in row:

            vx = int(R) - 128
            vy = int(G) - 128

            if vx == 0 and vy == 0:
                continue

            theta = math.degrees(math.atan2(vy, vx))

            if theta < 0:
                theta += 360

            angles.append(theta)

    return np.array(angles)


def plot_histogram(angles):

    plt.figure(figsize=(8,5))
    plt.hist(angles, bins=180)
    plt.xlabel("Angle (degrees)")
    plt.ylabel("Frequency")
    plt.title("Angle Distribution of Image Vectors")
    plt.show()
    plt.savefig("img/hist_analysis.png")


def plot_polar(angles):

    theta = np.radians(angles)

    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, projection='polar')
    ax.scatter(theta, np.ones_like(theta), s=5)
    ax.set_title("Polar Distribution of Vector Angles")
    plt.show()
    plt.savefig("img/polar_analysis.png")


def analyze(image_path):

    angles = extract_angles(image_path)

    print("Total vectors:", len(angles))

    plot_histogram(angles)
    plot_polar(angles)


if __name__ == "__main__":
    analyze("img/enc1.png")