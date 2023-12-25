AIRFLOW_VERSION ?= 2.8.0
PYTHON_SYSTEM ?= python3
PYTHON_VERSION ?= $(shell "$(PYTHON_SYSTEM)" --version | cut -d " " -f 2 | cut -d "." -f 1-2)
PWD=$(shell pwd)


hello:  # hello
	@echo "hello!  "
	@echo "this is airflow demo fun project  "
	@echo "run away!"


start_in_compose:  # start airflow&co in docker-compose
	-mkdir -pv ./_run/compose/logs ./_run/compose/postgres ./dags
	echo "AIRFLOW_UID=$$(id -u)" | tee .env
	docker-compose up


CMD ?= airflow standalone
start_standalone: # start airflow&co locally (standalone)

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
	$(CMD)

venv:  # create virtual environment (dev only)
	[ -f "$(PWD)/_venv/bin/python" ] || "$(PYTHON_SYSTEM)" -m venv "$(PWD)/_venv"
	wget -c "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" -O "$(PWD)/_venv/airflow-constraints-${AIRFLOW_VERSION}-${PYTHON_VERSION}.txt"
	"$(PWD)/_venv/bin/python" --version
	# install dev tools
	"$(PWD)/_venv/bin/pip" install --disable-pip-version-check flake8 black
	# install airflow and friends
	"$(PWD)/_venv/bin/pip" install --disable-pip-version-check \
	apache-airflow==${AIRFLOW_VERSION} \
	apache-airflow-providers-amazon \
	--constraint "$(PWD)/_venv/airflow-constraints-${AIRFLOW_VERSION}-${PYTHON_VERSION}.txt"

