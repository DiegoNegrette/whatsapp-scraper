from pathlib import Path
from .wrapper import evaluateOnNewDocument


def media_codecs(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/media.codecs.js").read_text()
    )
