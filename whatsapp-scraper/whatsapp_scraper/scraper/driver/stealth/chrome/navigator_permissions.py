from pathlib import Path
from .wrapper import evaluateOnNewDocument


def navigator_permissions(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/navigator.permissions.js").read_text()
    )
