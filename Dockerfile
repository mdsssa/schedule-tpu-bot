FROM python:3.13.5
LABEL maintainer = "mdssa1337@gmail.com"
LABEL authors="medisa"

ENV TZ = Asia/Tomsk

RUN pip install --no-cache-dir -r requirements.txt
RUN sudo apt-get install curl
RUN curl https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.122/linux64/chromedriver-linux64.zip --output chromedriver-linux64.zip
RUN sudo mv chromedriver-linux64.zip /usr/local/bin



ENTRYPOINT ["top", "-b"]