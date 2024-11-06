from pathlib import Path
from .wrapper import evaluateOnNewDocument


def navigator_languages(driver, languages: [str], **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/navigator.languages.js").read_text(),
        languages,
    )
