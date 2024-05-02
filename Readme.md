# Reespiration - FaceAnalysis module

## Installation 
- Install [Python 3.11]
- Create python virtual environment `python -m venv venv`
- Activate it `venv/Scripts/activate`
- Install python requirements `pip install -r requirements.txt`


## Usage
In your virtual environment run `python main.py`

It should output:
```Capture range from T 25.0 (298.15 K) to 36.0 (309.15 K)
Loading dll...
True
standard rel. path import scheme
SDK Program Files import scheme
<WinDLL 'C:\Program Files\InfraTec\IRBGRAB_SDK\v4\irbgrab_win64.dll', handle 110000000 at 0x154e1f099d0>
Found camera: simulator
Found camera: variocamhd
```

It connects to IRBIS camera and shared IR stream as  [Spout shared texture](https://leadedge.github.io/) named "IR" by default, then it sends live facetracking data for the closest face ([68 face landmarks](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10066970/) as 3D points, 3D pose, age, male, frame_shape of the received texture and a face_found boolean) through [OSC protocol](https://en.wikipedia.org/wiki/Open_Sound_Control) (localhost:10000 by default)

When successful, it shows the texture stream with the 68 face landmarks overlaid in blue.

Press 'q' or 'escape' to quit.

