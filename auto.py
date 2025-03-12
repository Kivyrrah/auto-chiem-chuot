import cv2
import numpy as np
import pyautogui
import time
from mss import mss
import threading
import keyboard  # Import the keyboard module

# Global flag to control the loop
stop_flag = False

def capture_screen(sct, region=None):
    if region:
        screen = np.array(sct.grab(region))
    else:
        screen = np.array(sct.grab(sct.monitors[1]))  # Grab the primary monitor if no region specified
    return cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)

def find_color_positions(image, target_color, tolerance=3):
    lower_bound = np.maximum(0, np.array(target_color) - tolerance)
    upper_bound = np.minimum(255, np.array(target_color) + tolerance)
    mask = cv2.inRange(image, lower_bound, upper_bound)
    
    coords = np.argwhere(mask > 0)
    positions = [(int(x), int(y)) for y, x in coords]  # Convert to list of (x, y) tuples
    return positions

def click_at_position(position):
    pyautogui.click(x=position[0], y=position[1], clicks=1, interval=0.0)
    print(f"Clicked at position: {position}")

def click_target(target_color, screen, tolerance=3, max_clicks=15):
    positions = find_color_positions(screen, target_color, tolerance)
    if positions:
        threads = []
        for position in positions[:max_clicks]:  # Limit to max_clicks positions
            thread = threading.Thread(target=click_at_position, args=(position,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
    else:
        print(f"Target color {target_color} not found on the screen.")

def main(target_colors, duration=3300, region=None, max_clicks=10):
    global stop_flag
    start_time = time.time()
    with mss() as sct:
        while (time.time() - start_time) < duration and not stop_flag:
            screen = capture_screen(sct, region)
            
            for target_color in target_colors:
                click_target(target_color, screen, tolerance=3, max_clicks=max_clicks)  # Adjust tolerance and max_clicks as needed
            
            # Optional sleep to control the rate of screen captures
            time.sleep(0.0)  # No sleep between iterations

def on_esc_press(event):
    global stop_flag
    if event.name == 'esc':
        stop_flag = True
        print("ESC pressed, stopping the script...")

if __name__ == "__main__":
    # Define the target colors in BGR format
    target_colors = [
        np.array([0, 222, 202])   # Green color
    ]
   
    # Define the duration for how long the script should run (in seconds)
    duration = 3300
   
    # Define the region to capture (left, top, width, height)
    region = {'left': 0, 'top': 0, 'width': 1800, 'height': 880}  # Adjust as needed

    # Define the maximum number of clicks for each target color
    max_clicks = 10  # Adjust this value to limit the number of clicks

    # Register the ESC key press event
    keyboard.on_press(on_esc_press)
   
    # Run main function with all target colors
    main(target_colors, duration, region, max_clicks)
