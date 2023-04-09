# RaspberryPi-Smart-Car
## Bachelor Degree Project

### Tasks Backlog
#### Mandatory
- [X] Build the car
- [X] Build a post for the camera
- [X] Make the car go front, back, left and right using the keyboard
- [X] Make the opencv framework work on the raspberry pi
- [X] Create a python class for streaming video over a socket
- [X] Create a python class for image processing
- [X] Create a python class for the motors controller 
- [X] Access the rpi physically and test if the camera can display video in real time
- [X] Establish a client server connection between rpi and pc
- [X] Stream video to pc 
- [X] Create a config class for storing constant variables
- [X] Try to reduce motion blur by increasing the frame rate
- [X] Resize output image 
- [X] Detect lines using OpenCV
- [X] Change the line detection algorithm to contour finding 
- [X] Create a simple PID Controller that changes the direction of the robot from the camera input
- [ ] Create a logging system 
- [ ] Setup the python debugger for VSCode
- [ ] Create a new track layout that is the size of 2 A0 sheets
- [ ] Implement the sliding window approach for the Lane Detection 
    - Optimize the Line class by adding the length attribute
    - Create the Point class to optimize code
    - Add region of interest
    - Choose the correct camera position
    - Add perspective warp
    - Split the line contours into multiple points
- [ ] Tune the PID Controller

#### Optional
- [ ] Try to create timer interrupts
- [ ] Speed up image processing and image transmission by using threads
- [ ] Investigate convex hull algorithm
- [ ] Investigate houghlines algorithm