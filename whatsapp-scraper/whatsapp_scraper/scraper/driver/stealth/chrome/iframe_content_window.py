from pathlib import Path
from .wrapper import evaluateOnNewDocument


def iframe_content_window(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/iframe.contentWindow.js").read_text()
    )
