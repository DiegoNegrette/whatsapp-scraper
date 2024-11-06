from pathlib import Path
from .wrapper import evaluateOnNewDocument


def navigator_webdriver(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/navigator.webdriver.js").read_text()
    )
