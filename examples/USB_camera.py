"""
Using the NanoCamera with USB Cameras
@author: Ayo Ayibiowu

"""

import cv2

# from nanocamera.NanoCam import Camera
import nanocamera as nano

if __name__ == '__main__':
    # you can see connected USB cameras by running : ls /dev/video* on the terminal
    # for usb camera /dev/video2, the device_id will be 2

    # Create the Camera instance
    camera = nano.Camera(camera_type=1, device_id=1, width=640, height=480, fps=30)
    print('USB Camera is now ready')
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
