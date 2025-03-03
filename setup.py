from setuptools import setup, find_packages

setup(
    name="kehe-fl",
    version="0.1.0",
    description="A federated learning package for IoT devices and aggregation server communication.",
    packages=find_packages(),
    install_requires=[
        "paho-mqtt",
    ],
    author="Kevin Hetzenauer",
    author_email="kevin@hetzenauer.me",
    url="https://github.com/ke-he/kehe-fl",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
