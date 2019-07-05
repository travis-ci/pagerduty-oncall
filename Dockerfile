FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY . .
RUN python setup.py develop


CMD [ "python", "./pagerduty-oncall.py" ]
