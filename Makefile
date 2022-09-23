hello:  # hello
	@echo hello! 
	@echo this is airflow demo fun project
	@echo run away!


start_in_compose:  # start airflow&co in docker-compose
	-mkdir -p ./_run/mnt/logs ./_run/mnt/postgres ./dags
	echo "AIRFLOW_UID=$$(id -u)" | tee .env
	docker-compose up


venv:  # create virtual environment (dev only)
	python3 -m venv _venv
	_venv/bin/pip install flake8 black
	_venv/bin/pip install apache-airflow[sqlite]==2.4.0