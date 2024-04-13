
.PHONY: create_virtual_env
create_virtual_env:
	python -m venv ./virtualenv/modelmaster
	source virtualenv/test/bin/activate
	pip install -r ./requirements.txt

#Package setup
requirements:
	#cd ./python/ && pipenv run pipenv_to_requirements
	# For an application, use:
	#cd ./python/ && pipenv run pipenv_to_requirements -f

wheels: requirements
	cd python && pipenv run python setup.py bdist_wheel

clean-dist:
	rm -rf ./python/dist

uninstall-inference-package:
	cd ./python/ && pipenv run pip uninstall -y ./dist/uu_inference-1.0-py3-none-any.whl 2> /dev/null

install-packages-in-env:
	cd ./python/ && pipenv install -d   && pipenv install

install-inference-package:
	cd ./python/ && pipenv run pip install ./dist/uu_inference-1.0-py3-none-any.whl

# may cause issues related to distnotfound error -- update accordingly
clean-build-files:
	cd python && pipenv run python setup.py clean

copy-env-variables:
	export aws_access_key_id=${aws_access_key_id}
	export aws_secret_access_key=${aws_secret_access_key}
	cp .env python/src/.env

setup-inference-dev-env: clean-dist wheels  uninstall-inference-package install-inference-package   clean-build-files   copy-env-variables

setup-docker-env:
	docker build -t uniteus/model-management .
	docker run -i -t uniteus/model-management /bin/bash

push-docker-to-aws:
	docker build -t uniteus/model-management .
	docker image tag uniteus/model-management:latest  543800268692.dkr.ecr.us-west-2.amazonaws.com/model-management
	docker login -u AWS -p $(aws ecr get-login-password --region us-west-2) 543800268692.dkr.ecr.us-west-2.amazonaws.com
	aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 543800268692.dkr.ecr.us-west-2.amazonaws.com
	#docker image push 543800268692.dkr.ecr.us-west-2.amazonaws.com/model-management