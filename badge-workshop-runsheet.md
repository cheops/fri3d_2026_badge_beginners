# Fri3d Badge Programming Workshop — Facilitator Runsheet
**Duration: 2 hours | Format: self-paced hands-on with interleaved mini-lectures**

## Design principle

Nobody waits for anybody. Every hands-on block has:
- A **copy-paste starting snippet** (so a slow typist isn't blocked by syntax)
- A **"done" signal** everyone can visibly reach (LED lights up = done)
- A **stretch goal** for fast finishers, so they keep experimenting instead of getting bored/distracting others
- A **fallback snippet** to paste if someone gets stuck, so they don't fall permanently behind

Lecture blocks are scheduled *right after* a hands-on block, timed so the fast finishers are already bored (good — they'll listen) and the slow finishers are still typing (fine — they can half-listen while finishing, and the snippet is right there if they need it).

Use a simple 2-card status system per person/table: 🟢 = done, want more | 🔴 = stuck, need help. Cuts down on "is everyone ready?" polling.

---

## Timeline overview

| # | Time | Duration | Block | Type |
|---|------|----------|-------|------|
| 0 | 0:00 | 5 min | Welcome + setup check | Logistics |
| 1 | 0:05 | 20 min | **Quick win: solid color** | Hands-on |
| 2 | 0:25 | 8 min | What's on your badge (hardware) | Lecture |
| 3 | 0:33 | 15 min | On/off + brightness | Hands-on |
| 4 | 0:48 | 10 min | Firmware options: Arduino / ESP-IDF / MicroPython / MicroPythonOS | Lecture |
| 5 | 0:58 | 15 min | Color slider | Hands-on |
| 6 | 1:13 | 10 min | Dev workflow: Thonny → mpremote → Fri3d-IDE | Lecture |
| 7 | 1:23 | 20 min | Animations: blink → chase (+ stretch: pulse/rainbow) | Hands-on |
| 8 | 1:43 | 10 min | Show & tell | Interactive |
| 9 | 1:53 | 7 min | Wrap-up + resources | Lecture |

Total: 120 min (includes ~5 min natural buffer distributed across blocks).

---

## Block 0 — Welcome + setup check (0:00–0:05)

Goal: everyone has a badge, USB cable, and Fri3d-IDE (ViperIDE-based) open in a browser tab, **before** any teaching starts.

- One sentence on what they'll build: "By the end, your badge will glow, pulse, and chase colors — and you'll have written the code yourself."
- Get everyone to plug in and load Fri3d-IDE. Don't explain it yet — just confirm the badge shows as connected.
- 🟢/🔴 card check. Help the 🔴s while the 🟢s wait 2 minutes (fine, it's short).

---

## Block 1 — Quick win: solid color (0:05–0:25) — HANDS-ON

**Goal: LEDs are lit within the first 20–25 minutes, no exceptions.**

Give this snippet directly — don't make them derive it. Explain each line in one short phrase, but don't dwell:

```python
from mpos import LightsManager

LightsManager.set_led_num(15)      # 5 badge LEDs + 10 SAO LEDs
LightsManager.set_all(255, 0, 128) # R, G, B — try changing these numbers!
LightsManager.write()              # nothing happens until you call this
```

- "Done" signal: badge lights up pink.
- Immediately invite them to change the R/G/B numbers and re-run. This is the "aha, I'm programming it" moment — let them play for 2–3 minutes.
- **Stretch goal** (fast finishers): try `set_led(index, r, g, b)` to light just one LED a different color than the rest.
- **Fallback**: if `set_led_num`/imports fail, have a pre-flashed badge nearby to swap in, so they're not stuck waiting on troubleshooting during the quick win.

---

## Block 2 — What's on your badge (0:25–0:33) — LECTURE

Keep this tight; it's context, not a prerequisite for what they just did.

- ESP32(-Sx) microcontroller — what that means in one sentence (small computer, WiFi/BT built in)
- The 5 onboard NeoPixel RGB LEDs (what they just controlled)
- The SAO (Simple Add-On) connector — expansion LEDs, what "SAO" stands for, other things people plug in there
- Screen/buttons if present — briefly, not a deep dive
- Power (USB / battery if applicable)

One slide with a labeled photo of the badge is enough. No code here — let the hands-on block speak for itself.

---

## Block 3 — On/off + brightness (0:33–0:48) — HANDS-ON

**Goal: introduce state (a variable that persists) and a UI control that changes it.**

Starting snippet (they extend Block 1's result):

```python
from mpos import Activity, LightsManager
import lvgl as lv

class Main(Activity):
    _brightness = 255

    def onCreate(self):
        screen = lv.obj()

        slider = lv.slider(screen)
        slider.set_range(0, 255)
        slider.set_value(self._brightness, False)
        slider.align(lv.ALIGN.CENTER, 0, 0)

        def slider_changed(e):
            self._brightness = slider.get_value()
            self.update_leds()
        slider.add_event_cb(slider_changed, lv.EVENT.VALUE_CHANGED, None)

        LightsManager.set_led_num(15)
        self.update_leds()

        self.setContentView(screen)  # should be last line

    def update_leds(self):
        LightsManager.set_all(self._brightness, 0, 128)
        LightsManager.write()
```

- "Done" signal: dragging the slider visibly dims/brightens the LEDs.
- **Stretch goal**: add a checkbox/switch that turns LEDs fully off regardless of slider position (this is the on/off toggle from earlier in this project — a nice natural next step).
- **Fallback**: paste-ready full snippet above works standalone — no dependency on Block 1's exact code.

---

## Block 4 — Firmware options (0:48–0:58) — LECTURE

This is the "why are we using what we're using" block — good to place *after* they've already had a working result, so it's satisfying context rather than a barrier before doing anything.

Suggested comparison table (put on a slide):

| Option | Language | Good for | Trade-off |
|---|---|---|---|
| Arduino (framework) | C/C++ | Huge library ecosystem, tons of tutorials | Slower iteration (compile + flash every change) |
| ESP-IDF | C | Full control, production firmware | Steepest learning curve, not beginner-friendly |
| MicroPython | Python | Fast iteration, live REPL, beginner-friendly | Slower execution than C, more RAM overhead |
| MicroPythonOS | Python + LVGL | App-style structure (Activities, UI widgets) — what we're using today | Newer/smaller ecosystem, badge-specific |

Message to land: *"We're using MicroPythonOS today because you get a working result in minutes, not hours — but everything you learn about MicroPython transfers if you ever want to drop down to raw MicroPython or even C later."*

---

## Block 5 — Color slider (0:58–1:13) — HANDS-ON

**Goal: a second slider, same pattern as brightness — reinforces the concept via repetition rather than novelty.**

Starting snippet (extends Block 3):

```python
def onCreate(self):
    # ...existing brightness slider code...

    hue_slider = lv.slider(screen)
    hue_slider.set_range(0, 359)
    hue_slider.align_to(slider, lv.ALIGN.OUT_BOTTOM_MID, 0, 20)

    def hue_changed(e):
        self._hue = hue_slider.get_value()
        self.update_leds()
    hue_slider.add_event_cb(hue_changed, lv.EVENT.VALUE_CHANGED, None)

def update_leds(self):
    r, g, b = self.colorHSV(int(self._hue * 65536 / 360), 255, self._brightness)
    LightsManager.set_all(r, g, b)
    LightsManager.write()
```

Give `colorHSV()` as a ready-made "magic function" to paste in — don't explain the HSV math in a beginner workshop, just say "this converts a color wheel position into red/green/blue for you."

- "Done" signal: dragging the second slider visibly changes the LED color, not just brightness.
- **Stretch goal**: style the slider track with the rainbow-gradient canvas trick (visually rewarding, optional).
- **Fallback**: full two-slider snippet as a single paste-able block for anyone who's fallen behind.

---

## Block 6 — Dev workflow (1:13–1:23) — LECTURE

Now that they've written real code twice, this context lands better than it would up front.

- **Thonny**: simplest MicroPython IDE, good for tiny scripts and REPL experiments — mention briefly, they may see it in tutorials online.
- **mpremote**: command-line tool for copying files to/from the board and running scripts — mention it exists, useful once they're comfortable with a terminal.
- **Fri3d-IDE (built on ViperIDE)**: what we're using today — browser-based, no install, direct USB connection, live file editing. This is *why* today's workshop has near-zero setup friction.

One sentence bridging to independence: "Once you go home, all three of these work with the exact same MicroPython code you wrote today — Fri3d-IDE isn't a toy, it's just the fastest way to get started."

---

## Block 7 — Animations (1:23–1:43) — HANDS-ON

**Goal: the "wow" moment. Split into an easy win and an optional deep end.**

**Step A — Blink (everyone should reach this, ~8 min):**

```python
import time

def blink_once(self):
    r, g, b = self.colorHSV(int(self._hue * 65536 / 360), 255, self._brightness)
    for _ in range(3):
        LightsManager.set_all(r, g, b)
        LightsManager.write()
        time.sleep_ms(200)
        LightsManager.clear()
        LightsManager.write()
        time.sleep_ms(200)
```
Wire it to a button: `btn.add_event_cb(lambda e: self.blink_once(), lv.EVENT.CLICKED, None)`

- "Done" signal: pressing the button makes the badge blink 3 times using their own chosen color.

**Step B — Chase (stretch, ~10 min for those who reach it):**

```python
def chase_once(self):
    r, g, b = self.colorHSV(int(self._hue * 65536 / 360), 255, self._brightness)
    for i in range(15):
        LightsManager.clear()
        LightsManager.set_led(i, r, g, b)
        LightsManager.write()
        time.sleep_ms(80)
    LightsManager.clear()
    LightsManager.write()
```

**Step C — Pulse / Rainbow (bonus, only for the fastest):** point them to `math.sin()` for smooth pulsing, or per-LED hue offsets for a rainbow sweep — frame these as "if you finish everything else, here's a puzzle" rather than required content.

**Fallback for anyone still behind**: it's fine if they only reach Static + Blink by the end — that's still a complete, satisfying result, and matches the "always have something working" principle from Block 1.

---

## Block 8 — Show & tell (1:43–1:53) — INTERACTIVE

- Walk around, badges lit up on the table.
- Ask 2–3 people to briefly show what they built (30 seconds each) — especially anyone who reached a stretch goal.
- This also naturally surfaces who needs a hand before wrap-up.

---

## Block 9 — Wrap-up + resources (1:53–2:00) — LECTURE

- Recap what they built: solid color → brightness → color → animation, i.e. state, UI events, and a frame loop — the same three concepts every interactive program uses.
- Point to: MicroPythonOS docs, the LightsManager API reference, where to get Fri3d-IDE / Thonny / mpremote at home, and a community channel (Discord/forum) for questions.
- Encourage them to keep their code — it's a real, working badge app they can keep extending.

---

## Facilitator tips

- **Pre-load every snippet** in this document into a shared link/QR code (e.g. a pastebin or the workshop repo) so people copy-paste instead of transcribing from a slide — transcription errors eat far more time than the actual concepts.
- **Pair up early strugglers with early finishers** rather than always routing to yourself — frees you to keep the room moving.
- **Timebox strictly on lecture blocks, loosely on hands-on blocks** — it's fine if hands-on runs 3–5 min over, since slower participants catching up is the whole point of this design. Trim from Block 9 (resources can be a shared link, doesn't need full airtime) if you're running behind.
