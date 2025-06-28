FROM    ubuntu:latest

ARG     USERNAME
ARG     PASSWORD

RUN     apt-get update && apt-get upgrade -y
RUN     apt install systemctl net-tools vsftpd vim -y tzdata

RUN     useradd -m $USERNAME
RUN     echo $USERNAME:$PASSWORD | chpasswd

COPY    ./ftp_directory /home/$USERNAME
COPY    ./confs/vsftpd.conf /etc/vsftpd.conf
RUN     mkdir -p /var/run/vsftpd/empty && chmod 755 /var/run/vsftpd/empty
RUN     chmod 777 /home/$USERNAME

WORKDIR /home/ftpuser

CMD     ["vsftpd"]