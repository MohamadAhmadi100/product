FROM python:3.9

WORKDIR /product

COPY ./README.md /product/README.md

COPY ./requirements.txt /product/requirements.txt

COPY ./.env /product/.env

COPY ./setup.py /product/setup.py

COPY ./app /product/app

RUN pip install --upgrade pip

RUN pip install -e /product/.

CMD cd /product && python /app/main.py
