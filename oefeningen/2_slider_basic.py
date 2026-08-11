from mpos import Activity, LightsManager
import lvgl as lv

class Main(Activity):
    _slider_value = 255

    def onCreate(self):
        screen = lv.obj()

        label = lv.label(screen)
        label.set_text("Press X to quit")
        label.align(lv.ALIGN.TOP_MID, 0, 30)

        slider = lv.slider(screen)
        slider.set_range(0, 255)
        slider.set_value(self._slider_value, False)
        slider.align(lv.ALIGN.CENTER, 0, 0)

        def slider_changed(e):
            self._slider_value = slider.get_value()
            self.update_leds()
        slider.add_event_cb(slider_changed, lv.EVENT.VALUE_CHANGED, None)

        LightsManager.set_led_num(15)
        self.update_leds()

        self.setContentView(screen)  # has to be last line

    def update_leds(self):
        LightsManager.set_all(self._slider_value, 0, 128)
        LightsManager.write()

    def onPause(self, screen):
        LightsManager.clear()
        LightsManager.write()


a = Main()
a.onCreate()
