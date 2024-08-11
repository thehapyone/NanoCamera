"""
Using the NanoCamera with USB Cameras and Debugging Enabled
@author: Ayo Ayibiowu

"""

# from nanocamera.NanoCam import Camera
import nanocamera as nano

if __name__ == '__main__':
	# you can see connected USB cameras by running : ls /dev/video* on the terminal
	# for usb camera /dev/video2, the device_id will be 2

	# Create the Camera instance
	try:
		# Create the Camera instance
		print("camera stream")
		camera = nano.Camera(camera_type=nano.USB, device_id=0, width=640, height=480, fps=30, debug=True)
	except Exception as e:
		print("Exception occurred ------ ")
		print("Exception Type - ", e)

	else:
		print('USB Camera ready? - ', camera.isReady())
		while True:
			try:
				# read the camera image
				frame = camera.read()
				print("do something with frame")
			# send_to_cloud(frame)
			# display the frame
			# cv2.imshow("Video Frame", frame)
			# if cv2.waitKey(25) & 0xFF == ord('q'):
			#    break
			except KeyboardInterrupt:
				break
			except Exception as e:
				print("Exception occurred in Reading ------ ")
				print("Exception Type - ", e)
				print(camera.hasError())
				break

		print("done here")
		try:
			# close the camera instance
			camera.release()
		except Exception as e:
			print("Release Exception")
			print("Exception type - ", e)

		# remove camera object
		del camera
