FROM centos:centos6
MAINTAINER Alex Leonhardt

RUN yum -y install epel-release
RUN yum -y install python-pip python-devel make gcc supervisor
RUN yum -y update

RUN mkdir -p /opt/sensu-grid

ADD . /opt/sensu-grid

RUN pip install -r /opt/sensu-grid/requirements.txt
RUN useradd -r sensu-grid
RUN chown -R sensu-grid:sensu-grid /opt/sensu-grid
RUN chmod 640 /opt/sensu-grid/config.yaml && chmod 755 /opt/sensu-grid/docker-start.sh

ADD start-scripts/supervisord-docker.conf /etc/supervisord.conf

WORKDIR /opt/sensu-grid

EXPOSE 5000

ENTRYPOINT ["/opt/sensu-grid/docker-start.sh"]
