from mpos import LightsManager

LightsManager.set_led_num(15)      # 5 badge LEDs + 10 SAO LEDs

# First 5 LEDs: Forward Rainbow
LightsManager.set_led(0, 255, 0, 0)      # Red
LightsManager.set_led(1, 204, 255, 0)    # Yellow-Green
LightsManager.set_led(2, 0, 255, 102)    # Cyan-Green
LightsManager.set_led(3, 0, 102, 255)    # Blue
LightsManager.set_led(4, 204, 0, 255)    # Purple

# Next 10 LEDs: Reverse Rainbow
LightsManager.set_led(5, 204, 0, 255)    # Purple
LightsManager.set_led(6, 102, 0, 255)    # Violet
LightsManager.set_led(7, 0, 0, 255)      # Pure Blue
LightsManager.set_led(8, 0, 102, 255)    # Deep Cyan
LightsManager.set_led(9, 0, 204, 255)    # Light Cyan
LightsManager.set_led(10, 0, 255, 102)   # Mint
LightsManager.set_led(11, 102, 255, 0)   # Lime
LightsManager.set_led(12, 204, 255, 0)   # Yellow-Green
LightsManager.set_led(13, 255, 153, 0)   # Orange
LightsManager.set_led(14, 255, 0, 0)     # Red

LightsManager.write()              # nothing happens until you call this
