import cv2
import numpy as np
import time
from helper_functions import get_numeric_input

qr_detected=False

def main(use_roi=False,scale_factor=0.5):


    # Initialize the webcam feed
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    frame_height, frame_width = frame.shape[:2]
    w_roi = int(frame_width * scale_factor)
    h_roi = int(frame_height * scale_factor)
    x_roi = (frame_width - w_roi) // 2
    y_roi = (frame_height - h_roi) // 2
    
    # Initialize QR Code Detector
    qr_detector = cv2.QRCodeDetector()

    # Variable to keep track of QR code detection time
    qr_detected_at = None

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        if use_roi:
            roi_frame = frame[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
        else:
            roi_frame = frame

        # Detect and decode the QR code
        data, bbox, _ = qr_detector.detectAndDecode(roi_frame)

        if bbox is not None:
            # Convert bounding box to integer format
            bbox = bbox[0].astype(int)

            # Draw the square/rectangular contour
            cv2.polylines(roi_frame, [bbox], True, (255, 0, 0), thickness=2)

            if data:
                if qr_detected_at is None:
                    # Record the time when QR code is first detected
                    qr_detected_at = time.time()

                # Calculate the width and height
                width = np.sqrt((bbox[0][0] - bbox[1][0])**2 + (bbox[0][1] - bbox[1][1])**2)
                height = np.sqrt((bbox[0][0] - bbox[3][0])**2 + (bbox[0][1] - bbox[3][1])**2)

                # Text for QR detection and size
                detect_text = "QR Detected"
                size_text = f"Size: {(np.mean([width,height])):.2f}"

                # Calculate text position
                text_size = cv2.getTextSize(detect_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = int(bbox[0][0] + (bbox[3][0] - bbox[0][0])/2 - text_size[0] / 2)
                detect_text_y = int(bbox[3][1] + 30)  # Below the QR code
                size_text_y = detect_text_y + text_size[1] + 5


                # Place the texts
                cv2.putText(roi_frame, size_text, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        else:
            # Reset the QR detection time if QR code is not detected
            qr_detected_at = None

        # Display the frame
        cv2.imshow('QR Code Detector', roi_frame)

        # Check if QR has been in view for more than 5 seconds
        if qr_detected_at is not None and (time.time() - qr_detected_at) > 5:
            print("QR code detected")
            qr_detected=True
            break

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture
    cap.release()
    cv2.destroyAllWindows()

    if qr_detected:
        input1 = get_numeric_input("Numeric Input", "Please enter the QR size in cm:")
        print("QR size entered: ", input1)


        try:
            input1 = float(input1)
        except:
            print("Invalid input")
    
        conv_factor = input1/np.mean([width, height])

        #write the qr size to a file
        with open("conv_factor.txt", "w") as f:
            f.write(str(conv_factor))

        print("Conversion factor (cm/pxl) saved to conv_factor.txt")


        

if __name__ == "__main__":
    main(use_roi=True, scale_factor=0.5)

