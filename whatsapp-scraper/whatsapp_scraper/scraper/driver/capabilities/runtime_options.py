import numpy as np


class RuntimeOptions:

    SCREEN_RES_FULLSCREEN = 'fullscreen'
    SCREEN_RES_1024_768 = '1024x768'
    SCREEN_RES_1280_720 = '1280x720'
    SCREEN_RES_1280_1024 = '1280x1024'
    SCREEN_RES_1366_768 = '1366x768'
    SCREEN_RES_1440_900 = '1440x900'

    SCREEN_RESOLUTIONS = [
        (SCREEN_RES_1024_768, 0.15),
        (SCREEN_RES_1280_720, 0.15),
        (SCREEN_RES_1280_1024, 0.15),
        (SCREEN_RES_1366_768, 0.5),
        (SCREEN_RES_1440_900, 0.05),
    ]

    OPTION_SCREEN_RESOLUTION = 'screen_resolution'

    def get_random_screen_resolution(self):
        screen_resolution = np.random.choice(
            [s[0] for s in self.SCREEN_RESOLUTIONS],
            p=[s[1] for s in self.SCREEN_RESOLUTIONS]
        )
        return screen_resolution

    def get_random_options(self):
        return {
            self.OPTION_SCREEN_RESOLUTION: self.get_random_screen_resolution()
        }
