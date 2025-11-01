.PHONY: update

update:
	echo "Updating the dependencies..."
	poetry lock && poetry install