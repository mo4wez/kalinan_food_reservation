from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from config.kalinan_config import KalinanConfig
from captcha_solver.cap_solver import solve_captcha
from time import sleep
import logging


class Kalinan:
    def __init__(self):
        self.config = KalinanConfig()
        self.driver = self._setup_driver()
        self.term_no = None
        self.captcha_code = None
        self.student_name = None

    def run(self):
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        sleep(3)
        self.login_to_kalinan()
        sleep(2)
        self.go_to_reservation_page()
        sleep(10)

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

        self.download_captcha_image()
        sleep(2)

        captcha_code = solve_captcha()
        username_field.send_keys('40111913299')
        password_field.send_keys('971097209')         
        captcha_field.send_keys(captcha_code)
        sleep(2)

        login_button.click()
        sleep(7)

    def download_captcha_image(self):
        captcha_image = self.driver.find_element(By.XPATH, '//*[@id="Img1"]')
        captcha_image.screenshot(r'C:\Users\moawezz\Desktop\Kalinan\Captchas\cap.png')
        logging.info('captcha image saved.')

    def go_to_reservation_page(self):
        self.driver.get(self.config.reserve_url)
        sleep(2)

        lunch = 'ناهار'
        dinner = 'شام'
        food_type = input('Enter food type: ')

        if food_type == lunch:
            self.get_meal_table_data(meal_table='cphMain_grdReservationLunch', meal=lunch)
        if food_type == dinner:
            dinner_label = self.driver.find_element(By.XPATH, '//*[@id="cphMain_lblDinner"]')
            sleep(2)
            dinner_label.click()
            sleep(2)
            self.get_meal_table_data(meal_table='cphMain_grdReservationDinner', meal=dinner)


    def get_meal_table_data(self, meal_table, meal):
        food_data = {}
        table = self.driver.find_element(By.ID, meal_table)
        rows = table.find_elements(By.XPATH, './/tr[position() > 1]')
        meal = self.driver.find_element(By.XPATH, f'//div[contains(text(), "{meal}")]').text

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

            print('Meal:', meal)
            print("Checkbox:", checkbox.is_selected())
            print("Day:", day)
            print("Food:", foods)  # This will print a list of all options
            print("Status:", status)
            print("------------------------------")

            food_data['meal'] = meal
            food_data['checkbox'] = checkbox.is_selected()
            food_data['day'] = day
            food_data['foods'] = foods
            food_data['status'] = status

        return food_data

