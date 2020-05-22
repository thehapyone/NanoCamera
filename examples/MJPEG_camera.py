"""
Using the NanoCamera with MJPEG or IP Cameras
@author: Ayo Ayibiowu

"""

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
    camera = nano.Camera(camera_type=2, source=camera_stream, width=640, height=480, fps=30)
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
