# Geometric Steganography via Angular Color Vector Encoding

A steganographic method that hides text inside existing images by rotating pixel color vectors to target angles in the RG plane, rather than modifying pixel intensities. Each character is encoded in the *direction* of a pixel's color vector while its magnitude is preserved.

---

## How It Works

A pixel's RGB triple can be interpreted as a vector in 3D color space. Conventional steganography (e.g. LSB) modifies the *magnitude* of color components. This project takes a different approach, that information is encoded in the *direction* of the vector, analogous to phase-shift keying in communications.

Each pixel is centered at the gray point `(128, 128, 128)`. The `(R-128, G-128)` pair forms a 2D vector in the RG plane. To encode a character:

1. The character is mapped to one of 37 angular sectors (~9.73° each)
2. The pixel's color vector is rotated to that sector
3. The vector's original magnitude is preserved
4. The B channel is never touched

Decoding reads the angle of each modified pixel's color vector and maps it back to the nearest character.

```
Vocabulary: A-Z, 0-9, and space: 37 tokens: ~9.73° per token
```

---

## Project Structure

```
M1
├── method.py      # Encoder and decoder (cover image method)
├── analysis.py     # Statistical analysis: histograms, PSNR, distortion
├── noise_test.py         # Noise tolerance test across Gaussian sigma values
├── img/                  # Output directory for encoded images and plots
└── paper/
    ├── paper.tex         # Full research paper (LaTeX)
    └── refs.bib          # Bibliography
```

---

## Requirements

```
pip install numpy pillow matplotlib
```

---

## Usage

### Encode a message into a cover image

```python
from method import encode_into_cover

encode_into_cover(
    message="Prometheus",
    cover_image_path="cover.png",
    output_path="img/stego.png"
)
```

### Decode a message from a stego image

```python
from method import decode_from_cover

message = decode_from_cover(
    stego_image_path="img/stego.png",
    message_length=11
)
print(message)  # Prometheus
```

### Quick correctness check

```
python method.py cover.png
```

---

## Analysis

### Cover vs. stego comparison

Generates four plots comparing the cover and stego images:
- Angle histogram (before and after encoding)
- Polar distribution of color vectors
- Per-pixel RGB distortion distribution
- Magnitude preservation scatter plot (original r vs. encoded r)

Also prints PSNR for the whole image and the encoded pixel region.

```
python analysis.py cover.png img/stego.png <message_length>
```

**Example:**
```
python analysis.py cover.png img/stego.png 5000
```

Output figures are saved to `img/`:
```
img/angle_comparison.png
img/polar_comparison.png
img/distortion.png
img/magnitude_scatter.png
```

### Noise tolerance test

Measures decode accuracy as Gaussian noise of increasing sigma is added to the stego image. Averages over multiple trials per sigma value.

```
python noise_test.py cover.png img/stego.png "YOUR MESSAGE"
```

Expected behavior: accuracy stays near 100% for low sigma, then drops sharply around σ ≈ 5 (pixel units), consistent with the ±4.86° decoding tolerance.

Output: `img/noise_tolerance.png`

---

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TOKENS` | `A-Z 0-9 space` | 37-character vocabulary |
| `ANGLE_STEP` | `~9.73°` | Angular sector width per token |
| `MIN_R` | `30` | Minimum vector magnitude (magnitude floor for near-gray pixels) |
| Encoding noise | `±4°` | Uniform noise added per token to avoid hard boundaries |

---

## Detectability

The encoding introduces a **geometric fingerprint**: the angle distribution of modified pixels collapses into 37 equally-spaced peaks, which is absent from natural images and detectable by simple histogram analysis.

This is a known limitation of absolute angular encoding. Two extensions are proposed in the paper to address it:

- **Differential encoding** — encodes angular *increments* between consecutive pixels rather than absolute angles, causing the marginal distribution to converge to uniform. Also acts as a stream cipher when the initial reference angle is kept secret.
- **Spherical encoding** — generalizes the scheme to all three RGB channels using spherical coordinates, increasing vocabulary capacity and dispersing the fingerprint into a harder-to-analyze 3D space.

---

## Paper

A full write-up of the method, quantization error analysis, and experimental results is in `paper/paper.tex`. Compile with:

```
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

The compiled paper (in pdf format) is also available: `Geometric_Encoding_Schemes_for_Image_Steganography_Using_Vector_Direction.pdf`

---

## Limitations

- **Cover image required** — the encoder modifies pixels in an existing image; it does not generate synthetic images
- **Lossless formats only** — JPEG compression shifts pixel values and corrupts the encoded angles; use PNG
- **Spatial domain fragility** — any post-processing that alters pixel values (resize, color correction) will break decoding
- **No error correction** — a single-pixel corruption causes a single character error; adding a Reed-Solomon or BCH code before encoding would improve robustness

---

## Author

Mahanti Pranith  
B.E. Computer Science, BITS Pilani Hyderabad Campus  
`pranithmahanti@gmail.com`