# NanoCamera [![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/thehapyone/NanoCamera/blob/master/LICENSE) [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/thehapyone/nanocamera/issues) [![HitCount](http://hits.dwyl.com/thehapyone/NanoCamera.svg)](http://hits.dwyl.com/thehapyone/NanoCamera)

A simple to use camera interface for the Jetson Nano for working with USB, CSI, IP and also RTSP cameras or streaming video in Python 3.

It currently supports the following types of camera or streaming source:
*  Works with CSI Cameras (Tested and Works)
*  Works with various USB cameras (Tested with Logitech USB camera)
*  Works with RTSP streaming camera and video with hardware acceleration (only supports H.264 video codec)
*  Works with IP Cameras(JPEG codec) or any MJPEG streaming source (Currently, supports CPU acceleration. TODO: Hardware acceleration)

If you like **NanoCamera** library - give it a star, or fork it and contribute!. Updates are always welcomed.

## Features
* It is OpenCV ready. The image file can be called directly with OpenCV imshow
* Image file is a NumPy RGB array.
* Support different Camera Flip Mode (Counterclockwise, Rotate 180 degrees, Clockwise - 90 degrees, Horizontal Flip, Vertical Flip)
* Can be used with multiple cameras.
* Support Frame rate enforcement. *Only available for USB, RTSP, and IP/MJPEG cameras.
* Frame rate enforcement ensures the cameras work at the given frame rate using GStreamer video rate plugin
* It is based on [Accelerated GStreamer Plugins](https://developer.download.nvidia.com/embedded/L4T/r32_Release_v1.0/Docs/Accelerated_GStreamer_User_Guide.pdf?uIzwdFeQNE8N-vV776ZCUUEbiJxYagieFEqUoYFM9XSf9tbslxWqFKnVHu8erbZZS20A7ADAIgmSQJvXZTb0LkuGl9GoD5HJz4263HcmYWZW0t2OeFSJKZOfuWZ-lF51Pva2DSDtu2QPs-junm7BhMB_9AMQRwExuDb5zIhf_o8PIbA4KKo)
* Should work with other Jetson boards like Jetson TX1, TX2 and others (Not tested)
* Support both Hardware and CPU acceleration.
* Easily read images as ``numpy`` arrays with ``image = camera.read()``
* Supports threaded read - available to all camera types. To enable a fast threaded read, you will enable the enforce_fps: ``enforce_fps = True``
* Check the status of the camera after initialization with ``isReady()`` function. Returns ``True`` if ready and ``False`` if otherwise.
* Provide debugging support. Added error codes and an optional exception handling. See example in [Debugging](https://github.com/thehapyone/NanoCamera#debugging). Now you can restart the camera if something goes wrong or send an admin notice if your camera goes down.
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
Create a CSI camera using default FPS=30, default image size: 640 by 480 and with no rotation (flip=0)
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
if the image is inverted, set ``flip = 2``

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
    # for USB camera /dev/video2, the device_id will be 2

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
Create an IP camera client connected to a camera streaming to ``http://192.168.1.26:80/stream``

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

Call ``read()`` to read the latest image as a ``numpy.ndarray``. The color format is ``BGR``.

```python
frame = camera.read()
```

#### Camera isReady?
You can check if the camera is ready for streaming using ``isReady()`` 
```python
status = camera.isReady()
```

A Simple program to read from the CSI camera and display with OpenCV
```python
import cv2
#from nanocamera.NanoCam import Camera
import nanocamera as nano

if __name__ == '__main__':
    # Create the Camera instance
    camera = nano.Camera(flip=0, width=640, height=480, fps=30)
    print('CSI Camera ready? - ', camera.isReady())
    while camera.isReady():
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
    while camera.isReady():
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

The library has some debugging builtin for managing expected, unexpected errors, and exceptions that might occur during the camera acquisition or initialization. 
 - Using the ``debug`` parameter to enable raising of exceptions when an error occurred. This is disabled in the default mode so you won't get any error if something goes wrong.
 - Using the ``hasError()`` to read the current error state of the camera with or without debug enabled.
 
### Errors and Exceptions Handling
Calling ``camere.hasError()`` at any point in time returns a list of error codes and a boolean value:
```python
# status holds a list.
status = camera.hasError()
print (status)
>> ([0, 3], True)
print ("Error codes list : ", status[0])
>> Error codes list : [0, 3]
print ("Error State : ", status[1])
>> Error State: True
```

Error codes are

    '''
    -1 = Unknown error
    0 = No error
    1 = Error: Could not initialize camera.
    2 = Thread Error: Could not read image from camera
    3 = Error: Could not read image from camera
    4 = Error: Could not release camera
    '''

For example:

```python
error_status = camera.hasError()
if error_status[1] == False: # means no error detected so far
    # read the camera image
    frame = camera.read()
    # print the current error codes
    print (error_status[0])
    # display the frame
    cv2.imshow("Video Frame", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
else:
    # an error has occured.
    print ("An error with the camera. Error code : ", error_status[0])

```
 
Enabling the ``debug = True`` parameter allows raising an exception to the main program. This might be useful for parallel computing if you running multiple threads. Without the ``debug`` enabled, your program will continue as normal, and worse if you're enabled the frame rate enforcement which uses the thread read function, you will keep getting image data but those images are old/static images.

See an example using the ``debug`` parameter and handling exceptions at different levels. Find here for full [debugging example](https://github.com/thehapyone/NanoCamera/tree/master/examples/USB_camera_with_debug.py)

```python
if __name__ == '__main__':
    # with debug=True. An Exception will be raised if something goes wrong.
    # Create the Camera instance
    try:
        # Create the Camera instance
        print("camera stream")
        camera = nano.Camera(camera_type=1, device_id=0, fps=30, debug=True)
    except Exception as e:
        # handle the exception from opening camera session
    else:
        print('USB Camera ready? - ', camera.isReady())
        while True:
            try:
                # read the camera image
                frame = camera.read()
                # do something with frame like: send_to_cloud(frame)
            except KeyboardInterrupt:
                break
            except Exception as e:
                # handle the exception from reading
                break
    
        print("done here")
        try:
            # close the camera instance
            camera.release()
        except Exception as e:
            # handle the exception from releasing the camera 

```
If an error occurred, a Runtime Error will be raised catching the following exceptions:
```python
The except cause might catch the following exceptions:
>> Exception Type - Error: Could not initialize USB Camera
>> Exception Type - An error as occurred. Error Value: [0, 3]
>> Exception Type - Unknown Error has occurred
>> Exception Type - Error: Could not release camera
```
Without ``debug`` and even if there is error the program runs as nothing happened. The error can still be detected with the ``hasError()`` function.

## Thanks! & Give it a Star
Thank you for downloading and enjoying the NanoCamera library.
I hope you find it useful. Heck, I wrote it for you- yeah, that's right- you.

Contributing to this software is warmly welcomed. Don't forget to give it a star. 

## License
This project is released under the MIT License.

## See also

- [Platooning Robot](https://github.com/thehapyone/Platooning-Robot) - Resources for building collaborative robots