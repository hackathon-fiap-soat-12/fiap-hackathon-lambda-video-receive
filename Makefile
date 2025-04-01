.PHONY: clean deps package

# Clean up previous builds
clean:
	rm -rf build app/bin/bootstrap.zip

# Install dependencies
deps:
	mkdir -p build
	pip install --target build -r app/src/requirements.txt

# Package the Lambda function
package: clean deps
	cp -r app/src/*.py build/
	cd build && zip -r ../bin/bootstrap.zip .
