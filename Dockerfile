# start from base
FROM python:3

LABEL maintainer="Christian Muise <christian.muise@queensu.ca>"

# install system-wide deps for python
RUN apt-get -yqq update
RUN apt-get -yqq install python3-pip python3-dev curl gnupg build-essential vim git

# copy our application code
RUN mkdir /PROJECT
WORKDIR /PROJECT

# # install tkinter for gui
# ARG DEBIAN_FRONTEND=noninteractive
# ENV TZ=America/Toronto
# RUN apt-get install -y python3-tk

# install required elements
RUN pip3 install --upgrade pip
ADD requirements.txt /PROJECT/requirements.txt
RUN pip3 install -r requirements.txt

# install dsharp to run in the container
RUN curl https://mulab.ai/cisc-204/dsharp -o /usr/local/bin/dsharp
RUN chmod u+x /usr/local/bin/dsharp

# default command to execute when container starts
CMD /bin/bash
