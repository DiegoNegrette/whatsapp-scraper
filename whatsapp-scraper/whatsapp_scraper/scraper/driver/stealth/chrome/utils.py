from pathlib import Path
from .wrapper import evaluateOnNewDocument


def with_utils(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/utils.js").read_text()
    )
