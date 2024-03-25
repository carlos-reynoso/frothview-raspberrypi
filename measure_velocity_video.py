import cv2
import numpy as np
import time
from helper_functions import draw_flow
import pandas as pd
import matplotlib.pyplot as plt

def main(video_path, show_fps=False, use_roi=True, scale_factor=1.0):
    print('Starting')

    # Pull the conversion factor from conv_factor.txt if exists
    try:
        with open('conv_factor.txt', 'r') as f:
            conv_factor = float(f.read())
            print(f"Conversion factor found: {conv_factor}")
    except FileNotFoundError:
        print("No conversion factor found. Using default value of 1.0")
        conv_factor = 1.0

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    # Get FPS from the video file
    real_time_fps = cap.get(cv2.CAP_PROP_FPS)
    real_time_fps = 30

    print(f"Video FPS: {real_time_fps}")

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

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec used to create the video
    output_dimensions = (w_roi, h_roi) if use_roi else (frame_width, frame_height)
    out = cv2.VideoWriter('output_video.mp4', fourcc, 10, output_dimensions)


    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    frame_count = 0
    start_time = time.time()
    prev_avg_velocity = 0
    winsize =50
    frame_data = []

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if use_roi:
            roi_frame = frame[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
        else:
            roi_frame = frame

        roi_frame_orig = roi_frame.copy()
        roi_frame_orig=cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        # Apply contrast enhancement on the ROI
        frame_YUV = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2YUV)
        frame_YUV[:, :, 0] = cv2.equalizeHist(frame_YUV[:, :, 0])
        roi_frame = cv2.cvtColor(frame_YUV, cv2.COLOR_YUV2BGR)

        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        # Ensure prev_gray is only set after the first frame is captured
        if frame_count == 1:
            prev_gray = gray


        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, pyr_scale=0.5, levels=3, winsize=winsize, iterations=5, poly_n=5, poly_sigma=1.2, flags=0)
    
        prev_gray = gray.copy()  # Update prev_gray for the next iteration

        vis, prev_avg_velocity = draw_flow(roi_frame_orig, flow, winsize, real_time_fps, show_fps, frame_count, start_time, prev_avg_velocity, conv_factor=conv_factor, color_map_on=True)
        
        timestamp = frame_count / real_time_fps  # Calculate timestamp for each frame
        frame_data.append((timestamp, prev_avg_velocity))  # Store timestamp and velocity

        
        cv2.imshow('Optical flow', vis)

        # Write the processed frame to the video file
        out.write(vis)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    
    # Create DataFrame from the frame data and save to CSV
    velocities_df = pd.DataFrame(frame_data, columns=['Timestamp', 'Velocity'])
    velocities_df.to_csv('velocities.csv', index=False)

    # Plot histogram of velocities
    velocities_df['Velocity'].hist(bins=20)
    plt.xlabel('Velocity')
    plt.ylabel('Frequency')
    plt.title('Velocity Histogram')
    plt.show()


if __name__ == "__main__":
    video_path = "video.mp4"  # Replace with the path to your video file
    main(video_path, show_fps=True, use_roi=True, scale_factor=.2)  # Adjust scale_factor as needed
