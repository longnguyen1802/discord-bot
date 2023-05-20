FROM alexellisuk/classic-watchdog:0.13.1 as watchdog
FROM heroku/heroku:16
FROM ubuntu:latest

LABEL maintainer="Hugging Face"
LABEL repository="transformers"
# Install dependencies
RUN apt-get update && \
    apt-get install -y python3 \
                   python3-pip && \
    rm -rf /var/lib/apt/lists

RUN pip install transformers
RUN python3 -m pip install torch

RUN mkdir -p /home/app

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

WORKDIR /home/app
COPY classify.py /home/app
COPY mymodel /home/app/mymodel

ENV GLOG_minloglevel="3"
ENV fprocess="xargs python3 classify.py"
ENV write_debug="false"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
