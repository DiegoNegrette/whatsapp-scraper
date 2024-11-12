from datetime import datetime
import os
import pytz
import stat
import random
import numpy as np

from django.utils import timezone


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chmod(directory, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        return True
    return False


def get_random_user_agent(operating_system=None):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.",
        "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36 Avast/109.0.24252.12",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.",
    ]
    available_user_agents = len(user_agents)
    random_index = random.randint(0, available_user_agents - 1)
    return user_agents[random_index]


def get_random_fingerprint_config(seed=None):
    webgl_def = bool(np.random.choice([True, False], p=[1, 0]))
    fp_def = bool(np.random.choice([True, False], p=[1, 0]))
    # fp_protector = bool(np.random.choice([True, False], p=[1, 0]))
    fp_spoof = bool(np.random.choice([True, False], p=[0, 1]))
    audio_def = bool(np.random.choice([True, False], p=[0.15, 0.85]))
    font_def = bool(np.random.choice([True, False], p=[0.15, 0.85]))
    geolocation = str(np.random.choice(["enable", "disable"], p=[0.70, 0.30]))
    return {
        "webgl_def": webgl_def,
        "fp_def": fp_def,
        "fp_spoof": fp_spoof,
        "audio_def": audio_def,
        "font_def": font_def,
        "geolocation": geolocation,
        "seed": seed,
        # 'fp_protector': fp_protector,
    }


def convert_datetime_str_to_aware(date_str, date_format):
    # Parse the string into a naive datetime (no timezone)
    naive_appointment_date = datetime.strptime(date_str, date_format)
    # Make the datetime timezone-aware by associating it with the Spain timezone
    appointment_date_spain = timezone.make_aware(
        naive_appointment_date, pytz.timezone("Europe/Madrid")
    )

    return appointment_date_spain
