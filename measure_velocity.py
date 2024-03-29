import cv2
import numpy as np
import time
from helper_functions import draw_flow
import subprocess
import sys
import csv

def main(show_fps=False, use_roi=True, scale_factor=1.0, skip_rate=1, buffer_size=10):
    print('Starting')

    # Try to pull the conversion factor from 'conv_factor.txt'
    try:
        with open('conv_factor.txt', 'r') as f:
            conv_factor = float(f.read())
            print(f"Conversion factor found: {conv_factor}")
    except FileNotFoundError:
        print("No conversion factor found. Using default value of 1.0")
        conv_factor = 1.0

    cap = cv2.VideoCapture(0)
    ret, prev = cap.read()
    if not ret:
        print("Failed to grab the frame")
        return

    frame_height, frame_width = prev.shape[:2]
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

    cv2.namedWindow('Optical flow', cv2.WINDOW_NORMAL)

    # Initialize CSV file for writing data
    with open('output_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Frame", "Data"])  # Header row
        buffer = []  # Initialize a buffer

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % skip_rate != 0:
                frame_count += 1
                continue

            current_frame_time = time.time()
            real_time_fps = 1 / (current_frame_time - prev_frame_time) if current_frame_time != prev_frame_time else 30
            prev_frame_time = current_frame_time

            if use_roi:
                roi_frame = frame[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
            else:
                roi_frame = frame

            frame_YUV = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2YUV)
            frame_YUV[:, :, 0] = cv2.equalizeHist(frame_YUV[:, :, 0])
            roi_frame = cv2.cvtColor(frame_YUV, cv2.COLOR_YUV2BGR)
            gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

            if frame_count == 0:
                prev_gray = gray

            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, pyr_scale=0.5, levels=3, winsize=winsize, iterations=5, poly_n=5, poly_sigma=1.2, flags=0)
            prev_gray = gray.copy()
            vis, prev_avg_velocity = draw_flow(gray, flow, winsize, real_time_fps, show_fps, frame_count, start_time, prev_avg_velocity, conv_factor=conv_factor, color_map_on=False)
            cv2.imshow('Optical flow', vis)

            # Collect and buffer data
            data_to_write = [frame_count, prev_avg_velocity]  
            buffer.append(data_to_write)

            
            if len(buffer) >= buffer_size:
                print("Writing buffer to file")
                writer.writerows(buffer)
                buffer.clear()

            frame_count += 1
            if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Optical flow', cv2.WND_PROP_VISIBLE) < 1:
                break

        # Write any remaining data in the buffer
        if buffer:
            writer.writerows(buffer)

    cap.release()
    cv2.destroyAllWindows()
    open_main_menu()

def open_main_menu():
    subprocess.Popen(['python', 'menu.py'])
    sys.exit()

if __name__ == "__main__":
    main(show_fps=True, use_roi=True, scale_factor=.5, skip_rate=1)  # Adjust scale_factor as needed
