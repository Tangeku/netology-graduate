FROM apache/airflow:latest-python3.12

# Права администратора
USER root

# Обновление и установка пакетных менеджеров
RUN apt-get update && \
    apt-get install -y apt-utils && \
    apt-get install -y wget

# Установка JDK
RUN wget https://download.oracle.com/java/22/latest/jdk-22_linux-x64_bin.tar.gz && \
    mkdir -p /opt/java/jdk-22 && \
    tar -xvf jdk-22_linux-x64_bin.tar.gz -C /opt/java && \
    rm jdk-22_linux-x64_bin.tar.gz

# Установка JAVA
RUN wget -O jre-8u411-linux-x64.tar.gz https://javadl.oracle.com/webapps/download/AutoDL?BundleId=249840_43d62d619be4e416215729597d70b8ac && \
    mkdir -p /opt/java/jre-1.8 && \
    tar -xvf jre-8u411-linux-x64.tar.gz -C /opt/java && \
    rm jre-8u411-linux-x64.tar.gz


# Возвращение к пользователю по умолчанию
USER airflow

# Установка переменных окружения
ENV JAVA_HOME=/opt/java/jdk-22.0.1
ENV PATH=$PATH:$JAVA_HOME/bin

# Установка остальных пакетов через pip
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt