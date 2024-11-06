from pathlib import Path
from .wrapper import evaluateOnNewDocument


def chrome_app(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/chrome.app.js").read_text()
    )
