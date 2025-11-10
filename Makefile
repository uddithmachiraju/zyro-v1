.PHONY: update build-test-package build-docker-image remove-docker-image

update:
	echo "Updating the dependencies..."
	poetry lock && poetry install

build-test-package: update
	echo "Building the zyro package.."
	rm -rf dist/
	poetry build
	# python -m build --wheel 

build-docker-image: build-test-package
	echo "Building Docker Image for testing..."
	docker build -t zyro-test-cli . 

remove-docker-image:
	echo "Removing test Docker Image..."
	docker rmi zyro-test-cli 

clean-test-resources: remove-docker-image
	echo "Clean the testing resources..."
	rm -rf dist/ 

test-package: build-docker-image
	echo "Entering the testing environment..."
	docker run -it --rm -p 8000:8000 zyro-test-cli 