import sys
import time
import argparse
from IRBGrab import isirgrab as grab
import cv2


if __name__ == '__main__': 
    parser = argparse.ArgumentParser("python main.py", description='Grab frame from IRBIS IR Camera and send them to "Spout" (texture sharing memory)',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--device', '-s', help="Device name to grab from", type=str, default="variocamhd")
    parser.add_argument('--min_t', help="Mininum temperature (°C)", type=float, default=25.)
    parser.add_argument('--max_t', help="Maximum temperature (°C)", type=float, default=36.)
    args = parser.parse_args()
    device_name = args.device
    min_t = args.min_t
    max_t = args.max_t

    try:
        i = grab.IsirIrbGrab(min_t, max_t) # In degrees
        i.load_dll()
        i.create_device(device_name)
        print(f"Grabbing : {device_name}")
        #i.create_device("simulator")
        i.connect()
        
        try:
            print("--- Press CTRL+C to exit ---")
            while True:
                time.sleep(1/30)
                if i.frame_ir_ok:
                    cv2.imshow("IR", i.frame_ir); 
                if cv2.waitKey(1) & 0xFF == ord('q'): break
        except KeyboardInterrupt:
            pass

        cv2.destroyAllWindows()
        i.disconnect()
        i.free_device()
        i.free_dll()
    except Exception as e:
        print(e)
        

