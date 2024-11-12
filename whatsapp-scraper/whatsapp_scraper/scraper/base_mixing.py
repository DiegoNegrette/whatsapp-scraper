import logging
import json
import random
import time

from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

from .driver.capabilities.local_storage import LocalStorage
from .driver.capabilities.runtime_options import RuntimeOptions
from .driver.stealth.chrome import (
    apply_stealth_features as apply_chrome_stealth_features,
)

from ..utils import (
    create_directory,
    get_random_fingerprint_config,
    get_random_user_agent,
)

logger = logging.getLogger("scraper")


class ScraperBaseMixin:

    BROWSER_CHROME = "chrome"
    BROWSER_FIREFOX = "firefox"

    def __init__(
        self, webdriver_url=settings.WEB_DRIVER_URL, task_identifier=None, **kwargs
    ):
        self.driver = None
        self.sleep_total = 0
        self.webdriver_url = webdriver_url
        self.browser_type = settings.BROWSER
        self.webdriver_container_host = None
        self.webdriver_container_port = None
        self.account_identifier = None
        self.task_identifier = task_identifier
        self.user_data_dir = None
        self.selenium_downloads_directory = None
        self.blocked_domains = []

        # Anti bot features
        self.user_agent = None
        self.extensions_map = {}
        self.runtime_config = {
            RuntimeOptions.OPTION_SCREEN_RESOLUTION: RuntimeOptions.SCREEN_RES_FULLSCREEN
        }
        self.local_storage = None
        self.fp_config = None

    def _create_host_directory(self, directory):
        if create_directory(directory):
            self.log(f"Created directory: {directory}")
        else:
            self.log(f"Directory: {directory} already exists")

    def get_host_downloads_directory(self):
        return self.host_downloads_directory

    def get_user_agent(self):
        user_agent = get_random_user_agent()
        return user_agent

    def get_fingerprint_config(self):
        fp_config = get_random_fingerprint_config()
        return fp_config

    def get_runtime_config(self):
        runtime_options = RuntimeOptions()
        runtime_config = runtime_options.get_random_options()
        return runtime_config

    def get_default_options(self):
        options_headers = [
            "--disable-notifications",
            "--start-maximized",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        initialize_options = {
            "chrome": webdriver.ChromeOptions,
            "firefox": webdriver.FirefoxOptions,
        }
        options_headers += ["--headless"] if settings.HEADLESS else []
        OptionClass = initialize_options.get(self.browser_type)
        options = OptionClass()

        for options_header in options_headers:
            options.add_argument(options_header)

        return options

    def get_chrome_options(self, options):

        if self.user_data_dir:
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-geolocation")

        prefs = dict()

        # disable geolocation
        prefs["profile.default_content_setting_values.geolocation"] = 2

        # disable "save password?" prompt
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False

        # disable webRTC to avoid real-IP leak
        prefs["webrtc.ip_handling_policy"] = "disable_non_proxied_udp"
        prefs["webrtc.multiple_routes_enabled"] = False
        prefs["webrtc.nonproxied_udp_enabled"] = False

        # Change Language to English (Does not work for XPATH)
        # prefs['translate_whitelists'] = {'uk': 'en'}
        # prefs['translate'] = {'enabled': 'true'}
        if self.selenium_downloads_directory:
            prefs["download.default_directory"] = self.selenium_downloads_directory
            prefs["download.prompt_for_download"] = False
            prefs["download.directory_upgrade"] = False
        prefs["safebrowsing.enabled"] = False

        options.add_experimental_option("prefs", prefs)

        # some assets are not worth loading and/or take too much time to load
        if len(self.blocked_domains) > 0:
            host_resolver_rules = ", ".join(
                [f"MAP {d} 127.0.0.1" for d in self.blocked_domains]
            )
            options.add_argument(f"--host-resolver-rules={host_resolver_rules}")

        # options.add_argument("--enable-javascript")

        return options

    def get_firefox_options(self, options):
        return options

    def get_options(self):
        options = self.get_default_options()

        if self.browser_type == self.BROWSER_CHROME:
            self.get_chrome_options(options)
        elif self.browser_type == self.BROWSER_FIREFOX:
            self.get_firefox_options(options)
        else:
            raise Exception(f"Browser not supported: {self.browser_type}")

        return options

    def get_driver(self, options):
        initialize_driver = {
            "remote+firefox": webdriver.Remote,
            "remote+chrome": webdriver.Remote,
            "local+chrome": webdriver.Chrome,
        }
        eligible_capabilities = {
            "chrome": DesiredCapabilities.CHROME,
            "firefox": DesiredCapabilities.FIREFOX,
        }
        connection_options = {
            "local": settings.WEB_DRIVER_PATH,
            "remote": self.webdriver_url,
        }

        primary_identifier = f"{settings.CONNECTION_TYPE}+{self.browser_type}"

        DriverClass = initialize_driver[primary_identifier]

        desired_capabilities = eligible_capabilities[self.browser_type]

        # desired_capabilities["pageLoadStrategy"] = "none"

        return DriverClass(
            connection_options[settings.CONNECTION_TYPE],
            desired_capabilities=desired_capabilities,
            options=options,
        )

    def init_driver(self):
        self.user_agent = self.get_user_agent()
        self.fp_config = self.get_fingerprint_config()
        if "fp_protector" not in self.fp_config:
            fp_protector = random.choice([True])
            self.fp_config["fp_protector"] = fp_protector
        if "cookie_editor" not in self.fp_config:
            cookie_editor = random.choice([True])
            self.fp_config["cookie_editor"] = cookie_editor
        if "audio_def" not in self.fp_config:
            audio_def = random.choice([True, False])
            self.fp_config["audio_def"] = audio_def
        if "font_def" not in self.fp_config:
            font_def = random.choice([True, False])
            self.fp_config["font_def"] = font_def
        self.runtime_config = self.get_runtime_config()

        self.options = self.get_options()
        self.log(f"init_driver on {self.webdriver_url}")
        self.driver = self.get_driver(options=self.options)

        apply_chrome_stealth_features(
            scraper_instance=self,
            user_agent=self.user_agent,
            platform=random.choice(["Windows", "Win32"]),
        )

        self.local_storage = LocalStorage(self.driver)

    def close_driver(self):
        self.log("Closing driver")
        try:
            self.driver.quit()
            self.driver = None
        except Exception:
            pass

    def sleep(self, seconds):
        self.sleep_total += seconds
        time.sleep(seconds)

    def log(self, obj, label=None):
        _id = ""
        _label = f"[{label}]" if label else ""
        task_identifier = f"[{self.task_identifier}]" if self.task_identifier else ""
        if self.account_identifier:
            webdriver_host = self.webdriver_container_host or ""
            webdriver_port = self.webdriver_container_port or ""
            _id = (
                f"[{webdriver_host}:{webdriver_port}]"
                f"[{self.account_identifier}]{task_identifier}{_label}"
            )
        logger.info(f"{_id} {obj}")

    def navigate_to(self, target_url):
        self.log(f"Navigating to {target_url}")
        self.driver.get(target_url)

    def type_like_human(self, text: str, element=None):
        if not text:
            False
        for character in text:
            sleep_time = random.uniform(0.05, 0.2)

            if element is not None:
                element.send_keys(*character)
            else:
                actions = ActionChains(self.driver)
                if character == "\n":
                    actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(
                        Keys.SHIFT
                    ).key_up(Keys.ENTER)
                else:
                    actions.send_keys(*character)
                actions.perform()
            time.sleep(sleep_time)

    def scroll_to_element(self, element, offset_top: int = None):
        script = "return arguments[0].scrollIntoView(true);"
        if offset_top is not None:
            script += f" window.scrollBy(0, {offset_top});"
        self.driver.execute_script(script, element)
        self.sleep(0.2)

    def scroll_to_botton(self, max_scroll_times=1):

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        current_scroll = 0
        while current_scroll < max_scroll_times:
            current_scroll += 1
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            # Wait to load page
            SCROLL_PAUSE_TIME = random.uniform(0.05, 0.5)
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def scroll_to_top(self, max_scroll_times=1):
        # Initialize current scroll count
        current_scroll = 0
        while current_scroll < max_scroll_times:
            current_scroll += 1
            # Scroll up to top
            self.driver.execute_script("window.scrollTo(0, 0);")

            # Wait to load page
            SCROLL_PAUSE_TIME = random.uniform(0.05, 0.5)
            time.sleep(SCROLL_PAUSE_TIME)

            # Check if already at the top
            # This assumes the page doesn't change height while scrolling
            new_height = self.driver.execute_script("return window.pageYOffset;")
            if new_height == 0:
                break

    def _get_xpath_translate_repr(self, attribute_to_translate):
        xpath_contains = f'translate({attribute_to_translate}, "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ", "abcdefghijklmnopqrstuvwxyzáéíóú")'  # noqa
        return xpath_contains

    def xpath_translated_text(self):
        return self._get_xpath_translate_repr("text()")

    def keep_driver_alive(self):
        # caution: this works like a ping so selenium doesnt time out in given specific cases
        return self.driver.current_url

    def click_element(self, element):
        try:
            ActionChains(self.driver).move_to_element(element).perform()
            self.sleep(0.5)
            element.click()
        # except StaleElementReferenceException:
        #     self.click_element(element)
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def focus_element(self, element):
        ActionChains(self.driver).move_to_element(element).perform()

    def _load_cookies(self, cookies):
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception:
                pass

    def natural_mouse_move_and_click(self, element):
        action = ActionChains(self.driver)

        # Get element location
        element_location = element.location
        element_size = element.size

        # Calculate the target point
        target_x = element_location["x"] + element_size["width"] / 2
        target_y = element_location["y"] + element_size["height"] / 2

        # Current mouse position (initially at 0,0)
        current_x, current_y = 0, 0

        # Move in small random steps towards the target
        while current_x != target_x or current_y != target_y:
            step_x = random.randint(-5, 5)
            step_y = random.randint(-5, 5)

            # Update the current position
            if current_x < target_x:
                current_x = min(current_x + step_x, target_x)
            else:
                current_x = max(current_x + step_x, target_x)

            if current_y < target_y:
                current_y = min(current_y + step_y, target_y)
            else:
                current_y = max(current_y + step_y, target_y)

            # Perform the movement
            action.move_by_offset(step_x, step_y).perform()

            # Random sleep to simulate natural movement
            time.sleep(random.uniform(0.01, 0.05))

        # Click the element
        action.click(element).perform()

    def press_enter(self, press_down=False):
        """
        Presses enter key
        Simulates human behavior while doing it
        """
        time.sleep(random.uniform(0.5, 1))
        if press_down:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            time.sleep(random.uniform(1, 2))
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    def clear_input(self, element):
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)

    def execute_cdp_cmd(self, cmd, params={}):
        resource = (
            f"/session/{self.driver.session_id}/chromium/send_command_and_get_result"
        )
        url = self.driver.command_executor._url + resource
        body = json.dumps({"cmd": cmd, "params": params})
        response = self.driver.command_executor._request("POST", url, body)
        return response.get("value")
