IMAGE_NAME = minesweeper

build:
	docker build -t $(IMAGE_NAME) .

dev:
	docker run -it --rm -v ./:/app $(IMAGE_NAME) bash

run:
	docker run --rm $(IMAGE_NAME)

style:
	black --line-length=100 .

play:
	python main.py

.PHONY: build dev run style play
