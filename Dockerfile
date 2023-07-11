FROM ubuntu:22.04
USER root
WORKDIR /root

# install java
RUN apt-get update
RUN apt-get install -y default-jre curl
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV JAVA=${JAVA_HOME}/bin/java
ENV PATH=${JAVA_HOME}/bin/:${PATH}

# install coursier, scala and sbt
RUN curl -fL https://github.com/coursier/coursier/releases/latest/download/cs-x86_64-pc-linux.gz | gzip -d > cs && chmod +x cs && echo Y | ./cs setup

# Copy sbt project
ADD scala /root/scala
WORKDIR /root/scala

# Run test
CMD . /root/.profile; sbt test
