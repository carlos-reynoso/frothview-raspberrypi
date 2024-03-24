import cv2
import numpy as np
import time

def color_map(velocity, max_velocity):
    normalized_velocity = min(velocity / max_velocity, 1)
    blue_component = int(normalized_velocity * 255)
    red_component = int((1 - normalized_velocity) * 255)
    return red_component, 0, blue_component

def draw_flow(img, flow, winsize=30, real_time_fps=30, show_fps=False, frame_count=0, start_time=None, prev_avg_velocity=0, alpha=0.1):
    h, w = img.shape[:2]
    step = max(2, winsize // 2)  # Dynamically set step based on winsize
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(np.int16)

    fx, fy = flow[y, x].T
    velocities = np.sqrt(fx**2 + fy**2) * real_time_fps *1
    current_velocity = np.mean(velocities) if velocities.size > 0 else 0

    # Calculate the Exponential Moving Average for velocity
    avg_velocity = (current_velocity * alpha) + (prev_avg_velocity * (1 - alpha))

    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int16(lines + 0.5)
    
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for ((x1, y1), (x2, y2)), velocity in zip(lines, velocities):
        color = color_map(velocity, 2)
        cv2.line(vis, (x1, y1), (x2, y2), color, 1)

    if show_fps and start_time is not None:
        current_fps = frame_count / (time.time() - start_time)
        cv2.putText(vis, f"FPS: {current_fps:.2f}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))
        cv2.putText(vis, f"Avg Velocity: {avg_velocity:.2f}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))

    return vis, avg_velocity



def main(show_fps=False, use_roi=True, scale_factor=1.0):
    cap = cv2.VideoCapture(0)
    ret, prev = cap.read()

    if not ret:
        print("Failed to grab the frame")
        return

    frame_height, frame_width = prev.shape[:2]

    # Calculate the ROI based on scale factor
    w_roi = int(frame_width * scale_factor)
    h_roi = int(frame_height * scale_factor)
    x_roi = (frame_width - w_roi) // 2
    y_roi = (frame_height - h_roi) // 2

    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    frame_count = 0
    start_time = time.time()
    prev_frame_time = start_time
    prev_avg_velocity = 0
    winsize = 100

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_frame_time = time.time()
        real_time_fps = 1 / (current_frame_time - prev_frame_time) if current_frame_time != prev_frame_time else 30
        prev_frame_time = current_frame_time

        if use_roi:
            roi_frame = frame[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
        else:
            roi_frame = frame

        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        # Ensure prev_gray is only set after the first frame is captured
        if frame_count == 0:
            prev_gray = gray


        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 1, winsize, 5, 5, 1.2, 0)
        prev_gray = gray.copy()  # Update prev_gray for the next iteration

        vis, prev_avg_velocity = draw_flow(gray, flow, winsize, real_time_fps, show_fps, frame_count, start_time, prev_avg_velocity)
        cv2.imshow('Optical flow', vis)

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(show_fps=True, use_roi=True, scale_factor=.5)  # Adjust scale_factor as needed
