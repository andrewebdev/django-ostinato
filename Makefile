help:
	@echo "\nPlease specify an action to run"
	@echo "==============================="
	@echo "start-interactive: Run the demo docker container interactively"
	@echo "run-tests: Run the django-ostinato unit tests"
	@echo "\n"
	@echo "Usefull commands for this project (NOT used with make):"
	@echo "----------------------------------------"
	@echo "docker-compose down: Stop and remove all containers"
	@echo "docker-compose up: Run the entire project in a simulated live environment"
	@echo "\n"

start-interactive:
	docker-compose run --rm --service-ports demo /bin/bash

run-tests:
	docker-compose run --rm demo /src/runtests.py
