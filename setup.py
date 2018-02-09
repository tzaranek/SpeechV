"""
SpeechV voice recognition engine.
"""

from setuptools import setup

setup(
    name='voice',
    version='0.1.0',
    packages=['voice'],
    include_package_data=True,
    install_requires=[
        "SpeechRecognition==3.8.1",
        "PyAudio==0.2.11",
        "google-api-python-client==1.6.5",
        "google-cloud-speech==0.31.0"
    ],
    entry_points={
        'console_scripts': [
            'voice = voice.__main__:main'
        ]
    },
)