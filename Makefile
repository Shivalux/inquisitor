NAME	= inquisitor
COMPOSE	= docker compose
YML		= ./srcs/docker-compose.yaml

$(NAME):
	$(COMPOSE) -f $(YML) -p "inquisitor" up -d --quiet-pull --build

up: $(NAME)

down:
	$(COMPOSE) -f $(YML) -p "inquisitor" down

console:
	$(COMPOSE) -f $(YML) -p "inquisitor" up  -quiet-pull --build

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

.PHONY: up down console list