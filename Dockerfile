FROM python:3.7

RUN mkdir -p /usr/src/Proxy_Flask
WORKDIR /usr/src/Proxy_Flask
COPY requirements.txt /usr/src/Proxy_Flask
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /usr/src/Proxy_Flask/requirements.txt
COPY . /usr/src/Proxy_Flask

CMD ["gunicorn", "-c", "/usr/src/Proxy_Flask/gunicorn.py", "manager:app"]
