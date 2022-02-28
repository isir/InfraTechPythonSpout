import sys
import os,time
import ctypes,_ctypes
import threading
import pathlib as pl
# infratec packages
# try importing as namespace package
from enum import Enum

import numpy as np
import cv2 as cv
import SpoutGL
from OpenGL import GL
import ctypes as ct

try:
    from IRBGrab import irbgrab as irbg
    from IRBGrab import hirbgrab as hirb
    print('IRBGrab module imported')
except (ImportError, ModuleNotFoundError):
    print('Pb import IRBGrab module')

IRBG_PARAM_SDK_NeedBitmap32 = 181
class IRBG_STREAMTYPE(Enum):
    IRBG_STREAMTYPE_IR = 1
    IRBG_STREAMTYPE_VIS = 2
    IRBG_STREAMTYPE_SCREEN = 3


class STATES(Enum):
    Init = 1
    DLLLoaded = 2
    DeviceCreated = 3
    Connected = 4
    Grabbing = 5

t = time.perf_counter()
tLive = t
lock = threading.Lock()
ev_has_fname = threading.Event()

def callback(context,*args):#, aHandle, aStreamIndex):
    context.updateStreamIR()


class IsirIrbGrab:
    def __init__(self, min, max):
        self.__min = min+273.15
        self.__max = max+273.15
        print(f"Capture range from T {min} ({self.__min} K) to {max} ({self.__max} K)")
        self.__ampl = max-min
        self.__grabIndex = 0
        self.__state = STATES.Init
        self.__cameras = []
        self.__devices = []
        self.__selectedDeviceName = "variocamhd"
        self.__show_window = False
        self.autolevel_checked_val = False
        self.__spouts = {}
        self.__spoutsName = {}
        self.vscale = np.vectorize(self.scale)
        self.frame = None

    def scale(self, v):
        return (v-self.__min)/self.__maxmin

    def load_dll(self):
        if self.__state != STATES.Init:
            print("Can't load DLL at this state")
            return
        print('Loading dll...')
        self.irbgrab_dll = irbg.getDLLHandle()
        self.irbgrab_object = irbg.irbgrab_obj(self.irbgrab_dll)
        inits = self.irbgrab_object.isinit()
        if inits != 0:
            # List available devices
            res = self.irbgrab_object.availabledevices()
            if res[0] == '0x10000001':
                for d in res[1]:
                    self.__cameras.append(d)
                    print(f'Found camera: {d}')
                self.__state = STATES.DLLLoaded
            else:
                raise Exception('Loading dll Failed to list devices')
        else:
            raise Exception('Loading dll Failed to init')

    def free_dll(self):
        if self.__state != STATES.DLLLoaded:
            print("Can't free_dll at this state")
            return
        print('free_dll...')
        try:
            self.__cameras.clear()
            del self.irbgrab_object
            _ctypes.FreeLibrary(self.irbgrab_dll._handle)
            del self.irbgrab_dll
            print('Free_dll ok')
            self.__state = STATES.Init
        except:
            print('Free_dll Failed')

    def create_device(self, name="variocamhd" ):
        if self.__state != STATES.DLLLoaded:
            print("Can't create_device at this state")
            return
        nr_device = self.__cameras.index(name)
        if nr_device != -1:
            res = self.irbgrab_object.create(nr_device, '')
            if hirb.TIRBG_RetDef[res] == 'Success':
                res = self.irbgrab_object.search()
                success = False
                if hirb.TIRBG_RetDef[res[0]] == 'Success':
                    #                    if res[1]!=0:
                    if True:
                        success = True
                        self.searchstrings = self.irbgrab_object.get_search_strings()
                        for i in self.searchstrings: self.__devices.append(i)
                    else:
                        print('create_device: No Device Available!')
                elif hirb.TIRBG_RetDef[res[0]] == 'NotSupported':
                    success = True  # For Simulator
                else:
                    print('create_device: search error: ' + hirb.TIRBG_RetDef[res[0]])
                if success:
                    print('create_device: Done')
                    self.__selectedDeviceName = name
                    self.__state = STATES.DeviceCreated
            else:
                raise Exception('create_device error: ' + hirb.TIRBG_RetDef[res])
        else:
            raise Exception('No Device DLL Available!')

    def free_device(self):
        if self.__state != STATES.DeviceCreated:
            print("Can't create_device at this state")
            return
        res = self.irbgrab_object.free()
        self.__devices.clear()
        if hirb.TIRBG_RetDef[res] == 'Success':
            print('free_device: Done')
            self.__state = STATES.DLLLoaded
        else:
            print('free_device: Failed')

    def initSpout(self, name, index):
        self.__spoutsName[index] = name
        self.__spouts[index] = SpoutGL.SpoutSender()
        self.__spouts[index].setSenderName(name)
        print(f"Spout stream {index} to: {name}")

    def connect(self):
        if self.__state != STATES.DeviceCreated:
            print("Can't connect at this state")
            return
        # known bug comes back with an error. res=self.irbgrab_object.get_state()
        # workaround for this version is to simply set to irbg.TIRBG_RetDef[res]=='Running' and ignore getstate
        res='0x20000004'
        if hirb.TIRBG_RetDef[res] == 'Running' or hirb.TIRBG_RetDef[res] == 'NotSupported':
            if len(self.__devices) > 0:
                print(f"Connecting to: {self.__devices[0]}")
                res = self.irbgrab_object.connect(self.__devices[0])
            else:
                res = self.irbgrab_object.connect('')
            if hirb.TIRBG_RetDef[res] == 'Success':
                res = self.irbgrab_object.set_callback_func(callback, self)
                if hirb.TIRBG_RetDef[res] == 'Success':
                    self.__state = STATES.Connected
                    self.grab(0)
                    #self.irbgrab_object.setparam_int32(181, 1); self.grab(1)
                else:
                    raise Exception('set callback error: ' + hirb.TIRBG_RetDef[res])
            else: raise Exception('connect error: '+hirb.TIRBG_RetDef[res])
        else: raise Exception('state error: '+hirb.TIRBG_RetDef[res])

    def grab(self, index):
        if self.__state not in (STATES.Connected, STATES.Grabbing):
            print("Can't grab at this state")
            return
        res = self.irbgrab_object.startgrab(index)
        if hirb.TIRBG_RetDef[res] == 'Success':
            self.initSpout(f"{self.__selectedDeviceName}_{index}", index)
            print(f'Grabbing stream {index}')
            self.__state = STATES.Grabbing
            #print("NeedBitmap32: ", self.irbgrab_object.setparam_int32(IRBG_PARAM_SDK_NeedBitmap32, 1))
        else:
            raise Exception('startgrab error: ' + hirb.TIRBG_RetDef[res])

    def disconnect(self):
        if self.__state != STATES.Connected:
            print("Can't disconnect at this state")
            return
        res = self.irbgrab_object.stopgrab(self.__grabIndex)

        if hirb.TIRBG_RetDef[res] == 'Success':
            res = self.irbgrab_object.disconnect()
            if hirb.TIRBG_RetDef[res] == 'Success':
                self.__state = STATES.DeviceCreated
            else:
                print('disconnect error: '+hirb.TIRBG_RetDef[res])
        else:
            print('stopgrab error: '+hirb.TIRBG_RetDef[res])

    def updateStreamIR(self):
        if self.__state != STATES.Grabbing:
            print("Can't updateStreamIR at this state")
            return

        global t
        global tLive
        now = time.perf_counter()
        # print(now-t)
        t = now

        #streamCount = self.irbgrab_object.getparam_int32(hirb.IRBG_PARAM_Stream_Count); print(f"streamCount: {streamCount}")

        # handle every image
        try:
            res = self.irbgrab_object.get_data_easy_noFree(3) #1:uint32, 2:uint16, 3:float32,4:uint8
            #res2 = self.irbgrab_object.get_dataex(1)
        except Exception as e:
            print(f"Exception get_data_easy_noFree():\n{e}")
            return

        # stream image
        if res[0] in hirb.TIRBG_RetDef.keys():
            if hirb.TIRBG_RetDef[res[0]] == 'Success' and len(res) >= 2 and res[1].shape[0] > 100:
                if lock.acquire(False):
                    if (t - tLive) > 0.04:  # 0.04
                        frame = res[1]
                        #print(frame.min(), frame.max())
                        frame = (frame-self.__min)/self.__ampl
                        frame = np.clip(frame, 0, 1)*255

                        frame = frame[:, :, np.newaxis].astype(np.uint8)
                        #print(frame.shape, frame.dtype)
                        frame = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)
                        self.frame = frame
                        self.__spouts[0].sendImage(frame, frame.shape[1], frame.shape[0], GL.GL_RGB, False, 1)#(768, 1024)
                        tLive = t
                    #else: print('Too slow')
                    try:
                        self.irbgrab_object.free_mem()
                    except Exception as e:
                        pass#print("Exception while freeing memory: ", e)

                    lock.release()
                # DEBUG
                #print('memory freed')
            else:
                print('Error when getting image: {}'.format(hirb.TIRBG_RetDef[res[0]]))


if __name__ == '__main__':
    #i = IsirIrbGrab(10000000, 17000000) #numerical raw
    i = IsirIrbGrab(25., 35.) # In degrees
    i.load_dll()
    i.create_device("variocamhd")
    i.connect()
    while True:
        #time.sleep(.033)
        i.updateStreamIR()
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    i.disconnect()
    i.free_device()
    i.free_dll()
