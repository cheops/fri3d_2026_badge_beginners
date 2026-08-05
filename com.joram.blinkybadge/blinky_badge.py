from mpos import Activity, LightsManager
import lvgl as lv

class BlinkyBadge(Activity):
    _slider_label = None
    _slider = None
    _hue_label = None
    _hue_slider = None
    _hue_canvas = None
    _hue_canvas_buf = None
    _leds = list(range(5, 15))
    _brightness = 51  # 0..255
    _hue = 0          # 0..65535, same range used by colorHSV()
    _show = True

    def onCreate(self):
        screen = lv.obj()
        title = lv.label(screen)
        title.set_text("SAO leds")
        title.align(lv.ALIGN.TOP_MID, 0, 30)

        on_off_label = lv.label(screen)
        on_off_label.set_text("on - off")
        on_off_label.align(lv.ALIGN.TOP_LEFT, 35, 85)
        on_off_toggle = lv.switch(screen)
        on_off_toggle.align(lv.ALIGN.TOP_RIGHT, -35, 75)
        on_off_toggle.add_state(lv.STATE.CHECKED)

        def on_off_changed(e):
            if on_off_toggle.get_state() & lv.STATE.CHECKED:
                self._show = True
            else:
                self._show = False
            self.update_leds()
        on_off_toggle.add_event_cb(on_off_changed, lv.EVENT.VALUE_CHANGED, None)

        def scale_brightness_to_percent(u8_value):
            return int(round(u8_value * 100 / 255))

        self._slider_label = lv.label(screen)
        self._slider_label.set_text("Brightness: {}%".format(scale_brightness_to_percent(self._brightness)))
        self._slider_label.align(lv.ALIGN.TOP_LEFT, 10, 120)
        self._slider = lv.slider(screen)
        self._slider.set_range(0, 255)
        self._slider.set_value(self._brightness, False)
        self._slider.set_width(140)
        self._slider.align_to(self._slider_label, lv.ALIGN.OUT_RIGHT_MID, 10, 0)

        def brightness_slider_changed(e):
            slider_value = int(self._slider.get_value())
            self._slider_label.set_text("Brightness: {}%".format(scale_brightness_to_percent(slider_value)))
            self._brightness = slider_value
            self.update_leds()
        self._slider.add_event_cb(brightness_slider_changed, lv.EVENT.VALUE_CHANGED, None)

        # --- Color (hue) slider with rainbow track ---
        self._hue_label = lv.label(screen)
        self._hue_label.set_text("Color")
        self._hue_label.align_to(self._slider_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 20)

        hue_w, hue_h = 240, 20

        # Rainbow background, drawn first so it sits behind the slider
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
        self._hue_canvas.align_to(self._hue_label, lv.ALIGN.OUT_RIGHT_MID, 20, 0)

        # Transparent slider on top of the rainbow, same size/position
        self._hue_slider = lv.slider(screen)
        self._hue_slider.set_range(0, 359)  # degrees, easier to reason about
        self._hue_slider.set_value(0, False)
        self._hue_slider.set_width(hue_w)
        self._hue_slider.set_height(hue_h)
        self._hue_slider.align_to(self._hue_label, lv.ALIGN.OUT_RIGHT_MID, 20, 0)
        self._hue_slider.set_style_bg_opa(0, lv.PART.MAIN)
        self._hue_slider.set_style_bg_opa(0, lv.PART.INDICATOR)
        self._hue_slider.set_style_radius(4, lv.PART.MAIN)

        def set_hue_from_slider():
            deg = int(self._hue_slider.get_value())
            self._hue = int(deg * 65536 / 360) % 65536
            r, g, b = self.colorHSV(self._hue, 255, 255)
            self._hue_slider.set_style_bg_color(lv.color_make(r, g, b), lv.PART.KNOB)

        def hue_slider_changed(e):
            set_hue_from_slider()
            self.update_leds()
        self._hue_slider.add_event_cb(hue_slider_changed, lv.EVENT.VALUE_CHANGED, None)
        set_hue_from_slider()  # initialize knob color to match starting hue

        self.setContentView(screen)
        LightsManager.set_led_num(15)
        self.update_leds()

    def update_leds(self):
        if self._show:
            for led in self._leds:
                LightsManager.set_led(led, *self.colorHSV(self._hue, 255, self._brightness))
        else:
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