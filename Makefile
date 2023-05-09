.PHONY: init
init:
	cd frontend/ ; pnpm installG

.PHONY: types
types:
	python -c "import py_ts_interfaces" || (echo "Install py-ts-interfaces to build types" && exit 1)
	py-ts-interfaces lib/oloren/types.py -o frontend/src/backend.ts
	perl -i -pe 's/^interface/export interface/g' frontend/src/backend.ts
	python lib/oloren/types.py frontend/src/backend.ts


.PHONY: dev
dev:
	pip install -e lib
	rm -rf lib/oloren/static
	cd lib/oloren ; ln -s ../../frontend/dist static
	cd frontend/ ; pnpm run dev

.PHONY: build
build:
	cd frontend/ ; pnpm run build
	rm -rf lib/oloren/static
	rsync -av --delete --delete-excluded --exclude=reports \
		frontend/dist/ lib/oloren/static/

.PHONY: pypi
pypi:
	make clean
	make build
	cd lib/ ; python setup.py sdist bdist_wheel
	cd lib/ ; twine upload dist/*

.PHONY: docs
docs:
	cd docs/ ; make html

clean:
	rm -rf lib/dist lib/build lib/*.egg-info lib/oloren/static
