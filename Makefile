NAME	= inquisitor
COMPOSE	= docker compose
YML		= ./srcs/docker-compose.yaml
ARG		= $(wordlist 2, $(words $(MAKECMDGOALS)), $(MAKECMDGOALS))
CLIENT	= ftp_client
SERVER	= ftp_server

%:
	@:

up:
	$(COMPOSE) -f $(YML) -p "inquisitor" up -d --quiet-pull --build

all: up

down:
	$(COMPOSE) -f $(YML) -p "inquisitor" down

clean: down

fclean: clean
	docker image rm $(NAME):$(NAME) $(CLIENT):$(NAME) $(SERVER):$(NAME)

re: fclean all

console:
	$(COMPOSE) -f $(YML) -p "inquisitor" up  -quiet-pull --build

information:
	@echo "[ $(SERVER) ]"
	@docker inspect $(SERVER) | grep '"MacAddress": "[^"]' | sed 's/^[ \t]*//' || true
	@docker inspect $(SERVER) | grep '"IPAddress": "[^"]' | sed 's/^[ \t]*//' || true
	@echo "[ $(CLIENT) ]"
	@docker inspect $(CLIENT) | grep '"MacAddress": "[^"]' | sed 's/^[ \t]*//' || true
	@docker inspect $(CLIENT) | grep '"IPAddress": "[^"]' | sed 's/^[ \t]*//' || true

inspect:
	@echo "[ $(ARG) ]"
	@docker inspect $(ARG) | grep '"MacAddress": "[^"]' | sed 's/^[ \t]*//' || true
	@docker inspect $(ARG) | grep '"IPAddress": "[^"]' | sed 's/^[ \t]*//' || true

list:
	@echo "-------------:: list :: all containers ::-------------"
	@docker ps -a
	@echo
	@echo "-------------:: list :: all images ::-------------"
	@docker images
	@echo
	@echo "-------------:: list :: all networks ::-------------"
	@docker network list
	@echo
	@echo "-------------:: list :: all volumes ::-------------"
	@docker volume list

.PHONY: up down console list inspect information all clean fclean re