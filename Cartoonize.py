import cv2
import numpy as np
import sys

def color_quantization(image, k):
    # Convert image to a 2D array of pixels
    data = image.reshape((-1, 3))
    
    # Convert to float32 for k-means
    data = np.float32(data)
    
    # Define criteria and apply k-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Convert back to 8-bit values
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized = quantized.reshape(image.shape)
    
    return quantized

def adjust_brightness(image, brightness=30):
    # Apply brightness adjustment
    new_image = cv2.convertScaleAbs(image, beta=brightness)
    return new_image

def lighten_colors_hsv(image, value_increase=40):
    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Increase the value (brightness) channel to lighten colors
    v = cv2.add(v, value_increase)
    v = np.clip(v, 0, 255)  # Ensure values are within valid range
    
    # Merge the channels back and convert to BGR
    hsv_lighter = cv2.merge((h, s, v))
    lighter_image = cv2.cvtColor(hsv_lighter, cv2.COLOR_HSV2BGR)
    
    return lighter_image


def process(file, processed_file):

    try:
        # Read the image
        img = cv2.imread(file)
    
    except:
        print("Unable to read file")

    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to smooth the image
    gray_blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # Apply adaptive threshold to get outlines
    outlines = cv2.adaptiveThreshold(gray_blurred, 255,
                                    cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 5, 2)

    # Apply bilateral filter for cartoon effect
    color = cv2.bilateralFilter(img, 50, 75, 75, cv2.BORDER_REFLECT101)

    # Apply color quantization with increased 'k' for more colors
    quantized_color = color_quantization(color, k=512)

    # Lighten the colors in the quantized image using HSV
    lighter_color = lighten_colors_hsv(quantized_color, value_increase=25)
        
    # Sharpen the image
    sharpen_kernel = np.array([[0, -1, 0],
                            [-1, 5, -1],
                            [0, -1, 0]])
    sharpened = cv2.filter2D(lighter_color, -1, sharpen_kernel)

    # Adjust brightness of the sharpened image
    brighter_sharpened = adjust_brightness(sharpened, brightness=10)

    # Convert outlines to 3 channels for blending
    outlines_colored = cv2.cvtColor(outlines, cv2.COLOR_GRAY2BGR)

    # Blend the brightened, sharpened image with the outlines using cv2.divide
    cartoon = cv2.divide(brighter_sharpened, outlines_colored, scale=255)

    # Display and save the results
    # cv2.imwrite("Original_Image.jpg", img)
    # cv2.imwrite("Outlines.jpg", outlines)
    cv2.imwrite(processed_file, cartoon)

#cartoonize_image
def cartoonize_image(file_path, processed_file_path):
    process(file_path, processed_file_path)