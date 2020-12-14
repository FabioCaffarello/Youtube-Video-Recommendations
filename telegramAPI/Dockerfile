FROM python:3.7-slim
COPY . /app
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++ 
RUN pip install -r requirements.txt
RUN python dbStarter.py

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
CMD gunicorn --bind 0.0.0.0:$PORT wsgi 
#CMD gunicorn --bind 0.0.0.0:80 wsgi 


#https://github.com/microsoft/LightGBM/blob/master/docker/dockerfile-python
#https://github.com/heroku/alpinehelloworld
#https://devcenter.heroku.com/articles/container-registry-and-runtime

# Creating ⬢ youtube-telegram... done
# https://youtube-telegram.herokuapp.com/ | https://git.heroku.com/youtube-telegram.git