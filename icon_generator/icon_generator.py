from PIL import Image, ImageDraw

def generate_exact_hardware_icon(output_name):
    # 1. Base 64x64 canvas with transparent margins for theme adaptability
    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Main Horizontal PCB Body (True 2:1 Wide Ratio Board layout)
    pcb_purple = (53, 24, 95, 255)
    draw.rectangle([2, 16, 61, 47], fill=pcb_purple) # Main center deck
    draw.rectangle([3, 15, 60, 48], fill=pcb_purple) # Extension layers for rounding
    
    # Rounded corners edge cleaning
    draw.point((3, 17), fill=pcb_purple)
    draw.point((60, 17), fill=pcb_purple)
    draw.point((3, 46), fill=pcb_purple)
    draw.point((60, 46), fill=pcb_purple)

    # 3. Gold Grounding Silkscreen Track Line Frame
    gold = (218, 165, 32, 255)
    draw.rectangle([3, 16, 60, 47], outline=gold, width=1)
    
    # 4. FIXED: Shifted Screen Upwards by 2 Pixels (Y: 18 to 35)
    draw.rectangle([18, 18, 45, 35], fill=(12, 14, 18, 255)) # Glass Matrix
    draw.rectangle([17, 17, 46, 36], outline=(40, 45, 55, 255), width=1) # Screen Bezel

    # 5. Left Side Analog Joystick Assembly (X: 10, Y: 32 Center Axis)
    draw.rectangle([8, 30, 12, 34], fill=(25, 25, 28, 255))
    draw.point((10, 32), fill=(100, 100, 105, 255))

    # 6. Right Side Action Buttons Diamond Assembly (Y: 32 Center Axis)
    btn_color = (20, 20, 22, 255)
    draw.point((53, 29), fill=btn_color) # Top Button (X)
    draw.point((50, 32), fill=btn_color) # Left Button (Y)
    draw.point((56, 32), fill=btn_color) # Right Button (A)
    draw.point((53, 35), fill=btn_color) # Bottom Button (B)

    # 7. SHINY DIAMOND SAO BREAKOUT (Top Left Header Bay Layout)
    sao_bg = (0, 128, 105, 255)
    sao_gold = (240, 190, 40, 255)
    
    draw.point((8, 8), fill=sao_gold)
    draw.rectangle([7, 9, 9, 9], fill=sao_bg)
    draw.point((7, 9), fill=sao_gold); draw.point((9, 9), fill=sao_gold)
    draw.rectangle([6, 10, 10, 10], fill=sao_bg)
    draw.point((6, 10), fill=sao_gold); draw.point((10, 10), fill=sao_gold)
    draw.rectangle([5, 11, 11, 11], fill=sao_bg)
    draw.point((5, 11), fill=sao_gold); draw.point((11, 11), fill=sao_gold)
    draw.rectangle([6, 12, 10, 12], fill=sao_bg)
    draw.point((6, 12), fill=sao_gold); draw.point((10, 12), fill=sao_gold)
    draw.rectangle([7, 13, 9, 13], fill=sao_bg)
    draw.point((7, 13), fill=sao_gold); draw.point((9, 13), fill=sao_gold)
    draw.point((8, 14), fill=sao_gold)
    
    # Specular gloss highlights on the SAO
    draw.point((7, 10), fill=(200, 255, 240, 255))
    draw.point((8, 10), fill=(255, 255, 255, 255))
    draw.point((8, 11), fill=(255, 50, 50, 255))   # Active Red LED node
    draw.point((8, 12), fill=(255, 120, 120, 125)) # Glow layer

    # 8. FIXED: Restored Main 5 LEDs to Large 3x3 Form Factor (Y: 39 to 41 Axis)
    led_positions_x = [21, 26, 31, 36, 41]
    led_colors = [
        (255, 40, 60, 255),   # LED 1: Red (X:21)
        (40, 255, 80, 255),   # LED 2: Green (X:26)
        (0, 180, 255, 255),   # LED 3: Blue (X:31)
        (255, 215, 0, 255),   # LED 4: Yellow (X:36)
        (255, 50, 180, 255)   # LED 5: Pink (X:41)
    ]
    
    for x, color in zip(led_positions_x, led_colors):
        # 3x3 square emissive node block
        draw.rectangle([x-1, 39, x+1, 41], fill=color)
        
        # Cross glow trace blend
        glow = tuple(list(color[:3]) + [100])
        draw.point((x-2, 40), fill=glow)
        draw.point((x+2, 40), fill=glow)
        draw.point((x, 38), fill=glow)
        draw.point((x, 42), fill=glow)

    # 9. FIXED: Placed 2 Navigation Buttons Interspersed in Between the Row Elements
    # Left Button centered between LED 1 & 2 (X Center: 23-24, Y: 44-45)
    draw.rectangle([23, 44, 24, 45], fill=btn_color)
    # Right Button centered between LED 4 & 5 (X Center: 38-39, Y: 44-45)
    draw.rectangle([38, 44, 39, 45], fill=btn_color)

    # Save to your directory tree
    img.save(output_name, 'PNG')
    print(f"Success! Exact 1:1 hardware configuration saved to '{output_name}'")

generate_exact_hardware_icon('icon_64x64.png')
