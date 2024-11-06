from typing import Any
import json


def evaluationString(fun: str, *args: Any) -> str:
    """Convert function and arguments to str."""
    _args = ', '.join([
        json.dumps('undefined' if arg is None else arg) for arg in args
    ])
    expr = '(' + fun + ')(' + _args + ')'
    return expr


def evaluateOnNewDocument(driver, pagefunction: str, *args: str) -> None:

    js_code = evaluationString(pagefunction, *args)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": js_code,
    })
