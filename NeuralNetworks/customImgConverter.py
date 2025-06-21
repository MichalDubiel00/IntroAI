from PIL import Image, ImageOps
import numpy as np

# Load and convert to grayscale
for i in range(0,9):
    img = Image.open(f"my_digit{i}.png").convert("L")  # L = 8-bit grayscale

    # Resize to MNIST size
    img = img.resize((28, 28))

    # Invert the image
    img = ImageOps.invert(img)


    # Convert to numpy array for CSV usage
    pixels = np.array(img).reshape(-1)  # Flatten to 784
    label = i  # replace with actual label

    # Create CSV line
    csv_line = ",".join([str(label)] + [str(int(p)) for p in pixels])

    # Save to file
    with open("custom_test.csv", "a") as f:
        f.write(csv_line + "\n")


