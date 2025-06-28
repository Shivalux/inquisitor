FROM    python:3.14.0b3-bookworm

RUN     apt-get update && apt-get upgrade -y
RUN     apt install net-tools libpcap-dev python3-pcapy iputils-ping systemctl sudo -y

COPY    ./srcs/requirements.txt /app/requirements.txt
RUN     pip install -r /app/requirements.txt
WORKDIR /app/inquisitor
RUN     ls > /var/directory.txt

CMD     ["tail", "-f", "/dev/null"]