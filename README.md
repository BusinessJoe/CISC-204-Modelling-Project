# Cosmic Express Model

Cosmic Express is a 2D puzzle game where you must make a train route that delivers each alien from its starting point to a drop off point of the alien’s colour.

Given a train track, our group aims to see if it works as a valid solution to a puzzle.

Our model will determine if each alien in a puzzle has been moved from its starting point to a respective drop off point, with none left unaccounted for.

## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.

## Running the Model

1. We first have to build the course image. To do so use the command:
`docker build . -t cisc204`

2. Now that we have the image we can run the image as a container by using one of the following commands, depending on the terminal:

    In Windows Command Line:
    `docker run -t -i -v %cd%:/cosmicExpress cisc204 /bin/bash`

    In PowerShell:
    `docker run -t -i -v ${PWD}:/cosmicExpress cisc204 /bin/bash`

    On Linux:
    `docker run -t -i -v $(pwd):/cosmicExpress cisc204 /bin/bash`

3. You can run the model with test cases using `python run.py data/xml/filename.xml` where the file name is any file in the data/xml folder. This Docker representation returns all the propositions for each tile, but not a visual display.

## Running the GUI

To use the GUI, install the requirements from `requirements.txt` in a virtual environment, and then run the `run_gui.py` file. The GUI does not run in Docker, so this must be done locally (i.e. in the VSCode terminal).

Note that there are up to ten colors for aliens and houses (indexed from 0-9). To create a board size that is smaller than the current board, the GUI must be restarted.

To create a level, it is crucial to add obstacles on the borders of each board (see Figures 5 and 6 in the project document for examples). Omitting the borders may cause unexpected behavior.
