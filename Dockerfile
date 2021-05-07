FROM python:3.7

WORKDIR /usr/src/flaskProxy

COPY . /usr/src/flaskProxy
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /usr/src/flaskProxy/requirements.txt  && chmod +x launch_service.sh

CMD ["/bin/bash", "-c", "/usr/src/flaskProxy/launch_service.sh"]
