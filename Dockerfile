FROM python:3.7
EXPOSE 5000
WORKDIR /code
COPY project /code/project
COPY requirements.txt /code/requirements.txt
RUN mkdir -p /code/images
RUN mkdir -p /code/text
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "0.0.0.0:5000", "project.app:app"]