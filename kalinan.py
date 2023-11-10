from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from kalinan_config import KalinanConfig
from PIL import Image
from time import sleep
import logging
import re
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
        self._login_to_kalinan()
        sleep(2)
        self._go_to_reservation_page()
        sleep(10)

    def _setup_driver(self):
        logging.info('Setting up driver...')
        # options = Options()
        # excluded_url = 'https://education.cfu.ac.ir/forms/authenticateuser/main.htm'
        # options.add_argument(f"--no-proxy-server={excluded_url}")
        # options.add_argument("--headless=new")  # run in headless mode (without gui)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),)

        return driver
    
    def _login_to_kalinan(self):
        self.driver.get(self.config.login_url)

        username_field = self.driver.find_element(By.XPATH, '//*[@id="txtUsernamePlain"]')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="txtPasswordPlain"]')
        captcha_field = self.driver.find_element(By.XPATH, '//*[@id="txtCaptcha"]')
        login_button = self.driver.find_element(By.XPATH, '//*[@id="btnEncript"]')
        sleep(3)

        self._download_captcha_image()
        sleep(2)

        username_field.send_keys('40111913299')
        password_field.send_keys('971097209')
        captcha_code = self._solve_captcha()
        captcha_field.send_keys(captcha_code)
        sleep(2)
        login_button.click()
        sleep(7)

    def _download_captcha_image(self):
        captcha_image = self.driver.find_element(By.XPATH, '//*[@id="Img1"]')
        captcha_image.screenshot(r'C:\Users\moawezz\Desktop\Kalinan\Captchas\cap.png')
        logging.info('captcha image saved.')

    def _solve_captcha(self):
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

    def _go_to_reservation_page(self):
        url = 'https://food1.kermancfu.ir/Reservation/Reservation.aspx'
        self.driver.get(url)
        sleep(2)

        # table_locator = (By.ID, 'cphMain_grdReservationLunch')
        # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(table_locator))
        # rows = self.driver.find_elements(By.XPATH, '//tr[@style="background-color:#EAFAEA;"]')
        # rows = self.driver.find_elements(By.XPATH, '//*[@id="cphMain_grdReservationLunch"]/tbody/tr[2]')
        
        # rows = self.driver.find_elements(By.XPATH, '//table[@id="cphMain_grdReservationLunch"]/tbody/tr')
        table = self.driver.find_element(By.ID, 'cphMain_grdReservationLunch')
        rows = table.find_elements(By.XPATH, './/tr[position() > 1]')

        for row in rows:
            checkbox = row.find_element(By.XPATH, './/input[@type="checkbox"]')
            day = row.find_element(By.XPATH, './/td[2]').text
            food_select = row.find_element(By.XPATH, './/td[4]/select')
            food_options = food_select.find_elements(By.XPATH, 'option')
            foods = [option.text for option in food_options]
            try:
                status_img = row.find_element(By.XPATH, './/td[8]/img')
                status = status_img.get_attribute('title')
            except NoSuchElementException:
                status = 'رزرو نشده'

            print("Checkbox:", checkbox.is_selected())
            print("Day:", day)
            print("Food:", foods)  # This will print a list of all options
            print("Status:", status)
            print("------------------------------")








