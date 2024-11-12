import logging

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger("practice_hub")


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

    def _validate_parameters(self, data, expected_keys):
        if not all(param in data for param in expected_keys):
            _expected_params = ", ".join(expected_keys)
            raise Exception(f"Must specify these params: {_expected_params}")

    def get_future_appointments(self, page):
        cmd = "get_todays_appointments"
        url = self.BASE_URL.format(**self.api_map[cmd]["url_info"])
        # 2024-11-05
        today = timezone.now().strftime("%Y-%m-%d")
        filters = [f"start=gte:{today}", f"page={page}"]
        url_filters = "&".join(filters)
        url = f"{url}?{url_filters}"
        logger.info(f"[{cmd}] Requesting appointments from: {url}")
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        return r

    def get_patients(self, page):
        cmd = "get_patients"
        url = self.BASE_URL.format(**self.api_map[cmd]["url_info"])
        filters = [f"page={page}"]
        url_filters = "&".join(filters)
        url = f"{url}?{url_filters}"
        logger.info(f"[{cmd}] Requesting patients from: {url}")
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        return r
