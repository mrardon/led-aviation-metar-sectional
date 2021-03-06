from threading import Thread, Condition
from sectional.models import Configuration
from sectional.models import Color
import logging


class SelfTestThread(Thread):
    def __init__(self, sectional):
        Thread.__init__(self, name="SelfTestThread")
        self.logger = logging.getLogger(__name__)
        self.sectional = sectional
        self.running = True
        self.condition = Condition()

    def shutdown(self):
        self.condition.acquire()
        self.running = False
        self.condition.notify()
        self.condition.release()

    def run(self):
        self.logger.info("self test thread is now complete.")
        for color in Color.ALL_COLORS():

            if (self.running is False):
                break

            self.condition.acquire()
            [self.sectional.renderer.set_led(x, color) for x in range(self.sectional.configuration.pixelcount)]
            self.condition.wait(timeout=1)

        self.logger.info("self test thread is now complete.")
