from module.base.button import ClickButton
from module.base.decorator import cached_property
from module.base.timer import Timer
from module.base.utils import *
from module.device.method.hermit import Hermit
from module.device.method.maatouch import MaaTouch
from module.device.method.minitouch import Minitouch
from module.device.method.scrcpy import Scrcpy
from module.logger import logger

import numpy as np


class Control(Hermit, Minitouch, Scrcpy, MaaTouch):
    def handle_control_check(self, button):
        # Will be overridden in Device
        pass

    @cached_property
    def click_methods(self):
        return {
            'ADB': self.click_adb,
            'uiautomator2': self.click_uiautomator2,
            'minitouch': self.click_minitouch,
            'Hermit': self.click_hermit,
            'MaaTouch': self.click_maatouch,
        }

    def click(self, button, control_check=True):
        """Method to click a button.

        Args:
            button (button.Button): AzurLane Button instance.
            control_check (bool):
        """
        if control_check:
            self.handle_control_check(button)
        x, y = random_rectangle_point(button.button)
        x, y = ensure_int(x, y)
        logger.info(f'Click {point2str(x, y)} @ {button}')
        method = self.click_methods.get(
            self.config.Emulator_ControlMethod,
            self.click_adb
        )
        method(x, y)

    def multi_click(self, button, n, interval=(0.1, 0.2)):
        self.handle_control_check(button)
        click_timer = Timer(0.1)
        for _ in range(n):
            remain = ensure_time(interval) - click_timer.current()
            if remain > 0:
                self.sleep(remain)
            click_timer.reset()

            self.click(button, control_check=False)

    def long_click(self, button, duration=(1, 1.2)):
        """Method to long click a button.

        Args:
            button (button.Button): AzurLane Button instance.
            duration(int, float, tuple):
        """
        self.handle_control_check(button)
        x, y = random_rectangle_point(button.button)
        x, y = ensure_int(x, y)
        duration = ensure_time(duration)
        logger.info(f'Click {point2str(x, y)} @ {button}, {duration}')
        method = self.config.Emulator_ControlMethod
        if method == 'MaaTouch':
            self.long_click_maatouch(x, y, duration)
        elif method == 'minitouch':
            self.long_click_minitouch(x, y, duration)
        elif method == 'scrcpy':
            self.long_click_scrcpy(x, y, duration)
        elif method == 'uiautomator2':
            self.long_click_uiautomator2(x, y, duration)
        else:
            self.swipe_adb((x, y), (x, y), duration)

    def swipe(self, p1, p2, duration=(0.1, 0.2), name='SWIPE', distance_check=True):
        self.handle_control_check(name)
        p1, p2 = ensure_int(p1, p2)
        duration = ensure_time(duration)
        method = self.config.Emulator_ControlMethod
        if method in ['minitouch', 'scrcpy', 'MaaTouch']:
            logger.info(f'Swipe {point2str(*p1)} -> {point2str(*p2)}')
        elif method == 'uiautomator2':
            logger.info(f'Swipe {point2str(*p1)} -> {point2str(*p2)}, {duration}')
        else:
            # ADB needs to be slow, or swipe doesn't work
            duration *= 2.5
            logger.info(f'Swipe {point2str(*p1)} -> {point2str(*p2)}, {duration}')

        if distance_check:
            if np.linalg.norm(np.subtract(p1, p2)) < 10:
                # Should swipe a certain distance, otherwise AL will treat it as click.
                # uiautomator2 should >= 6px, minitouch should >= 5px
                logger.info('Swipe distance < 10px, dropped')
                return

        if method == 'MaaTouch':
            self.swipe_maatouch(p1, p2)
        elif method == 'minitouch':
            self.swipe_minitouch(p1, p2)
        elif method == 'scrcpy':
            self.swipe_scrcpy(p1, p2)
        elif method == 'uiautomator2':
            self.swipe_uiautomator2(p1, p2, duration=duration)
        else:
            self.swipe_adb(p1, p2, duration=duration)

    def swipe_vector(self, vector, box=(123, 159, 1175, 628), random_range=(0, 0, 0, 0), padding=15,
                     duration=(0.1, 0.2), whitelist_area=None, blacklist_area=None, name='SWIPE', distance_check=True):
        """Method to swipe.

        Args:
            box (tuple): Swipe in box (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
            vector (tuple): (x, y).
            random_range (tuple): (x_min, y_min, x_max, y_max).
            padding (int):
            duration (int, float, tuple):
            whitelist_area: (list[tuple[int]]):
                A list of area that safe to click. Swipe path will end there.
            blacklist_area: (list[tuple[int]]):
                If none of the whitelist_area satisfies current vector, blacklist_area will be used.
                Delete random path that ends in any blacklist_area.
            name (str): Swipe name
            distance_check: (bool):
        """
        p1, p2 = random_rectangle_vector_opted(
            vector,
            box=box,
            random_range=random_range,
            padding=padding,
            whitelist_area=whitelist_area,
            blacklist_area=blacklist_area
        )
        self.swipe(p1, p2, duration=duration, name=name, distance_check=distance_check)

    def drag(self, p1, p2, segments=1, shake=(0, 15), point_random=(-10, -10, 10, 10), shake_random=(-5, -5, 5, 5),
             swipe_duration=0.25, shake_duration=0.1, name='DRAG'):
        self.handle_control_check(name)
        p1, p2 = ensure_int(p1, p2)
        logger.info(f'Drag {point2str(*p1)} -> {point2str(*p2)}')
        method = self.config.Emulator_ControlMethod
        if method == 'minitouch':
            self.drag_minitouch(p1, p2, point_random=point_random)
        elif method == 'uiautomator2':
            self.drag_uiautomator2(
                p1, p2, segments=segments, shake=shake, point_random=point_random, shake_random=shake_random,
                swipe_duration=swipe_duration, shake_duration=shake_duration)
        elif method == 'scrcpy':
            self.drag_scrcpy(p1, p2, point_random=point_random)
        elif method == 'MaaTouch':
            self.drag_maatouch(p1, p2, point_random=point_random)
        else:
            logger.warning(f'Control method {method} does not support drag well, '
                           f'falling back to ADB swipe may cause unexpected behaviour')
            self.swipe_adb(p1, p2, duration=ensure_time(swipe_duration * 2))
            self.click(ClickButton(button=area_offset(point_random, p2), name=name))

    # just used in cafe
    def pinch(self, box=(35, 130, 1250, 560), name='PINCH'):
        self.handle_control_check(name)
        middle_point = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
        width = box[2] - middle_point[0]
        height = box[3] - middle_point[1]
        box_0 = (middle_point[0], box[1], box[2], middle_point[1])
        box_1 = (box[0], middle_point[1], middle_point[0], box[3])
        r = np.random.uniform(0.8, 0.9)
        vector_0 = (-width * r, height * r)
        vector_1 = (width * r, -height * r)
        p1_1, p1_2 = random_rectangle_vector_opted(
            vector_0,
            box=box_0,
            random_range=(-5, -5, 5, 5),
            padding=5,
            whitelist_area=None,
            blacklist_area=None
        )
        p2_1, p2_2 = random_rectangle_vector_opted(
            vector_1,
            box=box_1,
            random_range=(-5, -5, 5, 5),
            padding=5,
            whitelist_area=None,
            blacklist_area=None
        )
        logger.info('Pinch')
        method = self.config.Emulator_ControlMethod
        if method == 'MaaTouch':
            self.pinch_maatouch(p1_1, p1_2, p2_1, p2_2)
        else:
            logger.warning(f'Control method {method} does not support pinch well')
            return
