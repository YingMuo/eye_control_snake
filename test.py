import cv2
import eyetrack as ET


vc = cv2.VideoCapture(0)
et = ET.eyeTracker()

while True:
    ret, frame = vc.read()
    if not ret:
        print("video finish")
        break
    
    et.eye_track(frame)
    frame = et.get_output_img()

    cv2.imshow('123', frame)
    if cv2.waitKey(1) == ord('q'):
        break
    # cv2.imwrite('./123.mp4', frame)