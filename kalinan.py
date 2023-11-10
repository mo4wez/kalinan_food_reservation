from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from kalinan_config import KalinanConfig
from time import sleep
import logging
import re
from PIL import Image
import easyocr
import numpy as np


class Kalinan:
    def __init__(self):
        self.config = KalinanConfig()
        self.driver = self._setup_driver()
        self.term_no = None
        self.captcha_code = None
        self.student_name = None

    def run(self):
        sleep(3)
        self.login_to_kalinan()

    def _setup_driver(self):
        logging.info('Setting up driver...')
        # options = Options()
        # excluded_url = 'https://education.cfu.ac.ir/forms/authenticateuser/main.htm'
        # options.add_argument(f"--no-proxy-server={excluded_url}")
        # options.add_argument("--headless=new")  # run in headless mode (without gui)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),)

        return driver
    
    def login_to_kalinan(self):
        self.driver.get(self.config.login_url)

        username_field = self.driver.find_element(By.XPATH, '//*[@id="txtUsernamePlain"]')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="txtPasswordPlain"]')
        captcha_field = self.driver.find_element(By.XPATH, '//*[@id="txtCaptcha"]')
        login_button = self.driver.find_element(By.XPATH, '//*[@id="btnEncript"]')
        sleep(3)

        username_field.send_keys('40111913299')
        password_field.send_keys('971097209')

    def solve_captcha(self):
        # Load the image using PIL
        try:
            image = Image.open(r'./Captchas/captcha.png')
            image = np.array(image)
        except IOError as e:
            print("An error occurred while trying to load the image: ", str(e))

        # Recognize the text using easyocr
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image)
        print(result)

        # Extract the number from the recognized text
        number = result[0][1]

        # Print the extracted number
        print(number)






