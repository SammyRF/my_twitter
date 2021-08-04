FROM ubuntu:18.04

WORKDIR "/vagrant"
RUN apt-get update
RUN apt-get install -y vim python3 python3-pip python-setuptools
RUN apt-get install -y wget lsb-release mysql-server libmysqlclient-dev
RUN pip3 install django djangorestframework markdown django-filter mysqlclient django-debug-toolbar
