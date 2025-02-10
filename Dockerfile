FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install poetry && poetry install --no-dev

ENTRYPOINT ["poetry", "run", "python", "hephai_pr_doctor/main.py"]
