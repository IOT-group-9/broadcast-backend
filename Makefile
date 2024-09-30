.PHONY: 
makemigrations:
	(cd app && piccolo migrations new app_db --auto)

migrate:
	(cd app && piccolo migrations forwards all)

createuser:
	(cd app && piccolo user create)

createsuperuser:
	(cd app && piccolo user create --username=aadmin --password=aadmin --email=admin@gmail.com --is_admin=true --is_superuser=true --is_active=true)

dev_start:
	python -m app

env_setup:
	pip install poetry
	poetry install
	echo "installed environment! Use poetry shell to enter environment. Create a new .env"