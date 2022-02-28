import cv2 as cv
import SpoutGL
from OpenGL import GL



# define a video capture object
vid = cv.VideoCapture(0)
sender = SpoutGL.SpoutSender()
sender.setSenderName("SpoutGL-test")
print("Spout stream to: SpoutGL-test")
while True:

    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    frame_width = int(vid.get(3))
    frame_height = int(vid.get(4))
    # Display the resulting frame
    cv.imshow('frame', frame)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    sender.sendImage(frame, frame_width, frame_height, GL.GL_RGB, False, 1)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv.destroyAllWindows()