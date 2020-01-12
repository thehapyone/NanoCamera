from setuptools import setup, find_packages

setup(
	name="NanoCamera",
	version="0.1.0",
	description="A simple to use camera interface for the Jetson Nano for working cameras in Python.",
	packages=find_packages(),
	install_requires=[
		'cv2'],
)
