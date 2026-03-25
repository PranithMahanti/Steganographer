# Steganographer
Colours can be represented as vectors, since each colour can be represented as a combination of RGB.  
If we are going to use this for encoding/encryption, we will need a method to interpret text as a vector. 

## Method 1: Basic
#### Encoding
One of the simplest algorithm I thought of was to use the direction of the vectors; each token (a letter or a number), differs by 10 degrees.
Now we take each letter of the message, encode it and use the colour in a pixel. This way we can generate an image with our message.

But since this is too simple and the image generated will be too suspicious, we need to randomise the encoding for each token. This can be done by mapping each token to a range rather than a fixed direction. To the current direction of the token we can add +/- 5 degrees to get this range. Since the magnitude of the vector doesn't really matter, we can multiply the resultant vector by an arbitrary number.

#### Decoding
To decode, we just have to retrace our steps:
1. Find the unit vector of the pixel
2. Find the direction of the vector
3. Round it off to the nearest 10
4. Find the corresponding token

#### Weaknesses
Even with noise, an attacker could:
1. Extract pixel vectors
2. Compute angles
3. Plot histogram
This might give them 36 clusters, and figuring out the rest it relatively simple.

### Ideas
1. Right now, we are still operating in a 2D plane (Using only any two of RGB). We can turn this into a 3D sphere (using all three of RGB).
2. Instead of having absolute angles, we can turn this into angles between two neighbouring vectors.
3. Add a key to turn this into an encryption system.
4. Using 128 ASCII tokens instead of 36 tokens.

## Method 2:

### 2.1
I was wondering how to use the spherical system and then I remembered the concept of spherical coordinates. This will let us use the horizontal and vertical angles as the token; hence spreading across the sphere and making it harder to detect.
The second idea of using relative directions is self-explanatory.
### 2.2
My roommate suggested dividing the region into 256 cubes and mapping each cube to an ASCII character. This is an interesting idea; I will implement this but I will not go forward with this idea because it will run into the same problem as Method 1, where the attacker can analyse clusters.
(This method uses absolute coordinates too, not the direction)