from setuptools import setup

# read the contents of README.md
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="matrix-registration-bot",
    version="0.0.1",
    description="A bot to manage user registrations of a matrix server.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Julian-Samuel Gebühr",
    author_email="julian-samuel@gebuehr.net",
    url="https://github.com/moan0s/matrix-registration-bot",
    download_url="https://github.com/moan0s/matrix-registration-bot.git",
    license="AGPL-3",
    packages=['matrix_registration_bot'],
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
