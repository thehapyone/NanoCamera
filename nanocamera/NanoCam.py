# Import the needed libraries
import cv2


class Camera:
    def __init__(self, camera_type=0, device_id=1, flip=0, width=640, height=480, fps=24, enforce_fps=False):
        # initialize all variables
        self.fps = fps
        self.camera_type = camera_type
        self.camera_id = device_id
        self.flip_method = flip
        self.width = width
        self.height = height
        self.enforce_fps = enforce_fps

        # tracks if a CAM opened was succesful or not
        self.__cam_opened = False

        # create the OpenCV camera inteface
        self.cap = None

        # open the camera interface
        self.open()

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
        else:
            # it is USB camera
            self.__open_usb()

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
            frame = self.__read()
            return frame
        except RuntimeError:
            raise RuntimeError('Error: Could not read image from camera')

    def release(self):
        # destroy the opencv camera object
        try:
            if self.cap is not None:
                self.cap.release()
            # update the cam opened variable
            self.__cam_opened = False
        except RuntimeError:
            raise RuntimeError('Error: Could not release camera')
