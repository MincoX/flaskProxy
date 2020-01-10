FROM python:3.7

RUN mkdir -p /usr/src/Proxy_Server
WORKDIR /usr/src/Proxy_Server
COPY requirements.txt /usr/src/Proxy_Server
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /usr/src/Proxy_Server/requirements.txt
COPY . /usr/src/Proxy_Server
RUN python /usr/src/Proxy_Server/init.py

CMD ["gunicorn", "-c", "/usr/src/Proxy_Server/gunicorn.py", "manager:app"]
