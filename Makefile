build:
	docker build -t lambda-openscad .
# https://gallery.ecr.aws/lambda/python
# https://docs.docker.com/reference/dockerfile
interactive: build
	docker run -it --entrypoint=/bin/bash --rm lambda-openscad
