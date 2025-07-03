FROM ultralytics/ultralytics:latest-cpu

WORKDIR /code

COPY ./requirements-docker.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade  -r /code/requirements.txt

COPY ./app /code/

EXPOSE 80

CMD ["fastapi", "run", "app/main.py", "--port", "80"]