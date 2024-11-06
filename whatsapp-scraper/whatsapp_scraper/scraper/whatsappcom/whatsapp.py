import inspect
import ipdb

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..base_mixing import ScraperBaseMixin


def _CatchWebDriverError(func, cls):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise e

    return wrapped


class WhatsappSiteScraper(ScraperBaseMixin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.account_identifier = "whatsapp scraper"
        self.user_data_dir = "home/seluser/whatsapp/"
        self.host_user_data_dir = f"{settings.USER_DATA_DIR_BASE_FOLDER}/whatsapp/"
        self._create_host_directory(self.host_user_data_dir)
        self.webdriver_container_host = "docker-host"
        self.webdriver_container_port = None
        self.base_url = "https://web.whatsapp.com"
        self.url_to_load_cookies = "https://web.whatsapp.com/favicon/1x/favicon/"
        self.cookies = None

        self.ignore_methods = ["log", "sleep"]
        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            method_name = member[0]
            if method_name not in self.ignore_methods:
                attr = getattr(self, method_name)
                wrapped = _CatchWebDriverError(attr, self)
                setattr(self, method_name, wrapped)

    def bootstrap_account(self):
        if not self.cookies:
            return
        self.navigate_to(self.url_to_load_cookies)
        self.sleep(2)
        # self._load_cookies(self.marketplaces_manager.cookies)

    def close_driver(self):
        self.log("Closing driver")
        try:
            if self.is_logged_in():
                self.log("Saving cookies")
                # cookies = self.driver.get_cookies()
                # self.marketplaces_manager.save_cookies(cookies)
            self.driver.quit()
            self.driver = None
        except Exception:
            pass

    def is_logged_in(self):
        try:
            WebDriverWait(self.driver, timeout=10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@aria-label='Search or start new chat']")
                )
            )
            return True
        except Exception:
            return False

    def login(self):
        self.bootstrap_account()
        self.navigate_to(self.base_url)
        if not self.is_logged_in():
            raise Exception("Error al iniciar sesión")
        # self.marketplaces_manager.save_cookies([])

    def start_a_new_chat(self, user_name):
        search_btn = WebDriverWait(self.driver, timeout=10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Search or start new chat']")
            )
        )
        self.click_element(search_btn)
        self.type_like_human(user_name)
        self.press_enter()

    def send_message(self, message):
        message_box = WebDriverWait(self.driver, timeout=10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@aria-placeholder='Type a message']")
            )
        )
        self.click_element(message_box)
        self.type_like_human(message)
        self.press_enter()

    def get_last_message_element(self):
        out_messages = WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[contains(@class, 'message-out')]/descendant::a")
            )
        )
        return out_messages[len(out_messages) - 1]

    def open_conversation_with_last_number(self):
        last_message_element = self.get_last_message_element()
        self.click_element(last_message_element)
        open_new_chat_btn = WebDriverWait(self.driver, timeout=10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@aria-label, 'Chat with')]")
            )
        )
        self.click_element(open_new_chat_btn)
