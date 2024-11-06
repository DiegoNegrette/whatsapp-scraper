from pathlib import Path
from .wrapper import evaluateOnNewDocument


def navigator_plugins(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/navigator.plugins.js").read_text()
    )
