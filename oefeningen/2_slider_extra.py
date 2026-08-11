from mpos import Activity, LightsManager
import lvgl as lv

class Main(Activity):
    _slider_value = 255
    _checkbox_value = True

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

        checkbox = lv.checkbox(screen)
        checkbox.set_text("Enable LEDs")
        checkbox.add_state(lv.STATE.CHECKED if self._checkbox_value else lv.STATE.DEFAULT)
        checkbox.align(lv.ALIGN.BOTTOM_MID, 0, -30)
        def checkbox_changed(e):
            self._checkbox_value = bool(checkbox.get_state() & lv.STATE.CHECKED)
            self.update_leds()
        checkbox.add_event_cb(checkbox_changed, lv.EVENT.VALUE_CHANGED, None)

        LightsManager.set_led_num(15)
        self.update_leds()

        self.setContentView(screen)  # has to be last line

    def update_leds(self):
        if self._checkbox_value:
            LightsManager.set_all(self._slider_value, 0, 128)
        else:
            LightsManager.clear()
        LightsManager.write()

    def onPause(self, screen):
        LightsManager.clear()
        LightsManager.write()


a = Main()
a.onCreate()
