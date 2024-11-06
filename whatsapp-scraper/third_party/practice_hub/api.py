import datetime
import logging

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger("scraper")


class PracticeHubAPI:

    def __init__(self):
        self.account_domain = settings.PRACTICE_HUB_ACCOUNT_DOMAIN
        self.BASE_URL = "https://{account_domain}.neptune.practicehub.io/api/{endpoint}"
        # self.headers = {"Authorization": f"Token {settings.PRACTICE_HUB_API_KEY}"}
        self.headers = {
            "x-practicehub-key": f"{settings.PRACTICE_HUB_API_KEY}",
            "x-app-details": f"whatsapp_scraper={settings.PRACTICE_HUB_CONTACT_EMAIL}",
        }
        self.timeout = 240
        self.max_retries = 5

        self.api_map = {
            "get_todays_appointments": {
                "url_info": {
                    "account_domain": self.account_domain,
                    "endpoint": "appointments",
                },
                "params": {},
            },
            "get_patients": {
                "url_info": {
                    "account_domain": self.account_domain,
                    "endpoint": "patients",
                },
                "params": {},
            },
        }

    def log_info(self, obj):
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{now}] {obj}")

    def log_error(self, obj):
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"[{now}] {obj}")

    def _validate_parameters(self, data, expected_keys):
        if not all(param in data for param in expected_keys):
            _expected_params = ", ".join(expected_keys)
            raise Exception(f"Must specify these params: {_expected_params}")

    def get_todays_appointments(self):
        cmd = "get_todays_appointments"
        url = self.BASE_URL.format(**self.api_map[cmd]["url_info"])
        # 2024-11-05
        today = timezone.now().strftime("yyyy-mm-dd")
        filters = f"?start=gte:{today}"
        url += filters
        # self.log_info(
        #     f"[{cmd}] Requesting calls for phonenumber: {customer_phone_number}"
        # )
        # end_date = timezone.now()
        # start_date = end_date - datetime.timedelta(days=365)
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        response = r.json()
        if r.status_code == 200 and response.get("data", None):
            return response["data"]
        return []

    def get_patients(self):
        cmd = "get_patients"
        url = self.BASE_URL.format(**self.api_map[cmd]["url_info"])
        # self.log_info(
        #     f"[{cmd}] Requesting calls for phonenumber: {customer_phone_number}"
        # )
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        response = r.json()
        if r.status_code == 200 and response.get("data", None):
            return response["data"]
        return []
