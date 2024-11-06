

def user_agent_override(
        driver,
        user_agent: str = None,
        language: str = None,
        platform: str = None,
        **kwargs
) -> None:
    if user_agent is None:
        ua = driver.execute_cdp_cmd("Browser.getVersion", {})['userAgent']
    else:
        ua = user_agent
    ua = ua.replace("HeadlessChrome", "Chrome")  # hide headless nature
    override = {}
    if language and platform:
        override = {"userAgent": ua, "acceptLanguage": language, "platform": platform}
    elif not language and platform:
        override = {"userAgent": ua, "platform": platform}
    elif language and not platform:
        override = {"userAgent": ua, "acceptLanguage": language}
    else:
        override = {"userAgent": ua}

    driver.execute_cdp_cmd('Network.setUserAgentOverride', override)
