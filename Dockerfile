FROM python:3.9-slim

WORKDIR /api

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./api .

RUN apt-get clean

RUN pip cache purge

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
