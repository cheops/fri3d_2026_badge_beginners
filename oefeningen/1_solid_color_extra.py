from mpos import LightsManager

LightsManager.set_led_num(15)      # 5 badge LEDs + 10 SAO LEDs
LightsManager.set_all(250, 190, 0) # R, G, B — try changing these numbers!
LightsManager.write()              # nothing happens until you call this
