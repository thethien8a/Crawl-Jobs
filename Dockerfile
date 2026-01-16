# Cập nhật phiên bản Airflow phù hợp với bộ phụ thuộc dbt
ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

# Chuyển sang user root để cài đặt system packages
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    pkg-config \
    chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt dbt ở nơi khác
RUN python3 -m venv /opt/dbt_venv && \
    /opt/dbt_venv/bin/pip install --no-cache-dir dbt-postgres==1.9.1 elementary-data==0.20.1 && \
    ln -s /opt/dbt_venv/bin/dbt /usr/local/bin/dbt && \
    # ln -s /opt/dbt_venv/bin/edr /usr/local/bin/edr && \
    chown -R airflow:root /opt/dbt_venv

# Quay lại user airflow
USER airflow

# Copy requirements file
COPY requirements.txt /requirements.txt

# Cập nhật các arguments
ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11
ARG AIRFLOW_CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Cài đặt Python dependencies với constraints để đảm bảo tính tương thích
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt --constraint "${AIRFLOW_CONSTRAINT_URL}" && \
    pip install --no-cache-dir apache-airflow-providers-standard apache-airflow-providers-fab --constraint "${AIRFLOW_CONSTRAINT_URL}"
# Cleanup để giảm kích thước image
RUN pip cache purge