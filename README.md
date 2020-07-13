# NanoCamera [![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/thehapyone/NanoCamera/blob/master/LICENSE)
A simple to use camera interface for the Jetson Nano for working with USB, CSI, IP and also RTSP cameras or streaming video in Python 3.

It currently supports the following types of camera or streaming source:
*  Works with CSI Cameras (Tested and Works)
*  Works with various USB cameras (Tested with Logitech USB camera)
*  Works with RTSP streaming camera and video with hardware acceleration (only supports H.264 video codec)
*  Works with IP Cameras(JPEG codec) or any MJPEG streaming source (Currently, supports CPU acceleration. TODO: Hardware acceleration)

## Features
* It is OpenCV ready. Image file can be called directly with OpenCV imshow
* Image file is a numpy RGB array.
* Support different Camera Flip Mode (Counterclockwise, Rotate 180 degress, Clockwise - 90 degrees, Horizontal Flip, Vertical Flip)
* Can be used with multiple cameras.
* Support Frame rate enforcement. *Only available for USB, RTSP, and IP/MJPEG cameras.
* Frame rate enforcement ensures the cameras work at the given frame rate using gstreamer videorate plugin
* It is based on [Accelerated GStreamer Plugins](https://developer.download.nvidia.com/embedded/L4T/r32_Release_v1.0/Docs/Accelerated_GStreamer_User_Guide.pdf?uIzwdFeQNE8N-vV776ZCUUEbiJxYagieFEqUoYFM9XSf9tbslxWqFKnVHu8erbZZS20A7ADAIgmSQJvXZTb0LkuGl9GoD5HJz4263HcmYWZW0t2OeFSJKZOfuWZ-lF51Pva2DSDtu2QPs-junm7BhMB_9AMQRwExuDb5zIhf_o8PIbA4KKo)
* Should work with other Jetson boards like Jetson TX1, TX2 and others (Not tested)
* Support both Hardware and CPU acceleration.
* Easily read images as ``numpy`` arrays with ``image = camera.read()``
* Supports threaded read - available to all camera types. To enable a fast threaded read, you will to enable the enforce_fps: ``enforce_fps = True``
* Check the status of the camera after initialization with ``isReady()`` function. Returns ``True`` if ready and ``False`` if otherwise.
* Provide debugging support. Added error codes and an optionally exception handling. See example in [Debugging](https://github.com/thehapyone/NanoCamera#debugging). Now you can restart the camera if somethings goes wrong or send an admin notice if your camera goes down.
* Support multiple CSI cameras using the ``device_id`` parameter. See examples.

## Requirements
This library requires OpenCV to be installed to work.
If you don't have OpenCV, you can install one with pip:
```bash
pip3 install opencv-python 
```

## Install
Installation is simple. Can be installed in two ways with Pip or Manually.
##### Pip Installation
```bash
pip3 install nanocamera 
```
##### Manual Installation
```bash
git clone https://github.com/thehapyone/NanoCamera
cd NanoCamera
sudo python3 setup.py install
```

## Usage & Example
Using NanoCamera is super easy. Below we show some usage examples.  You can find more in the [examples](https://github.com/thehapyone/NanoCamera/tree/master/examples).
### Working with CSI Camera
For CSI Cameras, the ``camera_type = 0``.

Find here for full [CSI camera example](https://github.com/thehapyone/NanoCamera/tree/master/examples/CSI_camera.py)

Python Example - 
Create CSI camera using default FPS=30, default image size: 640 by 480 and with no rotation (flip=0)
```python
import nanocamera as nano
# Create the Camera instance for 640 by 480
camera = nano.Camera()
```
Customizing the width and height
```python
import nanocamera as nano
# Create the Camera instance for No rotation (flip=0) with size of 1280 by 800
camera = nano.Camera(flip=0, width=1280, height=800, fps=30)
```
if image is inverted, set ``flip = 2``

#### Multiple CSI Camera support.
For Multiple CSI Cameras, set the ``device_id`` to the ID of the camera. 
```python
import nanocamera as nano
# Create the Camera instance for No rotation (flip=0) with size of 1280 by 800
# Connect to CSI camera with ID 0 (Default)
camera_1 = nano.Camera(device_id=0, flip=0, width=1280, height=800, fps=30)
# Connect to another CSI camera on the board with ID 1
camera_2 = nano.Camera(device_id=1, flip=0, width=1280, height=800, fps=30)
```

### Working with USB Camera
For USB Cameras, set the ``camera_type = 1``, and set the ``device_id`` as well.
Find here for full [USB camera example](https://github.com/thehapyone/NanoCamera/tree/master/examples/USB_camera.py)

Python Example - 
Create USB camera connected to ``/dev/video1``

```python
import nanocamera as nano
# Create the Camera instance for No rotation (flip=0) with size of 640 by 480
camera = nano.Camera(camera_type=1, device_id=1, width=640, height=480, fps=30)
```

You can see connected USB cameras by running : 
```bash
ls /dev/video*
```
    # for usb camera /dev/video2, the device_id will be 2

### Working with RTSP streaming camera or streaming video
For RTSP source, set the ``camera_type = 2``, and set the ``source`` as well.
Find here for full [RTSP camera example](https://github.com/thehapyone/NanoCamera/tree/master/examples/RTSP_camera.py)

Python Example - 
Create RTSP receiving camera client. RTSP location example:  ``rtsp://192.168.1.26:8554/stream``

```python
# a location for the rtsp stream. Stream location without "rtsp://"
rtsp_location = "192.168.1.26:8554/stream"
# Create the Camera instance
camera = nano.Camera(camera_type=2, source=rtsp_location, width=640, height=480, fps=30)
```

### Working with IP or any MJPEG streaming camera or video
For IP/MJPEG Cameras, set the ``camera_type = 3``, and set the streaming ``source`` as well.
Find here for full [MJPEG camera example](https://github.com/thehapyone/NanoCamera/tree/master/examples/MJPEG_camera.py)

Python Example - 
Create IP camera client connected to a camera streaming to ``http://192.168.1.26:80/stream``

```python
# a location for the camera stream. Stream location without "http://"
camera_stream = "192.168.1.26:80/stream"
# Create the Camera instance
camera = nano.Camera(camera_type=3, source=camera_stream, width=640, height=480, fps=30)
```

### Frame Rate Enforcement
Enable frame rate enforcement i.e force the camera to work at the given frame rate
```python
import nanocamera as nano
# enforce the capture frame rate with the enforce_fps=True
camera = nano.Camera(camera_type=1, device_id=1, width=640, height=480, fps=30, enforce_fps=True)
```
### Reading Camera

Call ``read()`` to read the latest image as a ``numpy.ndarray``. The color format is ``BGR8``.

```python
frame = camera.read()
```

A Simple program to read from the CSI camera and display with OpenCV
```python
import cv2
#from nanocamera.NanoCam import Camera
import nanocamera as nano

if __name__ == '__main__':
    # Create the Camera instance
    camera = nano.Camera(flip=0, width=640, height=480, fps=30)
    print('CSI Camera is now ready')
    while True:
        try:
            # read the camera image
            frame = camera.read()
            # display the frame
            cv2.imshow("Video Frame", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        except KeyboardInterrupt:
            break

    # close the camera instance
    camera.release()

    # remove camera object
    del camera
```

A Simple program to read from the IP/MJPEG camera and display with OpenCV
```python
import cv2

# from nanocamera.NanoCam import Camera
import nanocamera as nano

if __name__ == '__main__':
    # requires the Camera streaming url. Something like this: http://localhost:80/stream
    # For IP/MJPEG camera, the camera_type=3.
    # This works with only camera steaming MJPEG format and not H.264 codec for now

    # a location for the camera stream
    camera_stream = "192.168.1.26:80"

    # Create the Camera instance
    camera = nano.Camera(camera_type=3, source=camera_stream, width=640, height=480, fps=30)
    print('MJPEG/IP Camera is now ready')
    while True:
        try:
            # read the camera image
            frame = camera.read()
            # display the frame
            cv2.imshow("Video Frame", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        except KeyboardInterrupt:
            break

    # close the camera instance
    camera.release()

    # remove camera object
    del camera
```

## Debugging

The library has some debugging builtin in to manage errors and exception that might occured during the camera acquistion. 
 - Using the "debug" variable to raise exceptions when an error occured. 
 - Using the HasError to read current error state of the camera with or without debug enabled.
 

## See also

- [Platooning Robot](https://github.com/thehapyone/Platooning-Robot) - Resources for building collaborative robots