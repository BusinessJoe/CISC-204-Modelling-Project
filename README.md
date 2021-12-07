# Cosmic Express Model

Cosmic Express is a 2D puzzle game where you must make a train route that delivers each alien from its starting point to a drop off point of the alien’s colour.

Given a train track, our group aims to see if it works as a valid solution to a puzzle.

Our model will determine if each alien in a puzzle has been moved from its starting point to a respective drop off point, with none left unaccounted for.

## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.

## Docker

Docker file for developing the course project.

1. We first have to build the course image. To do so use the command:
`docker build . -t cisc204`

2. Now that we have the image we can run the image as a container by using the command: `docker run -t -i -v /modelProject:/PROJECT cisc204 /bin/bash`

    /modelProject can be replaced with the path of whatever folder you want to link to the container

    /PROJECT is the folder in the container that will be tied to your local directory

3. From there the two folders should be connected, everything you do in one automatically updates in the other. For the project you will write the code in your local directory and then run it through the docker command line. A quick test to see if they're working is to create a file in the folder on your computer then use the terminal to see if it also shows up in the docker container.
