from PIL import Image
import easyocr
import numpy as np


def solve_captcha():
    # Load the image using PIL
    try:
        image = Image.open(r'C:\Users\moawezz\Desktop\Kalinan\Captchas\cap.png')
        image = np.array(image)
    except IOError as e:
        print("An error occurred while trying to load the image: ", str(e))

    # Recognize the text using easyocr
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    # Extract the number from the recognized text
    number = result[0][1]
    # Print the extracted number
    return str(number)