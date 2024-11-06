from pathlib import Path
from .wrapper import evaluateOnNewDocument


def hairline_fix(driver, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/hairline.fix.js").read_text()
    )
