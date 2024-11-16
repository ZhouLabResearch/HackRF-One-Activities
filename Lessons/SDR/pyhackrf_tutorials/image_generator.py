import matplotlib.pyplot as plt
import numpy as np

# Example: Decoded image array
image_data = np.random.rand(800, 1024)  # Replace with actual decoded data
plt.imshow(image_data, cmap="gray", aspect="auto")
plt.title("NOAA APT Image")
plt.axis("off")
plt.savefig("noaa_image.png")
plt.show()
