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
import os
import pickle


class Kalinan:
    def __init__(self):
        self.driver = self._setup_driver()
        self.config = KalinanConfig()
        self.term_no = None
        self.captcha_code = None
        self.student_name = None

    #     if os.path.exists('cookies.pkl'):
    #         self.load_cookies()
    #     else:
    #         self.save_cookies()

    # def save_cookies(self):
    #     if self.is_logged_in():
    #         with open('cookies.pkl', 'wb') as filehandler:
    #             pickle.dump(self.driver.get_cookies(), filehandler)

    # def load_cookies(self):
    #     expected_domain = self.config.dashboard_url
    #     if self.driver.current_url == expected_domain:
    #         with open('cookies.pkl', 'rb') as cookiesfile:
    #             cookies = pickle.load(cookiesfile)
    #             for cookie in cookies:
    #                 self.driver.add_cookie(cookie)
    #     else:
    #         print("Domain mismatch! Please log in to the correct domain to load cookies.")
        # self.driver.get(self.config.reserve_url)

    def _setup_driver(self):
        logging.info('Setting up driver...')
        options = Options()
        # options.add_argument(f"--no-proxy-server={excluded_url}")
        options.add_argument("--headless=new")  # run in headless mode (without gui)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        return driver

    def is_logged_in(self):
        try:
            expected_url = self.config.dashboard_url
            current_url = self.driver.current_url
            return expected_url in current_url
        except Exception as e:
            print('Not loged in: ', e)
            return False
    
    def login_to_kalinan(self, kalinan_username: str, kalinan_password: str):
        self.driver.get(self.config.login_url)

        username_field = self.driver.find_element(By.XPATH, '//*[@id="txtUsernamePlain"]')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="txtPasswordPlain"]')
        captcha_field = self.driver.find_element(By.XPATH, '//*[@id="txtCaptcha"]')
        login_button = self.driver.find_element(By.XPATH, '//*[@id="btnEncript"]')
        sleep(1)

        self.download_captcha_image()
        sleep(1)

        captcha_code = solve_captcha()
        username_field.send_keys(str(kalinan_username))
        password_field.send_keys(str(kalinan_password))         
        captcha_field.send_keys(captcha_code)
        sleep(1)

        login_button.click()
        sleep(3)
        # self.save_cookies()

    def download_captcha_image(self):
        captcha_image = self.driver.find_element(By.XPATH, '//*[@id="Img1"]')
        captcha_image.screenshot(r'C:\Users\moawezz\Desktop\Kalinan\Captchas\cap.png')
        logging.info('captcha image saved.')

    def go_to_reservation_page(self, meal: str = None):
        self.driver.get(self.config.reserve_url)
        sleep(1)

        if meal == 'ناهار':
            lunch_lable = self.driver.find_element(By.XPATH, '//*[@id="UpdatePanel1"]/div[4]/ul/li[2]/label')
            lunch_lable.click()
        if meal == 'شام':
            dinner_label = self.driver.find_element(By.XPATH, '//*[@id="cphMain_lblDinner"]')
            dinner_label.click()

    def get_meal_table_data(self, meal_table, meal):
        food_data_collection = {}
        table = self.driver.find_element(By.ID, meal_table)
        rows = table.find_elements(By.XPATH, './/tr[position() > 1]')
        meal = self.driver.find_element(By.XPATH, f'//div[contains(text(), "{meal}")]').text

        for row in rows:
            food_data = {}
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

            food_data['meal'] = meal
            food_data['checkbox'] = checkbox.is_selected()
            food_data['foods'] = foods
            food_data['status'] = status

            day_key = day
            if day_key not in food_data_collection:
                food_data_collection[day_key] = []

            food_data_collection[day_key].append(food_data)

        print(food_data_collection)

        return food_data_collection

