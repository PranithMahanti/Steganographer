import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math

TOKENS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
N = len(TOKENS)
ANGLE_STEP = 360 / N


def extract_angles(img_array, n_pixels=None):
    """
    Extract (R-128, G-128) vector angles for the first n_pixels pixels
    in raster order.  Skips zero vectors.
    """
    pixels = img_array.reshape(-1, 3)
    if n_pixels is not None:
        pixels = pixels[:n_pixels]

    angles = []
    for R, G, B in pixels:
        vx = int(R) - 128
        vy = int(G) - 128
        if vx == 0 and vy == 0:
            continue
        theta = math.degrees(math.atan2(vy, vx))
        if theta < 0:
            theta += 360
        angles.append(theta)
    return np.array(angles)


def compute_psnr(original, stego):
    """Peak Signal-to-Noise Ratio between two uint8 RGB images (arrays)."""
    mse = np.mean((original.astype(np.float64) - stego.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * math.log10(255 ** 2 / mse)


def pixel_delta(original, stego, n_pixels):
    """
    Per-pixel Euclidean distance in RGB between cover and stego,
    for the first n_pixels pixels.
    """
    orig_px = original.reshape(-1, 3)[:n_pixels].astype(np.float64)
    stego_px = stego.reshape(-1, 3)[:n_pixels].astype(np.float64)
    return np.sqrt(np.sum((orig_px - stego_px) ** 2, axis=1))


def plot_angle_comparison(cover_angles, stego_angles, n_encoded,
                          save_path="img/angle_comparison.png"):
    """
    Side-by-side histograms: angle distribution of the encoded pixels
    in the cover vs. the stego image.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

    axes[0].hist(cover_angles, bins=180, color='slategray', edgecolor='none')
    axes[0].set_title(f"Cover image — angles of first {n_encoded} pixels",
                      fontsize=11)
    axes[0].set_xlabel("Angle (degrees)")
    axes[0].set_ylabel("Frequency")

    axes[1].hist(stego_angles, bins=180, color='steelblue', edgecolor='none')
    axes[1].set_title(f"Stego image — same pixels after encoding",
                      fontsize=11)
    axes[1].set_xlabel("Angle (degrees)")

    # Draw vertical lines at nominal token angles
    for ax in axes:
        for k in range(N):
            ax.axvline(k * ANGLE_STEP, color='salmon', linewidth=0.4,
                       alpha=0.7, linestyle='--')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"Saved: {save_path}")


def plot_polar_comparison(cover_angles, stego_angles, n_encoded,
                          save_path="img/polar_comparison.png"):
    """
    Side-by-side polar scatter: cover vs stego for the encoded pixels.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 5),
                             subplot_kw={'projection': 'polar'})

    axes[0].scatter(np.radians(cover_angles), np.ones_like(cover_angles),
                    s=3, alpha=0.3, color='slategray')
    axes[0].set_title(f"Cover (first {n_encoded} pixels)", pad=15)

    axes[1].scatter(np.radians(stego_angles), np.ones_like(stego_angles),
                    s=3, alpha=0.3, color='steelblue')
    axes[1].set_title(f"Stego (same pixels)", pad=15)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"Saved: {save_path}")


def plot_distortion(deltas, save_path="img/distortion.png"):
    """
    Histogram of per-pixel RGB distortion (Euclidean distance) introduced
    by encoding.
    """
    plt.figure(figsize=(8, 4))
    plt.hist(deltas, bins=80, color='darkorange', edgecolor='none')
    plt.xlabel("Per-pixel RGB distortion (Euclidean)", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.title("Distribution of Pixel-Level Distortion Introduced by Encoding",
              fontsize=13)
    plt.axvline(np.mean(deltas), color='black', linestyle='--', linewidth=1.2,
                label=f"Mean = {np.mean(deltas):.2f}")
    plt.axvline(np.median(deltas), color='gray', linestyle=':', linewidth=1.2,
                label=f"Median = {np.median(deltas):.2f}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"Saved: {save_path}")


def plot_magnitude_scatter(cover_arr, stego_arr, n_pixels,
                           save_path="img/magnitude_scatter.png"):
    """
    Scatter plot of original vector magnitude vs stego vector magnitude
    for encoded pixels, to verify the magnitude-preservation strategy.
    """
    cover_px = cover_arr.reshape(-1, 3)[:n_pixels].astype(np.float64)
    stego_px = stego_arr.reshape(-1, 3)[:n_pixels].astype(np.float64)

    orig_r  = np.sqrt((cover_px[:, 0] - 128)**2 + (cover_px[:, 1] - 128)**2)
    stego_r = np.sqrt((stego_px[:, 0] - 128)**2 + (stego_px[:, 1] - 128)**2)

    plt.figure(figsize=(6, 6))
    plt.scatter(orig_r, stego_r, s=4, alpha=0.3, color='steelblue')
    lim = max(orig_r.max(), stego_r.max()) + 5
    plt.plot([0, lim], [0, lim], 'r--', linewidth=1, label="y = x (perfect preservation)")
    plt.xlabel("Original magnitude $r$", fontsize=12)
    plt.ylabel("Encoded magnitude $r'$", fontsize=12)
    plt.title("Magnitude Preservation: Cover vs. Stego Pixels", fontsize=13)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"Saved: {save_path}")


def analyze(cover_path, stego_path, message_length):
    """
    Full comparative analysis between cover and stego image.

    Parameters
    ----------
    cover_path     : str - path to the original cover image
    stego_path     : str - path to the stego image produced by method1_cover.py
    message_length : int - number of pixels that were modified (= len(message))
    """
    cover_arr = np.array(Image.open(cover_path).convert("RGB"))
    stego_arr = np.array(Image.open(stego_path).convert("RGB"))

    assert cover_arr.shape == stego_arr.shape, \
        "Cover and stego images must have identical dimensions."

    n = message_length   # number of encoded pixels

    # PSNR
    psnr_full = compute_psnr(cover_arr, stego_arr)
    # PSNR restricted to only the modified pixels
    cover_patch = cover_arr.reshape(-1, 3)[:n]
    stego_patch = stego_arr.reshape(-1, 3)[:n]
    psnr_patch = compute_psnr(cover_patch, stego_patch)

    print(f"PSNR (whole image)      : {psnr_full:.2f} dB")
    print(f"PSNR (encoded pixels)   : {psnr_patch:.2f} dB")
    print(f"  (PSNR > 40 dB is generally considered imperceptible)")

    # Per-pixel distortion
    deltas = pixel_delta(cover_arr, stego_arr, n)
    print(f"\nDistortion over {n} encoded pixels:")
    print(f"  Mean   : {np.mean(deltas):.2f}")
    print(f"  Median : {np.median(deltas):.2f}")
    print(f"  Max    : {np.max(deltas):.2f}")
    print(f"  % pixels with delta > 10 : "
          f"{100 * np.mean(deltas > 10):.1f}%")
    print(f"  % pixels with delta > 30 : "
          f"{100 * np.mean(deltas > 30):.1f}%")

    # Angle distributions
    cover_angles = extract_angles(cover_arr, n_pixels=n)
    stego_angles = extract_angles(stego_arr, n_pixels=n)

    print(f"\nAngle extraction:")
    print(f"  Cover vectors (non-zero): {len(cover_angles)}")
    print(f"  Stego vectors (non-zero): {len(stego_angles)}")

    # Plots
    plot_angle_comparison(cover_angles, stego_angles, n)
    plot_polar_comparison(cover_angles, stego_angles, n)
    plot_distortion(deltas)
    plot_magnitude_scatter(cover_arr, stego_arr, n)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python analysis_cover.py <cover_path> "
              "<stego_path> <message_length>")
    else:
        analyze(sys.argv[1], sys.argv[2], int(sys.argv[3]))