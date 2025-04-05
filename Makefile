.PHONY: clean docker-build package

# Clean up previous builds
clean:
	rm -rf bin/bootstrap.zip
	mkdir -p bin

# Build Docker image and extract zip file
docker-build:
	docker build -t lambda-package-builder -f Dockerfile .

# Package the Lambda function using Docker
package: clean docker-build
	docker run --rm lambda-package-builder > bin/bootstrap.zip