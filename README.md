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

2. Now that we have the image we can run the image as a container by using one of the following commands, depending on the terminal:

    In Windows Command Line:

    `docker run -t -i -v %cd%:/cosmicExpress cisc204 /bin/bash`

    In PowerShell:

    `docker run -t -i -v ${PWD}:/cosmicExpress cisc204 /bin/bash`

    On Linux:

    `docker run -t -i -v $(pwd):/cosmicExpress cisc204 /bin/bash`

3. You can run the model with test cases using `python run.py data/xml/complex.xml` where the file name is any file in the data/xml folder.
