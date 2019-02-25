FROM centos:7.6.1810

RUN curl -L --silent -o aurora-tools-0.18.0-1.el7.centos.aurora.x86_64.rpm https://apache.bintray.com/aurora/centos-7/aurora-tools-0.18.0-1.el7.centos.aurora.x86_64.rpm
RUN curl -L --silent -o aurora-tools-0.18.0-1.el7.centos.aurora.x86_64.rpm.sha https://apache.bintray.com/aurora/centos-7/aurora-tools-0.18.0-1.el7.centos.aurora.x86_64.rpm.sha
RUN sha1sum -c aurora-tools-0.18.0-1.el7.centos.aurora.x86_64.rpm.sha
RUN yum install -y aurora-tools-0.18.0-1.el7.centos.aurora.x86_64.rpm epel-release
RUN yum makecache && yum install -y python-pip
RUN pip install ansible
# Ansible 2.5 far too often exists with 0 status
#RUN yum install -y centos-release-scl && yum makecache && yum install -y centos-release-ansible26
#RUN yum makecache && yum install -y ansible

ADD . /prm
ADD clusters.json /etc/aurora/clusters.json
