from pathlib import Path
from .wrapper import evaluateOnNewDocument


def chrome_runtime(driver, run_on_insecure_origins: bool = False, **kwargs) -> None:
    evaluateOnNewDocument(
        driver, Path(__file__).parent.joinpath("js/chrome.runtime.js").read_text(),
        run_on_insecure_origins,
    )
