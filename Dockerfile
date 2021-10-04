# START STAGE 1
FROM openjdk:8-jdk-slim as builder
RUN apt-get update &&  apt-get -y install --no-install-recommends --no-upgrade wget
USER root

ENV ANT_VERSION 1.10.11
ENV ANT_HOME /etc/ant-${ANT_VERSION}

WORKDIR /tmp

RUN wget https://downloads.apache.org/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz \
    && mkdir ant-${ANT_VERSION} \
    && tar -zxvf apache-ant-${ANT_VERSION}-bin.tar.gz \
    && mv apache-ant-${ANT_VERSION} ${ANT_HOME} \
    && rm apache-ant-${ANT_VERSION}-bin.tar.gz \
    && rm -rf ant-${ANT_VERSION} \
    && rm -rf ${ANT_HOME}/manual \
    && unset ANT_VERSION

ENV PATH ${PATH}:${ANT_HOME}/bin

#WORKDIR /home/stefano/gitwork/exist-fdsn-station
WORKDIR /tmp
COPY . .
 
RUN ant
RUN wget https://exist-db.org/exist/apps/public-repo/public/shared-resources-0.9.1.xar
#RUN wget https://exist-db.org/exist/apps/public-repo/public/xquery-versioning-module-1.1.5.xar

# START STAGE 2
FROM existdb/existdb:release
#FROM existdb/existdb:5.2.0
#ADD http://exist-db.org/exist/apps/public-repo/public/functx-1.0.1.xar /exist/autodeploy

COPY --from=builder /tmp/build/*.xar /exist/autodeploy/
COPY --from=builder /tmp/*.xar /exist/autodeploy/

EXPOSE 8080 8443

CMD [ "java", "-jar", "start.jar", "jetty" ]
