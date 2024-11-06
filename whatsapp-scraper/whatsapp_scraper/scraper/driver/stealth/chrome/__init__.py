from .chrome_app import chrome_app
from .chrome_runtime import chrome_runtime
from .iframe_content_window import iframe_content_window
from .media_codecs import media_codecs
from .navigator_languages import navigator_languages
from .navigator_permissions import navigator_permissions
from .navigator_plugins import navigator_plugins
from .navigator_vendor import navigator_vendor
from .navigator_webdriver import navigator_webdriver
from .user_agent_override import user_agent_override
from .utils import with_utils
from .webgl_vendor import webgl_vendor_override
from .window_outerdimensions import window_outerdimensions
from .hairline_fix import hairline_fix


def apply_stealth_features(scraper_instance,
            user_agent: str = None,
            languages: [str] = ['en-US', 'en', 'es'],
            vendor: str = 'Google Inc.',
            platform: str = None,
            webgl_vendor: str = 'Intel Inc.',
            renderer: str = 'Intel Iris OpenGL Engine',
            fix_hairline: bool = False,
            run_on_insecure_origins: bool = False, **kwargs) -> None:

    with_utils(scraper_instance, **kwargs)
    chrome_app(scraper_instance, **kwargs)
    chrome_runtime(scraper_instance, run_on_insecure_origins, **kwargs)
    iframe_content_window(scraper_instance, **kwargs)
    media_codecs(scraper_instance, **kwargs)
    navigator_languages(scraper_instance, languages, **kwargs)
    navigator_permissions(scraper_instance, **kwargs)
    navigator_plugins(scraper_instance, **kwargs)
    navigator_vendor(scraper_instance, vendor, **kwargs)
    navigator_webdriver(scraper_instance, **kwargs)
    ua_languages = ','.join(languages)
    user_agent_override(scraper_instance, user_agent, ua_languages, platform, **kwargs)
    webgl_vendor_override(scraper_instance, webgl_vendor, renderer, **kwargs)
    window_outerdimensions(scraper_instance, **kwargs)

    if fix_hairline:
        hairline_fix(scraper_instance, **kwargs)
