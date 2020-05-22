"""
Using the NanoCamera with RTSP Source Cameras
@author: Ayo Ayibiowu

"""

import cv2

# from nanocamera.NanoCam import Camera
import nanocamera as nano

if __name__ == '__main__':
    # requires the RTSP location. Something like this: rtsp://localhost:8888/stream
    # For RTSP camera, the camera_type=2.
    # This only supports H.264 codec for now

    # a location for the rtsp stream
    rtsp_location = "192.168.1.26:8554/stream"
    # Create the Camera instance
    camera = nano.Camera(camera_type=2, source=rtsp_location, width=640, height=480, fps=30)
    print('RTSP Camera is now ready')
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
