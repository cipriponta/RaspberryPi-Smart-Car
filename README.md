# Lane Keeping System

This system requires a Raspberry Pi 4 board or an equivalent SBC that can run python and OpenCV. 
Moreover, the processed images captured by the camera can be viewed via a socket on another computer.
In order to have a communication session using sockets, the Raspberry Pi 4 and the computer need to be connected to the same LAN. This can be done using a router.

What to install on both systems:
- Python3(if not already installed)
- OpenCV(Python version): run in terminal: pip install opencv-python

How to run:
- Change inside source/constants.py the RPI_IP_ADDRESS to the one assigned by your router.
- Connect to Raspberry Pi via SSH, cd to this repository and run: python source/main_rpi.py (optional: --debug --stand).
- Connect to another machine in order to view the processed output, cd to this repository and run: python source/main_pc.py.

Video Demo: https://www.youtube.com/watch?v=zEGgocpqRnU