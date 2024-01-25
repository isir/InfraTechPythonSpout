import numpy as np
import cv2 as cv

size = 100
shape = [size,size]
r = np.linspace(0,60000,size*size, dtype=np.uint32).reshape(size,size)
#print(r[0][1])
#print(x.shape)
dt=np.dtype((np.int32, {'r':(np.uint8,0),'g':(np.uint8,1),'b':(np.uint8,2), 'a':(np.uint8,3)}))

img= r.view(dtype=[('r', np.uint8), ('g', np.uint8), ('b', np.uint8), ('a', np.uint8)])
img = np.array([img['r'],img['g'],img['b']]).reshape(size,size,3)
#print(img.shape)
#print(img[0][1])

x_min = 0
x_max = 60000
y_min = 0 
y_max = 60000
Nx = size #number of steps for x axis
Ny = size #number of steps for y axis

x = np.linspace(x_min, x_max, Nx)
y = np.linspace(y_min, y_max, Ny)

#Can then create a meshgrid using this to get the x and y axis system
xx, yy = np.meshgrid(x, y)


uv = np.dstack((xx*0,yy,xx))/y_max
print(uv.shape, uv.dtype)

while True:
    cv.imshow("UV", uv)
    cv.imshow("img", img)
    k = cv.waitKey(33)
    if k==27 or k == ord('q'):    # Esc key to stop
        break