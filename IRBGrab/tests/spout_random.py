import SpoutGL
from itertools import islice, cycle
import time
from OpenGL import GL
import numpy as np
import cv2 as cv

#768, 1024
TARGET_FPS = .2
SEND_WIDTH = 10
SEND_HEIGHT = 10
SENDER_NAME = "SpoutGL-test"

def sendRGB8():
    pixels = np.random.random_sample((SEND_HEIGHT, SEND_WIDTH, 3))
    return sender.sendImage(pixels, SEND_WIDTH, SEND_HEIGHT, GL.GL_RGB, True, 0)

def sendUINT32():
    mat = np.ones((SEND_HEIGHT, SEND_WIDTH, 3), dtype=np.uint32)
    r = np.random.randn(SEND_HEIGHT, SEND_WIDTH).astype(np.uint32)
    r = r[:,:, np.newaxis, np.newaxis, np.newaxis]
    res = r
    #res = res[:, np.newaxis]
    #res.reshape(SEND_HEIGHT, SEND_WIDTH, 3)
    #print(res.shape)
    return sender.sendImage(res, SEND_WIDTH, SEND_HEIGHT, GL.GL_RGB, True, 0)

def sendFloat32():
    r = np.random.normal(.5,.1,size=(SEND_HEIGHT, SEND_WIDTH)).astype(np.float32)
    print(r.dtype)
    r *= 255
    r = r[:, :, np.newaxis].astype(np.uint8)
    # print(frame.shape, frame.dtype)
    frame = cv.cvtColor(r, cv.COLOR_GRAY2RGB)
    res = frame
    #res = res[:, np.newaxis]
    #res.reshape(SEND_HEIGHT, SEND_WIDTH, 3)
    #print(res.shape)
    return sender.sendImage(res, SEND_WIDTH, SEND_HEIGHT, GL.GL_RGB, True, 0)

with SpoutGL.SpoutSender() as sender:
    sender.setSenderName(SENDER_NAME)

    while True:
        # Generating bytes in Python is very slow; ideally you should pass in a buffer obtained elsewhere
        # or re-use an already allocated array instead of allocating one on the fly
        #pixels = bytes(islice(cycle([randcolor(), randcolor(), randcolor(), 255]), SEND_WIDTH * SEND_HEIGHT * 4))
        #result = sender.sendImage(pixels, SEND_WIDTH, SEND_HEIGHT, GL.GL_RGB, True, 0)
        #print("Send result", result)

        #sendRGB8()
        #sendUINT32()
        sendFloat32()


        # Indicate that a frame is ready to read
        sender.setFrameSync(SENDER_NAME)

        # Wait for next send attempt
        time.sleep(1. / TARGET_FPS)