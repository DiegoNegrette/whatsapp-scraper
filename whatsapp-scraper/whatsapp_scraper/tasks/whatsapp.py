import ipdb
import traceback

# from selenium import webdriver
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

from service.celery import app
from ..scraper.whatsappcom.whatsapp import WhatsappSiteScraper

queue_name = "main_queue"


@app.task(queue_name=queue_name)
def send_whatsapp_remainder():
    task_name = "send_whatsapp_remainder"
    scraper = WhatsappSiteScraper(task_identifier=task_name)
    messages = [
        {"number": "+34614216462", "message": "Test message 1"},
        {"number": "+584141882966", "message": "Test message 2"},
    ]
    try:
        scraper.init_driver()
        scraper.login()
        ipdb.set_trace()
        for message in messages:
            try:
                scraper.start_a_new_chat(user_name="Diego")
                scraper.send_message(message["number"])
                scraper.open_conversation_with_last_number()
                max_attempts = 3
                current_attempt = 1
                while current_attempt <= max_attempts:
                    scraper.log(f"Attempting to send the message ({current_attempt})")
                    try:
                        scraper.send_message(message["message"])
                        # MESSAGE SENT
                        break
                    except StaleElementReferenceException:
                        pass
                    current_attempt += 1
            except Exception as e:
                stacktrace = traceback.format_exc()
                scraper.log(stacktrace)
                scraper.log("{} Going to next message".format(e))
    except KeyboardInterrupt:
        stacktrace = "KeyboardInterrupt"
    except Exception as e:
        # ipdb.set_trace()
        stacktrace = traceback.format_exc()
        scraper.log(stacktrace)
        scraper.log("{} Terminating".format(e))

    scraper.close_driver()
