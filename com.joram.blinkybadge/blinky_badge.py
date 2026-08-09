from mpos import Activity, LightsManager
import mpos.ui
import lvgl as lv
import time
import math

class BlinkyBadge(Activity):
    _slider_label = None
    _slider = None
    _hue_label = None
    _hue_slider = None
    _hue_canvas = None
    _hue_canvas_buf = None
    _sao_spinbox = None
    _anim_buttons = None
    _anim_style_selected = None

    _badge_leds = list(range(0, 5))
    _sao_count = 8
    _brightness = 51  # 0..255
    _hue = 0          # 0..65535, same range used by colorHSV()
    _badge_show = True
    _sao_show = True
    _active_leds = []

    # Animation modes, ordered from simplest to most complex for the workshop.
    # "blink" and "chase" are ONE-SHOT: they play once and revert to "static".
    # "pulse" and "rainbow" loop continuously until another button is pressed.
    _mode = "static"       # static | blink | chase | pulse | rainbow
    _anim_active = False
    _last_time = 0
    _blink_state = True
    _blink_count = 0
    _blink_max = 6         # 3 full on/off cycles, then done
    _chase_index = -1
    _pulse_phase = 0.0
    _rainbow_hue = 0.0

    UPDATE_INTERVAL = 0.05  # 20 Hz

    def onCreate(self):
        screen = lv.obj()
        screen.set_style_pad_all(0, 0)
        screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        screen.remove_flag(lv.obj.FLAG.SCROLLABLE)

        title = lv.label(screen)
        title.set_text("SAO leds")
        title.align(lv.ALIGN.TOP_MID, 0, 4)

        # --- Row 1: Badge leds checkbox / SAO leds checkbox ---
        badge_checkbox = lv.checkbox(screen)
        badge_checkbox.set_text("Badge leds")
        badge_checkbox.add_state(lv.STATE.CHECKED)
        badge_checkbox.align(lv.ALIGN.TOP_LEFT, 10, 26)

        def badge_checkbox_changed(e):
            self._badge_show = bool(badge_checkbox.get_state() & lv.STATE.CHECKED)
            self.recompute_active_leds()
            self.update_leds()
        badge_checkbox.add_event_cb(badge_checkbox_changed, lv.EVENT.VALUE_CHANGED, None)

        sao_checkbox = lv.checkbox(screen)
        sao_checkbox.set_text("SAO leds")
        sao_checkbox.add_state(lv.STATE.CHECKED)
        sao_checkbox.align(lv.ALIGN.TOP_LEFT, 170, 26)

        def sao_checkbox_changed(e):
            self._sao_show = bool(sao_checkbox.get_state() & lv.STATE.CHECKED)
            self.recompute_active_leds()
            self.update_leds()
        sao_checkbox.add_event_cb(sao_checkbox_changed, lv.EVENT.VALUE_CHANGED, None)

        # --- Row 2: SAO count spinbox with +/- buttons, under "SAO leds" ---
        sao_minus_btn = lv.button(screen)
        sao_minus_btn.set_size(26, 26)
        sao_minus_btn.align(lv.ALIGN.TOP_LEFT, 170, 52)
        minus_label = lv.label(sao_minus_btn)
        minus_label.set_text("-")
        minus_label.center()

        self._sao_spinbox = lv.spinbox(screen)
        self._sao_spinbox.set_range(0, 100)
        self._sao_spinbox.set_digit_format(3, 0)
        self._sao_spinbox.set_value(self._sao_count)
        self._sao_spinbox.set_width(50)
        self._sao_spinbox.align(lv.ALIGN.TOP_LEFT, 201, 52)

        sao_plus_btn = lv.button(screen)
        sao_plus_btn.set_size(26, 26)
        sao_plus_btn.align(lv.ALIGN.TOP_LEFT, 256, 52)
        plus_label = lv.label(sao_plus_btn)
        plus_label.set_text("+")
        plus_label.center()

        def sao_count_changed():
            self._sao_count = int(self._sao_spinbox.get_value())
            new_led_num = len(self._badge_leds) + self._sao_count
            current_led_num = LightsManager.get_led_count()
            if current_led_num > new_led_num:
                for led in range(new_led_num, current_led_num):
                    LightsManager.set_led(led, 0, 0, 0)
                LightsManager.write()
            LightsManager.set_led_num(new_led_num)
            self.recompute_active_leds()
            self.update_leds()

        def sao_minus_clicked(e):
            self._sao_spinbox.decrement()
            sao_count_changed()
        sao_minus_btn.add_event_cb(sao_minus_clicked, lv.EVENT.CLICKED, None)

        def sao_plus_clicked(e):
            self._sao_spinbox.increment()
            sao_count_changed()
        sao_plus_btn.add_event_cb(sao_plus_clicked, lv.EVENT.CLICKED, None)

        def sao_spinbox_value_changed(e):
            sao_count_changed()
        self._sao_spinbox.add_event_cb(sao_spinbox_value_changed, lv.EVENT.VALUE_CHANGED, None)

        def scale_brightness_to_percent(u8_value):
            return int(round(u8_value * 100 / 255))

        # --- Row 3: Brightness slider ---
        self._slider_label = lv.label(screen)
        self._slider_label.set_text("Brightness: {}%".format(scale_brightness_to_percent(self._brightness)))
        self._slider_label.align(lv.ALIGN.TOP_LEFT, 10, 90)
        self._slider = lv.slider(screen)
        self._slider.set_range(0, 255)
        self._slider.set_value(self._brightness, False)
        self._slider.set_width(150)
        self._slider.align(lv.ALIGN.TOP_LEFT, 150, 88)

        def brightness_slider_changed(e):
            slider_value = int(self._slider.get_value())
            self._slider_label.set_text("Brightness: {}%".format(scale_brightness_to_percent(slider_value)))
            self._brightness = slider_value
            self.update_leds()
        self._slider.add_event_cb(brightness_slider_changed, lv.EVENT.VALUE_CHANGED, None)

        # --- Row 4: Color (hue) slider with rainbow track ---
        self._hue_label = lv.label(screen)
        self._hue_label.set_text("Color")
        self._hue_label.align(lv.ALIGN.TOP_LEFT, 10, 118)

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
        self._hue_canvas.align(lv.ALIGN.TOP_LEFT, 60, 116)

        self._hue_slider = lv.slider(screen)
        self._hue_slider.set_range(0, 359)  # degrees, easier to reason about
        self._hue_slider.set_value(0, False)
        self._hue_slider.set_width(hue_w)
        self._hue_slider.set_height(hue_h)
        self._hue_slider.align(lv.ALIGN.TOP_LEFT, 60, 116)
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

        # --- Row 5: Animation pattern buttons, simple -> complex, left to right ---
        self._anim_style_selected = lv.style_t()
        self._anim_style_selected.init()
        self._anim_style_selected.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))

        anim_row = lv.obj(screen)
        anim_row.set_size(300, 34)
        anim_row.align(lv.ALIGN.TOP_LEFT, 10, 150)
        anim_row.set_style_pad_all(0, 0)
        anim_row.set_style_border_width(0, 0)
        anim_row.set_style_bg_opa(0, 0)
        anim_row.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        anim_row.remove_flag(lv.obj.FLAG.SCROLLABLE)
        anim_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        anim_row.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        # Ordered simplest -> most complex, for teaching purposes.
        # "Blink" and "Chase" are one-shot (play once, then back to Static) -
        # much easier for beginners than a forever-looping effect.
        anim_defs = [
            ("Static", "static"),
            ("Blink", "blink"),
            ("Chase", "chase"),
            ("Pulse", "pulse"),
            ("Rainbow", "rainbow"),
        ]
        self._anim_buttons = []

        def make_anim_click_handler(mode, btn):
            def handler(e):
                self.select_animation(mode, btn)
            return handler

        for text, mode in anim_defs:
            btn = lv.button(anim_row)
            btn.set_size(54, 32)
            label = lv.label(btn)
            label.set_text(text)
            label.set_style_text_font(lv.font_montserrat_10, 0)
            label.center()
            btn.add_event_cb(make_anim_click_handler(mode, btn), lv.EVENT.CLICKED, None)
            self._anim_buttons.append((mode, btn))
            if mode == self._mode:
                btn.add_style(self._anim_style_selected, 0)

        LightsManager.set_led_num(len(self._badge_leds) + self._sao_count)
        self.recompute_active_leds()
        self.update_leds()
        
        self.setContentView(screen)

    def select_animation(self, mode, btn):
        self._mode = mode
        self.highlight_button(mode)

        if mode == "static":
            self._stop_animation()
            self.update_leds()
        else:
            # reset per-animation state so switching patterns looks clean
            self._blink_state = True
            self._blink_count = 0
            self._chase_index = -1
            self._pulse_phase = 0.0
            self._rainbow_hue = 0.0
            self._start_animation()

    def highlight_button(self, mode):
        """Update which animation button looks selected, without needing a click event."""
        for m, b in self._anim_buttons:
            if m == mode:
                b.add_style(self._anim_style_selected, 0)
            else:
                b.remove_style(self._anim_style_selected, 0)

    def onResume(self, screen):
        if self._mode != "static":
            self._start_animation()

    def onPause(self, screen):
        self._stop_animation()
        LightsManager.clear()
        LightsManager.write()

    def _start_animation(self):
        if not self._anim_active:
            self._last_time = time.ticks_ms()
            mpos.ui.task_handler.add_event_cb(self.update_frame, 1)
            self._anim_active = True

    def _stop_animation(self):
        if self._anim_active:
            mpos.ui.task_handler.remove_event_cb(self.update_frame)
            self._anim_active = False

    def _finish_one_shot(self):
        """Called when a one-shot animation (blink/chase) completes: stop and go back to Static."""
        self._stop_animation()
        self._mode = "static"
        self.highlight_button("static")
        self.update_leds()

    def recompute_active_leds(self):
        leds = []
        if self._badge_show:
            leds.extend(self._badge_leds)
        if self._sao_show:
            leds.extend(range(len(self._badge_leds), len(self._badge_leds) + self._sao_count))
        self._active_leds = leds

    def set_active_leds(self, colors_by_index):
        """colors_by_index: dict {led_index: (r,g,b)}. Any active led not in the dict is turned off."""
        LightsManager.clear()
        for led, color in colors_by_index.items():
            LightsManager.set_led(led, *color)
        LightsManager.write()

    def update_frame(self, a, b):
        now = time.ticks_ms()
        delta_time = time.ticks_diff(now, self._last_time) / 1000.0
        if delta_time < self.UPDATE_INTERVAL:
            return
        self._last_time = now

        if not self._active_leds:
            LightsManager.clear()
            LightsManager.write()
            return

        # 1. Blink (ONE-SHOT): flip on/off a few times, then stop and revert to Static
        if self._mode == "blink":
            self._blink_state = not self._blink_state
            color = self.colorHSV(self._hue, 255, self._brightness) if self._blink_state else (0, 0, 0)
            self.set_active_leds({led: color for led in self._active_leds})
            self._blink_count += 1
            if self._blink_count >= self._blink_max:
                self._finish_one_shot()

        # 2. Chase (ONE-SHOT): light moves through the LEDs once, then stop and revert to Static
        elif self._mode == "chase":
            self._chase_index += 1
            if self._chase_index >= len(self._active_leds):
                self._finish_one_shot()
                return
            lit_led = self._active_leds[self._chase_index]
            color = self.colorHSV(self._hue, 255, self._brightness)
            self.set_active_leds({lit_led: color})

        # 3. Pulse (loops): smooth brightness fade using a sine wave
        elif self._mode == "pulse":
            self._pulse_phase += delta_time * 2.0  # speed
            level = (math.sin(self._pulse_phase) + 1) / 2  # 0..1
            val = int(self._brightness * level)
            color = self.colorHSV(self._hue, 255, val)
            self.set_active_leds({led: color for led in self._active_leds})

        # 4. Rainbow (loops): each LED gets its own hue offset, and the whole thing rotates
        elif self._mode == "rainbow":
            self._rainbow_hue += delta_time * 20000  # speed, wraps at 65536
            base_hue = int(self._rainbow_hue) % 65536
            colors = {}
            for i, led in enumerate(self._active_leds):
                led_hue = (base_hue + int(i * 65536 / len(self._active_leds))) % 65536
                colors[led] = self.colorHSV(led_hue, 255, self._brightness)
            self.set_active_leds(colors)

    def update_leds(self):
        """Static (non-animated) display, driven by checkboxes/sliders."""
        LightsManager.clear()
        color = self.colorHSV(self._hue, 255, self._brightness)
        for led in self._active_leds:
            LightsManager.set_led(led, *color)
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