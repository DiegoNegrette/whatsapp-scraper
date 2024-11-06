from pathlib import Path
from .wrapper import evaluateOnNewDocument


def window_outerdimensions(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/window.outerdimensions.js").read_text()
    )
