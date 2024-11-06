from pathlib import Path
from .wrapper import evaluateOnNewDocument


def navigator_vendor(driver, vendor: str, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/navigator.vendor.js").read_text(), vendor
    )
