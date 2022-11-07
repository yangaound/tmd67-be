FROM python

RUN apt-get update && apt-get install -y netcat
WORKDIR /workspaces/tmd67-be
COPY . .
RUN pip --no-cache-dir install -r requirements_prod.txt
ENTRYPOINT [ "bash", "entrypoint.sh" ]
CMD uwsgi --ini uwsgi.ini
