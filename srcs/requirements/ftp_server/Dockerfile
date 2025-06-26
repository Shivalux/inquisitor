FROM    ubuntu:latest

ARG     USER_PASSWORD

RUN     apt-get update && apt-get upgrade -y
RUN     apt install systemctl vsftpd vim -y tzdata

RUN     useradd -m ftpuser
RUN     echo ftpuser:$USER_PASSWORD | chpasswd

COPY    ./ftpuser /home/ftpuser
COPY    ./confs/vsftpd.conf /etc/vsftpd.conf
RUN     mkdir -p /var/run/vsftpd/empty && chmod 755 /var/run/vsftpd/empty
RUN     chmod 777 /home/ftpuser
WORKDIR /home/ftpuser

CMD     ["vsftpd"]