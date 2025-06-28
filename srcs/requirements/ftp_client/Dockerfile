FROM    ubuntu:latest
WORKDIR /app

RUN     apt-get update && apt-get upgrade -y
RUN     apt install net-tools systemctl ftp -y
COPY    ./files /app/

CMD     ["tail", "-f", "/dev/null"]