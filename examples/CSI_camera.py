import cv2

from nanocamera.NanoCam import Camera

if __name__ == '__main__':
    # Create the Camera instance
    camera = Camera(flip=0, width=640, height=480, fps=30)
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
