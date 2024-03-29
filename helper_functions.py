import numpy as np
import cv2
import time
import tkinter as tk
import subprocess
import json

def color_map(velocity, max_velocity):
    normalized_velocity = min(velocity / max_velocity, 1)
    blue_component = int(normalized_velocity * 255)
    red_component = int((1 - normalized_velocity) * 255)
    return red_component, 0, blue_component

def draw_flow(img, flow, winsize=30, real_time_fps=30, show_fps=False, frame_count=0, start_time=None, prev_avg_velocity=0, alpha=0.1, conv_factor=1.0, color_map_on=False):
    """
    Draws the optical flow on the given image.

    Parameters:
    img (numpy.ndarray): The input image (grayscale or color) on which the flow vectors will be drawn.
    flow (numpy.ndarray): The calculated optical flow vectors for each point in the image.
    winsize (int, optional): The size of the window for calculating optical flow. Default is 30.
    real_time_fps (float, optional): The frames per second of the video input for scaling the flow vectors. Default is 30.
    show_fps (bool, optional): If True, the current FPS will be displayed on the image. Default is False.
    frame_count (int, optional): The current count of frames processed, used for FPS calculation. Default is 0.
    start_time (float, optional): The start time in seconds for FPS calculation. If None, FPS will not be calculated. Default is None.
    prev_avg_velocity (float, optional): The previous average velocity, used for calculating the exponential moving average. Default is 0.
    alpha (float, optional): The alpha value for the exponential moving average calculation. Default is 0.1.
    conv_factor (float, optional): A conversion factor for adjusting the velocity scale. Default is 1.0.
    color_map_on (bool, optional): If True, a color map will be applied to the flow lines based on velocity. Default is False.

    Returns:
    tuple: A tuple containing:
        - vis (numpy.ndarray): The image with flow vectors drawn.
        - avg_velocity (float): The current average velocity calculated from the flow vectors.
    
    Description:
    The function calculates the flow vectors' magnitudes and directions from the 'flow' parameter.
    It then draws these vectors on the 'img' as lines, indicating the motion detected in the image.
    If 'show_fps' is True, it also calculates and displays the current frames per second on the image.
    The function uses an exponential moving average to smooth out the velocity values over time.
    """  
    
    # Get height (h) and width (w) of the image for grid calculation
    h, w = img.shape[:2]

    # Calculate the step size for sampling flow vectors; it depends on the window size (winsize)
    step = max(2, winsize // 2)

    # Generate a grid of (x, y) coordinates for sampling the flow.
    # The grid points are spaced 'step' units apart and cover the whole image.
    # The grid is then flattened into 1D arrays for 'x' and 'y'.
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(np.int16)

    # Sample the optical flow vectors (fx, fy) at each grid point.
    # 'fx' and 'fy' represent motion in the x and y directions, respectively.
    fx, fy = flow[y, x].T

    # Calculate the magnitude of the flow vector (velocity) at each sampled point.
    # This represents the speed and scale of movement.
    velocities = np.hypot(fx, fy) * real_time_fps * conv_factor

    # Compute the average velocity across all sampled points for a general sense of motion.
    current_velocity = np.mean(velocities) if velocities.size > 0 else 0

    # Calculate the Exponential Moving Average of the velocity to smooth fluctuations over time.
    avg_velocity = (current_velocity * alpha) + (prev_avg_velocity * (1 - alpha))

    # Create an array of line segments to represent the flow. Each line starts at (x, y) and
    # ends at (x + fx, y + fy), indicating the direction and magnitude of flow.
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int16(lines + 0.5)

    # Convert the image to a BGR color image if it's not already, to draw colored lines.
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Draw each line on the image. Each line represents the optical flow vector at one grid point.
    for ((x1, y1), (x2, y2)) in lines:
        color = (0, 255, 0)  # Set the line color to green
        cv2.line(vis, (x1, y1), (x2, y2), color, 1)

    # If FPS (Frames Per Second) display is enabled, compute and display it on the image.
    if show_fps and start_time is not None:
        current_fps = frame_count / (time.time() - start_time)  # Calculate current FPS
        cv2.putText(vis, f"FPS: {current_fps:.2f}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv2.putText(vis, f"Avg Velocity: {avg_velocity:.2f}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

    # Return the final image with optical flow vectors drawn and the current average velocity.
    return vis, avg_velocity


# Define a function to create a numeric keypad instead of using the simpledialog
def get_numeric_input(title, prompt):
    def on_button_press(value):
        if value == 'Enter':
            user_input.set(entry.get())  # Set the user_input variable with the entry value
            keypad.destroy()
        elif value == 'Clear':
            entry.delete(0, tk.END)
        else:
            entry.insert(tk.END, value)  # Insert the button's value at the end of the text entry

    keypad = tk.Tk()
    keypad.title(title)
    keypad.attributes('-fullscreen', True)  # Make the window full screen
    
    # Variable to store user input
    user_input = tk.StringVar(keypad)
    
    tk.Label(keypad, text=prompt, font=("Helvetica", 20)).grid(row=0, column=0, columnspan=3)
    
    entry = tk.Entry(keypad, textvariable=user_input, justify='right', font=("Helvetica", 20))
    entry.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)
    
    # Numeric Buttons
    buttons = [
        ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
        ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
        ('7', 4, 0), ('8', 4, 1), ('9', 4, 2),
        ('Clear', 5, 0), ('0', 5, 1), ('Enter', 5, 2),
    ]
    
    for (text, row, col) in buttons:
        action = lambda x=text: on_button_press(x)
        btn = tk.Button(keypad, text=text, command=action, font=("Helvetica", 20))
        btn.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
        keypad.grid_rowconfigure(row, weight=1)
        keypad.grid_columnconfigure(col, weight=1)

    # Adjust the row and column weights so they expand to fill the screen
    for i in range(1, 6):
        keypad.grid_rowconfigure(i, weight=1)
    for i in range(3):
        keypad.grid_columnconfigure(i, weight=1)

    keypad.mainloop()
    return user_input.get()  # Return the value when the window is closed



def find_usb_mount_path():
    try:
        result = subprocess.run(['lsblk', '-o', 'NAME,MOUNTPOINT', '-J'], capture_output=True, text=True)
        output = result.stdout

        if output:
            data = json.loads(output)
            for device in data.get('blockdevices', []):
                if device.get('children'):
                    for child in device['children']:
                        if child.get('mountpoint'):
                            return child['mountpoint']
        return None
    except Exception as e:
        print(f"Error finding USB mount point: {e}")
        return None


