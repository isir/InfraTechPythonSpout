import numpy as np
import cv2 as cv

frame = np.load("frame_uint32.npy")

while True:
    cv.imshow("UV", uv)
    cv.imshow("img", img)
    k = cv.waitKey(33)
    if k==27 or k == ord('q'):    # Esc key to stop
        break