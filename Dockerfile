FROM python:latest

COPY . /app
RUN sudo pip install -r /app/requirements.txt
CMD ["python3", "/app/main_bot.py"]
