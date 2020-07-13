# Import the needed libraries
import time
from threading import Thread

import cv2


class Camera:
    def __init__(self, camera_type=0, device_id=0, source="localhost:8080", flip=0, width=640, height=480, fps=30,
                 enforce_fps=False, debug=False):
        # initialize all variables
        self.fps = fps
        self.camera_type = camera_type
        self.camera_id = device_id
        # for streaming camera only
        self.camera_location = source
        self.flip_method = flip
        self.width = width
        self.height = height
        self.enforce_fps = enforce_fps

        self.debug_mode = debug
        # track error value
        '''
        -1 = Unknown error
        0 = No error
        1 = Error: Could not initialize camera.
        2 = Thread Error: Could not read image from camera
        3 = Error: Could not read image from camera
        4 = Error: Could not release camera
        '''
        # Need to keep an history of the error values
        self.__error_value = [0]

        # created a thread for enforcing FPS camera read and write
        self.cam_thread = None
        # holds the frame data
        self.frame = None

        # tracks if a CAM opened was succesful or not
        self.__cam_opened = False

        # create the OpenCV camera inteface
        self.cap = None

        # open the camera interface
        self.open()
        # enable a threaded read if enforce_fps is active
        if self.enforce_fps:
            self.start()

    def __csi_pipeline(self, sensor_id=0):
        return ('nvarguscamerasrc sensor-id=%d ! '
                'video/x-raw(memory:NVMM), '
                'width=(int)%d, height=(int)%d, '
                'format=(string)NV12, framerate=(fraction)%d/1 ! '
                'nvvidconv flip-method=%d ! '
                'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink' % (sensor_id,
                                                               self.width, self.height, self.fps, self.flip_method,
                                                               self.width, self.height))

    def __usb_pipeline(self, device_name="/dev/video1"):
        return ('v4l2src device=%s ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'format=(string)YUY2, framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % (device_name, self.width, self.height, self.fps))

    def __rtsp_pipeline_bak(self, location="localhost:8080"):
        return ('rtspsrc location=%s latency=0 ! '
                'rtph264depay ! h264parse ! omxh264dec ! '
                'videorate ! videoscale ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'format=(string)YUY2, framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % ("rtsp://" + location, self.width, self.height, self.fps))

    def __rtsp_pipeline(self, location="localhost:8080"):
        return ('rtspsrc location=%s ! '
                'rtph264depay ! h264parse ! omxh264dec ! '
                'videorate ! videoscale ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % ("rtsp://" + location, self.width, self.height, self.fps))

    def __mjpeg_pipeline(self, location="localhost:8080"):
        return ('souphttpsrc location=%s do-timestamp=true is_live=true ! '
                'multipartdemux ! jpegdec ! '
                'videorate ! videoscale ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % ("http://" + location, self.width, self.height, self.fps))

    def __usb_pipeline_enforce_fps(self, device_name="/dev/video1"):
        return ('v4l2src device=%s ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'format=(string)YUY2, framerate=(fraction)%d/1 ! '
                'videorate ! '
                'video/x-raw, framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % (device_name, self.width, self.height, self.fps, self.fps))

    def open(self):
        # open the camera inteface
        # determine what type of camera to open
        if self.camera_type == 0:
            # then CSI camera
            self.__open_csi()
        elif self.camera_type == 2:
            # rtsp camera
            self.__open_rtsp()
        elif self.camera_type == 3:
            # http camera
            self.__open_mjpeg()
        else:
            # it is USB camera
            self.__open_usb()
        return self

    def start(self):
        self.cam_thread = Thread(target=self.__thread_read)
        self.cam_thread.daemon = True
        self.cam_thread.start()
        return self

    # Tracks if camera is ready or not(maybe something went wrong)
    def isReady(self):
        return self.__cam_opened

    # Tracks the camera error state.
    def hasError(self):
        # check the current state of the error history
        latest_error = self.__error_value[-1]
        if latest_error == 0:
            # means no error has occured yet.
            return self.__error_value, False
        else:
            return self.__error_value, True

    def __open_csi(self):
        # opens an inteface to the CSI camera
        try:
            # initialize the first CSI camera
            self.cap = cv2.VideoCapture(self.__csi_pipeline(self.camera_id), cv2.CAP_GSTREAMER)
            if not self.cap.isOpened():
                # raise an error here
                # update the error value parameter
                self.__error_value.append(1)
                raise RuntimeError()
            self.__cam_opened = True
        except RuntimeError:
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError('Error: Could not initialize CSI camera.')
        except Exception:
            # some unknown error occurred
            self.__error_value.append(-1)
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError("Unknown Error has occurred")

    def __open_usb(self):
        # opens an interface to the USB camera
        try:
            # initialize the USB camera
            self.camera_name = "/dev/video" + str(self.camera_id)
            # check if enforcement is enabled
            if self.enforce_fps:
                self.cap = cv2.VideoCapture(self.__usb_pipeline_enforce_fps(self.camera_name), cv2.CAP_GSTREAMER)
            else:
                self.cap = cv2.VideoCapture(self.__usb_pipeline(self.camera_name), cv2.CAP_GSTREAMER)
                if not self.cap.isOpened():
                    # raise an error here
                    # update the error value parameter
                    self.__error_value.append(1)
                    raise RuntimeError()
            self.__cam_opened = True
        except RuntimeError:
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError('Error: Could not initialize USB camera.')
        except Exception:
            # some unknown error occurred
            self.__error_value.append(-1)
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError("Unknown Error has occurred")

    def __open_rtsp(self):
        # opens an interface to the RTSP location
        try:
            # starts the rtsp client
            self.cap = cv2.VideoCapture(self.__rtsp_pipeline(self.camera_location), cv2.CAP_GSTREAMER)
            if not self.cap.isOpened():
                # raise an error here
                # update the error value parameter
                self.__error_value.append(1)
                raise RuntimeError()
            self.__cam_opened = True
        except RuntimeError:
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError('Error: Could not initialize RTSP camera.')
        except Exception:
            # some unknown error occurred
            self.__error_value.append(-1)
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError("Unknown Error has occurred")

    def __open_mjpeg(self):
        # opens an interface to the MJPEG location
        try:
            # starts the MJEP client
            self.cap = cv2.VideoCapture(self.__mjpeg_pipeline(self.camera_location), cv2.CAP_GSTREAMER)
            if not self.cap.isOpened():
                # raise an error here
                # update the error value parameter
                self.__error_value.append(1)
                raise RuntimeError()
            self.__cam_opened = True
        except RuntimeError:
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError('Error: Could not initialize MJPEG camera.')
        except Exception:
            # some unknown error occurred
            self.__error_value.append(-1)
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError("Unknown Error has occurred")

    def __thread_read(self):
        # uses thread to read
        time.sleep(1.5)
        while self.__cam_opened:
            try:
                self.frame = self.__read()

            except Exception:
                # update the error value parameter
                self.__error_value.append(2)
                self.__cam_opened = False
                if self.debug_mode:
                    raise RuntimeError('Thread Error: Could not read image from camera')
                break
        # reset the thread object:
        self.cam_thread = None

    def __read(self):
        # reading images
        ret, image = self.cap.read()
        if ret:
            return image
        else:
            # update the error value parameter
            self.__error_value.append(3)

    def read(self):
        # read the camera stream
        try:
            # check if debugging is activated
            if self.debug_mode:
                # check the error value
                if self.__error_value[-1] != 0:
                    raise RuntimeError("An error as occurred. Error Value:", self.__error_value)
            if self.enforce_fps:
                # if threaded read is enabled, it is possible the thread hasn't run yet
                if self.frame is not None:
                    return self.frame
                else:
                    # we need to wait for the thread to be ready.
                    return self.__read()
            else:
                return self.__read()
        except Exception as ee:
            if self.debug_mode:
                raise RuntimeError(ee.args)

    def release(self):
        # destroy the opencv camera object
        try:
            # update the cam opened variable
            self.__cam_opened = False
            # ensure the camera thread stops running
            if self.enforce_fps:
                if self.cam_thread is not None:
                    self.cam_thread.join()
            if self.cap is not None:
                self.cap.release()
            # update the cam opened variable
            self.__cam_opened = False
        except RuntimeError:
            # update the error value parameter
            self.__error_value.append(4)
            if self.debug_mode:
                raise RuntimeError('Error: Could not release camera')
