FROM python:3.7

RUN mkdir -p /usr/src/flaskProxy
WORKDIR /usr/src/flaskProxy
COPY requirements.txt /usr/src/flaskProxy
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /usr/src/flaskProxy/requirements.txt
COPY . /usr/src/flaskProxy

# CMD ["gunicorn", "-c", "/usr/src/flaskProxy/gunicorn.py", "manager:app"]

