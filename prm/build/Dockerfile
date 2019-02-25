FROM centos:7.6.1810

RUN curl -L --silent -o aurora-tools-0.20.0-1.el7.centos.aurora.x86_64.rpm https://apache.bintray.com/aurora/centos-7/aurora-tools-0.20.0-1.el7.centos.aurora.x86_64.rpm
RUN curl -L --silent -o aurora-tools-0.20.0-1.el7.centos.aurora.x86_64.rpm.sha512 https://apache.bintray.com/aurora/centos-7/aurora-tools-0.20.0-1.el7.centos.aurora.x86_64.rpm.sha512
RUN sha512sum -c aurora-tools-0.20.0-1.el7.centos.aurora.x86_64.rpm.sha512
RUN yum install -y aurora-tools-0.20.0-1.el7.centos.aurora.x86_64.rpm

ADD . /prm
RUN mkdir /etc/aurora
ADD clusters.json /etc/aurora/clusters.json