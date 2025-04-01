FROM apache/airflow:2.6.0-python3.9

WORKDIR /opt/airflow

COPY requirements.txt requirements.txt

USER airflow

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install selenium==4.30.0  # Explicitly install selenium

USER root

RUN mkdir -p /opt/airflow/dags/src/screenshots && \
    chmod -R 777 /opt/airflow/dags/src/screenshots &&\
    mkdir -p /opt/airflow/dags/src/output && \
    chmod -R 777 /opt/airflow/dags/src/output
USER airflow
