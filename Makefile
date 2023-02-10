.DEFAULT_GOAL := help

IMAGE_NAME = tokhna
PROYECT_NAME = youtube_watcher
CONTAINER_NAME = youtube_watcher
CONTAINER_OWNER = tokhna


######## Manage containers status (default target = all)
status: ## Show containers status, use me with: make status target=api
	docker-compose ps ${target}

stop: ## Stops the docker containers, use me with: make stop target=api
	docker-compose stop ${target}

down: ## Stops and removes the docker containers, use me with: make down target=api
	docker-compose down ${target}

delete: ## Delete the docker containers, use me with: make delete target=api
	docker-compose rm -fv ${target}

d.build: ## Build the docker containers, use me with: make build target=api
	docker-compose build ${target}

up: ## Up the docker containers, use me with: make up target=api
	docker-compose up -d ${target}

logs: ## Logss the docker containers, use me with: make logs target=api
	docker-compose logs -f ${target}

restart: ## Restart the docker containers, use me with: make restart target=api
	docker-compose restart ${target}

rebuild: # Rebuild the docker containers, use me with: make rebuild
	make stop
	make delete
	make d.build
	make up

ssh: ## SSH connect to container, se me with: make ssh target=api
		docker-compose -p $(PROYECT_NAME) run --rm ${target} sh -c "bash"

######## Manage containers execution
exec: ## Execute command in the docker container, use me with: make exec target=api cmd=ls
	docker exec ${target} ${cmd}

push: ## Push the docker containers, use me with: make push revision=1.0
	docker push ${revision}

######## Tag images
tag.all: ## Tag the docker containers, use me with: make tag.all version=1.0
	docker tag ${CONTAINER_NAME} ${CONTAINER_OWNER}/${CONTAINER_NAME}:${version}

######## Push images
push.all: ## Push all the docker containers, use me with: make push.all version=1.0
	docker push ${CONTAINER_OWNER}/${CONTAINER_NAME}:${version}

######## Pull images
pull.all: # Pull all the docker containers, use me with: make pull.all version=1.0
	docker pull ${CONTAINER_OWNER}/${CONTAINER_NAME}:${version}

###### Help
help:
	@echo  'Development commands for project ${PROYECT_NAME}'
	@echo
	@echo 'Usage: make COMMAND [target=some-targets] [cms=some-commads] [revision=some-revision]'
	@echo
	@echo 'Targets:'
	@echo
	@echo '  api            API Rest'
	@echo '  worker         Worker for asynchronous tasks'
	@echo '  postgres_db    PostgreSQL database'
	@echo '  mongo_db       MongoDB database'
	@echo '  rq-dashboard   Dashboard for Pyhton-RQ'
	@echo
	@echo '  default target=all'
	@echo
	@echo 'Commands:'
	@echo
	@grep -E '^[a-zA-Z_-]+.+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo
