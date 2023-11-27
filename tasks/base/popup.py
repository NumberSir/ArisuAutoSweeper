from module.base.base import ModuleBase
from module.base.timer import Timer
from tasks.base.assets.assets_base_popup import *
from tasks.base.assets.assets_base_page import LOADING_CHECK


class PopupHandler(ModuleBase):
    def handle_loading(self) -> bool:
        """
        Args:
            interval:

        Returns:
            If handled.
        """
        if not self.appear(LOADING_CHECK):
            return False
        
        timer = Timer(0.5).start()
        while 1:
            if not timer.reached_and_reset():
                continue
                
            self.device.screenshot()
            if not self.appear(LOADING_CHECK):
                break
                
            self.device.stuck_record_clear()
        return True

    def handle_reward(self) -> bool:
        """
        Args:
            interval:

        Returns:
            If handled.
        """
        if not any([
            self.appear(GET_REWARD),
            self.match_color(GET_REWARD, threshold=30)
        ]):
            return False

        while 1:
            self.device.screenshot()
            if not any([
                self.appear(GET_REWARD),
                self.match_color(GET_REWARD, threshold=30)
            ]):
                break
            self.click_with_interval(GET_REWARD, interval=0.5)
        return True

    def handle_reward_skip(self, interval=5) -> bool:
        if self.appear_then_click(GET_REWARD_SKIP, interval=interval):
            return True

    def handle_daily_news(self, interval=2) -> bool:
        return self.appear_then_click(DAILY_NEWS, interval=interval)

    def handle_daily_reward(self, interval=2) -> bool:
        return self.appear_then_click(DAILY_REWARD, interval=interval)

    def handle_network_reconnect(self, interval=5) -> bool:
        return any([
            self.appear_then_click(NETWORK_RECONNECT, interval=interval),
            self.appear_then_click(NETWORK_RECONNECT_OK, interval=interval)
        ])

    def handle_affection_level_up(self) -> bool:
        if not self.appear_then_click(AFFECTION_LEVEL_UP):
            return False
        while 1:
            self.device.screenshot()
            if not self.appear(AFFECTION_LEVEL_UP):
                break
            self.click_with_interval(AFFECTION_LEVEL_UP, interval=1)
        return True

    def handle_new_student(self, interval=5) -> bool:
        return bool(self.appear_then_click(GET_NEW_STUDENT, interval=interval))

    def handle_ap_exceed(self, interval=5) -> bool:
        return bool(self.appear_then_click(AP_EXCEED, interval=interval))

    def handle_insufficient_inventory(self, interval=5) -> bool:
        return bool(self.appear_then_click(INSUFFICIENT_INVENTORY, interval=interval))

    def handle_item_expired(self, interval=5) -> bool:
        return bool(self.appear_then_click(ITEM_EXPIRED, interval=interval))
