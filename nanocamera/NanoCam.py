# Import the needed libraries
import cv2
import time
from threading import Thread


class Camera:
    def __init__(self, camera_type=0, device_id=1, source="localhost:8080", flip=0, width=640, height=480, fps=30,
                 enforce_fps=False):
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

    def __csi_pipeline(self):
        return ('nvarguscamerasrc ! '
                'video/x-raw(memory:NVMM), '
                'width=(int)%d, height=(int)%d, '
                'format=(string)NV12, framerate=(fraction)%d/1 ! '
                'nvvidconv flip-method=%d ! '
                'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink' % (
                    self.width, self.height, self.fps, self.flip_method, self.width, self.height))

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

    def __open_csi(self):
        # opens an inteface to the CSI camera
        try:
            # initialize the first CSI camera
            self.cap = cv2.VideoCapture(self.__csi_pipeline(), cv2.CAP_GSTREAMER)
            self.__cam_opened = True
        except RuntimeError:
            raise RuntimeError('Error: Could not initialize camera.')

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
            self.__cam_opened = True
        except RuntimeError:
            raise RuntimeError('Error: Could not initialize USB camera.')

    def __open_rtsp(self):
        # opens an interface to the RTSP location
        try:
            # starts the rtsp client
            self.cap = cv2.VideoCapture(self.__rtsp_pipeline(self.camera_location), cv2.CAP_GSTREAMER)
            self.__cam_opened = True
        except RuntimeError:
            raise RuntimeError('Error: Could not initialize RTSP camera.')

    def __open_mjpeg(self):
        # opens an interface to the MJPEG location
        try:
            # starts the MJEP client
            self.cap = cv2.VideoCapture(self.__mjpeg_pipeline(self.camera_location), cv2.CAP_GSTREAMER)
            self.__cam_opened = True
        except RuntimeError:
            raise RuntimeError('Error: Could not initialize MJPEG camera.')

    def __thread_read(self):
        # uses thread to read
        time.sleep(1.5)
        while self.__cam_opened:
            try:
                self.frame = self.__read()

            except RuntimeError:
                raise RuntimeError('Thread Error: Could not read image from camera')
        # reset the thread object:
        self.cam_thread = None

    def __read(self):
        # reading images
        ret, image = self.cap.read()
        if ret:
            return image
        else:
            raise RuntimeError('Error: Could not read image from camera')

    def read(self):
        # read the camera stream
        try:
            if self.enforce_fps:
                # if threaded read is enabled, it is possible the thread hasn't run yet
                if self.frame is not None:
                    return self.frame
                else:
                    # we need to wait for the thread to be ready.
                    return self.__read()
            else:
                return self.__read()
        except RuntimeError:
            raise RuntimeError('Error: Could not read image from camera')

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
            raise RuntimeError('Error: Could not release camera')
