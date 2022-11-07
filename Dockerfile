FROM python

COPY . .
RUN pip --no-cache-dir install -r requirements.txt
CMD uwsgi --ini uwsgi.ini
