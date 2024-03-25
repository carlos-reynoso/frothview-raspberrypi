import numpy as np
import cv2
import time

def color_map(velocity, max_velocity):
    normalized_velocity = min(velocity / max_velocity, 1)
    blue_component = int(normalized_velocity * 255)
    red_component = int((1 - normalized_velocity) * 255)
    return red_component, 0, blue_component

def draw_flow(img, flow, winsize=30, real_time_fps=30, show_fps=False, frame_count=0, start_time=None, prev_avg_velocity=0, alpha=0.1,conv_factor=1.0,color_map_on=False):
    h, w = img.shape[:2]
    step = max(2, winsize // 2)  # Dynamically set step based on winsize
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(np.int16)

    fx, fy = flow[y, x].T

#    velocities = np.sqrt(fx**2 + fy**2) * real_time_fps * conv_factor
    velocities = np.hypot(fx, fy) * real_time_fps * conv_factor

    current_velocity = np.mean(velocities) if velocities.size > 0 else 0

    # Calculate the Exponential Moving Average for velocity
    avg_velocity = (current_velocity * alpha) + (prev_avg_velocity * (1 - alpha))

    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int16(lines + 0.5)
    
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for ((x1, y1), (x2, y2)), velocity in zip(lines, velocities):
        color= (0,255,0)
        cv2.line(vis, (x1, y1), (x2, y2), color, 1)

    if show_fps and start_time is not None:
        current_fps = frame_count / (time.time() - start_time)
        cv2.putText(vis, f"FPS: {current_fps:.2f}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv2.putText(vis, f"Avg Velocity: {avg_velocity:.2f}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0,0))


    return vis, avg_velocity

