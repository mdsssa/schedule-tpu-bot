FROM python:3.13.5
LABEL maintainer = "mdssa1337@gmail.com"
LABEL authors="medisa"

ENV TZ = Asia/Tomsk

RUN pip install --no-cache-dir -r requirements.txt



ENTRYPOINT ["top", "-b"]