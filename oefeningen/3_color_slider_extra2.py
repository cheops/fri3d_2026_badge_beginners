from mpos import Activity, LightsManager
import lvgl as lv

class Main(Activity):
    _slider_value = 255
    _hue = 0

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

        hue_w, hue_h = 250, 16

        self._hue_canvas_buf = bytearray(hue_w * hue_h * 2)  # RGB565 = 2 bytes/px
        self._hue_canvas = lv.canvas(screen)
        self._hue_canvas.set_buffer(self._hue_canvas_buf, hue_w, hue_h, lv.COLOR_FORMAT.RGB565)
        for x in range(hue_w):
            hue16 = int(65536 * x / hue_w)
            r, g, b = self.colorHSV(hue16, 255, 255)  # full sat/val for a vivid rainbow
            color = lv.color_make(r, g, b)
            for y in range(hue_h):
                self._hue_canvas.set_px(x, y, color, 255)
        self._hue_canvas.set_style_radius(4, 0)
        self._hue_canvas.set_style_clip_corner(True, 0)
        self._hue_canvas.align_to(slider, lv.ALIGN.OUT_BOTTOM_MID, 0, 20)
        
        hue_slider = lv.slider(screen)
        hue_slider.set_range(0, 359)
        hue_slider.set_style_bg_opa(0, lv.PART.MAIN)
        hue_slider.set_style_bg_opa(0, lv.PART.INDICATOR)
        hue_slider.set_style_radius(4, lv.PART.MAIN)
        hue_slider.align_to(slider, lv.ALIGN.OUT_BOTTOM_MID, 0, 20)

        def set_hue_from_slider():
            deg = int(hue_slider.get_value())
            self._hue = int(deg * 65536 / 360) % 65536
            r, g, b = self.colorHSV(self._hue, 255, 255)
            hue_slider.set_style_bg_color(lv.color_make(r, g, b), lv.PART.KNOB)

        def hue_changed(e):
            set_hue_from_slider()
            self.update_leds()
        hue_slider.add_event_cb(hue_changed, lv.EVENT.VALUE_CHANGED, None)

        set_hue_from_slider()  # Set initial color of the hue slider knob


        LightsManager.set_led_num(15)
        self.update_leds()

        self.setContentView(screen)  # has to be last line

    def update_leds(self):
        r, g, b = self.colorHSV(self._hue, 255, self._slider_value)
        LightsManager.set_all(r, g, b)
        LightsManager.write()
        
    def onPause(self, screen):
        LightsManager.clear()
        LightsManager.write()

    def colorHSV(self, hue, sat, val):
        """
        Converts HSV color to rgb tuple and returns it.
        The logic is almost the same as in Adafruit NeoPixel library:
        https://github.com/adafruit/Adafruit_NeoPixel so all the credits for that
        go directly to them (license: https://github.com/adafruit/Adafruit_NeoPixel/blob/master/COPYING)
        :param hue: Hue component. Should be on interval 0..65535
        :param sat: Saturation component. Should be on interval 0..255
        :param val: Value component. Should be on interval 0..255
        :return: (r, g, b) tuple
        """
        if hue >= 65536:
            hue %= 65536
        hue = (hue * 1530 + 32768) // 65536
        if hue < 510:
            b = 0
            if hue < 255:
                r = 255
                g = hue
            else:
                r = 510 - hue
                g = 255
        elif hue < 1020:
            r = 0
            if hue < 765:
                g = 255
                b = hue - 510
            else:
                g = 1020 - hue
                b = 255
        elif hue < 1530:
            g = 0
            if hue < 1275:
                r = hue - 1020
                b = 255
            else:
                r = 255
                b = 1530 - hue
        else:
            r = 255
            g = 0
            b = 0
        v1 = 1 + val
        s1 = 1 + sat
        s2 = 255 - sat
        r = ((((r * s1) >> 8) + s2) * v1) >> 8
        g = ((((g * s1) >> 8) + s2) * v1) >> 8
        b = ((((b * s1) >> 8) + s2) * v1) >> 8
        return r, g, b


a = Main()
a.onCreate()
