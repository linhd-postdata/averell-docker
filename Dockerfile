FROM python:3.11

WORKDIR /usr/src/app 

COPY . . 
RUN pip install -e .
RUN pip install --no-cache-dir -r requirements.txt 

EXPOSE 5741

CMD [ "gradio", "./app.py" ]