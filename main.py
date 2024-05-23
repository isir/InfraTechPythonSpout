import sys
import time
import argparse
from IRBGrab import isirgrab as grab
from pythonosc import udp_client
import cv2

def getArgsStr(args:argparse.Namespace) -> str:
    res = ""
    for i, arg in enumerate(vars(args)):
        if i==0:
            res += f"{arg}: {getattr(args, arg)}"
        else:
            res += f", {arg}: {getattr(args, arg)}"
    return res

def main(argv):
    parser = argparse.ArgumentParser("python main.py", description='Grab frame from IRBIS IR Camera and send them to "Spout" (texture sharing memory)',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--device', '-s', help="Device name to grab from", type=str, default="variocamhd")
    parser.add_argument('--min_t', help="Mininum temperature (°C)", type=float, default=25.)
    parser.add_argument('--max_t', help="Maximum temperature (°C)", type=float, default=36.)
    parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=10000, help="The port the OSC server is listening on")
    
    args = parser.parse_args()
    device_name = args.device
    min_t = args.min_t
    max_t = args.max_t
    osc_client = udp_client.SimpleUDPClient(args.ip, args.port)
    frameid = 0

    try:
        i = grab.IsirIrbGrab(min_t, max_t) # In degrees
        i.load_dll()
        i.create_device(device_name)
        print(f"Grabbing : {device_name}")
        #i.create_device("simulator")
        i.connect()
        spout_name = i.getSpoutName(0)
        print("-------------------")
        print("Launched with options:", getArgsStr(args))
        try:
            print("--- Press CTRL+C to exit ---")
            while True:
                time.sleep(1/30)
                if i.frame_ir_ok:
                    frame = cv2.putText(i.frame_ir, f"Sharing to spout {spout_name}, T min {min_t}, max {max_t}",
                                              (20, 20) , cv2.FONT_HERSHEY_SIMPLEX ,  0.35, (250, 250, 250), 1, cv2.LINE_AA) 
                    cv2.putText(frame, "Press Q to quit", (20, 40) , cv2.FONT_HERSHEY_SIMPLEX ,  0.35, (250, 250, 250), 1, cv2.LINE_AA) 
                    cv2.imshow("IRBIS_Grap", frame)                    
                    if frameid%50==0:
                        osc_client.send_message("/irbis/min_t", min_t)
                        osc_client.send_message("/irbis/max_t", max_t)
                    osc_client.send_message("/irbis/frameid", frameid); frameid +=1                    
                if cv2.waitKey(1) & 0xFF == ord('q'): break
        except KeyboardInterrupt:
            pass

        cv2.destroyAllWindows()
        i.disconnect()
        i.free_device()
        i.free_dll()
    except Exception as e:
        print(e)

if __name__ == '__main__': 
    main(sys.argv[1:])        

