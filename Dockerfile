FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /acmapp

WORKDIR /acmapp

ADD . /acmapp/
#COPY requirements.txt /acmapp/
RUN pip install -r requirements.txt
#COPY . /code/
CMD ["python", "manage.py", "runserver", "0.0.0.0", "8000"]

#ENTRYPOINT ["python", "manage.py"]
#CMD ["runserver", "0.0.0.0:8000"]