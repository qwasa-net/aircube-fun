AIRFLOW_VERSION=2.4.0
PYTHON_VERSION=$(shell python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)
PWD=$(shell pwd)


hello:  # hello
	@echo "hello!  "
	@echo "this is airflow demo fun project  "
	@echo "run away!"


start_in_compose:  # start airflow&co in docker-compose
	-mkdir -pv ./_run/compose/logs ./_run/compose/postgres ./dags
	echo "AIRFLOW_UID=$$(id -u)" | tee .env
	docker-compose up


start_standalone:  venv  # start airflow&co locally (standalone)

	# make dirs and copy config
	-mkdir -pv ./_run/local/logs ./_run/local/postgres ./dags
	-cp -v ./standalone_airflow.cfg ./_run/local/airflow.cfg
	-ln -sf $(PWD)/dags ./_run/local/

	# init db
	PATH=$PATH:$(PWD)/_venv/bin/ \
	AIRFLOW_HOME=$(PWD)/_run/local/ \
	"$(PWD)/_venv/bin/airflow" db init

	# run full lot
	PATH=$PATH:$(PWD)/_venv/bin/ \
	AIRFLOW_HOME=$(PWD)/_run/local/ \
	airflow standalone


venv:  # create virtual environment (dev only)
	[ -f "$(PWD)/_venv/bin/python" ] || python3 -m venv "$(PWD)/_venv"
	"$(PWD)/_venv/bin/python" --version
	# install dev tools
	"$(PWD)/_venv/bin/pip" install flake8 black
	# install airflow and friends
	"$(PWD)/_venv/bin/pip" install \
	apache-airflow==${AIRFLOW_VERSION} \
	apache-airflow-providers-amazon \
	--constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"