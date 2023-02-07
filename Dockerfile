# base image  
FROM python:3.10   
# setup environment variable  
ENV DOCKERHOME=/home/app/webapp  

# set work directory  
RUN mkdir -p $DOCKERHOME 

RUN apt-get update && apt-get install cron -y

# where your code lives  
WORKDIR $DOCKERHOME  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# install dependencies  
RUN pip install --upgrade pip  

# copy whole project to your docker home directory. 
COPY . $DOCKERHOME  
# run this command to install all dependencies  
RUN pip install -r requirements.txt