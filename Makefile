build:
	docker build -t lambda-openscad .
# https://gallery.ecr.aws/lambda/python
# https://docs.docker.com/reference/dockerfile
interactive: build
	docker run -it --entrypoint=/bin/bash --rm lambda-openscad
clean:
	docker rm -f lambda-openscad || true
	docker rmi lambda-openscad || true
start: build
	docker run -p 9000:8080 lambda-openscad
background: clean build
	docker run --name lambda-openscad -d -p 9000:8080 lambda-openscad
test: background
	curl -s "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"model_source_base64": "Y3ViZShbMTAsMTAsMTBdKTsK"}' | jq '.body' -r | jq '.rendered_model_base64' -r | base64 -d | head
