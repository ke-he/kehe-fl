import re
from setuptools import setup, find_packages


def get_version():
    with open("kehe_fl/__init__.py", "r") as f:
        return re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="kehe-fl",
    version=get_version(),
    description="A federated learning package for IoT devices and aggregation server communication.",
    packages=find_packages(),
    install_requires=[
        "aiomqtt"
    ],
    author="Kevin Hetzenauer",
    author_email="kevin@hetzenauer.me",
    url="https://github.com/ke-he/kehe-fl",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
