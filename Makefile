.PHONY: init
init:
	cd frontend/ ; pnpm install

.PHONY: types
types:
	python -c "import py_ts_interfaces" || (echo "Install py-ts-interfaces to build types" && exit 1)
	py-ts-interfaces oloren/types.py -o frontend/src/backend.ts
	perl -i -pe 's/^interface/export interface/g' frontend/src/backend.ts
	python oloren/types.py frontend/src/backend.ts


.PHONY: dev
dev:
	rm -rf oloren/static ; ln -s ../frontend/dist oloren/static
	cd frontend/ ; pnpm run dev

.PHONY: build
build:
	cd frontend/ ; pnpm run build
	rm -rf oloren/static
	rsync -av --delete --delete-excluded --exclude=reports \
		frontend/dist/ oloren/static/
	cp frontend/config.json oloren/static/config.json

.PHONY: pypi
pypi:
	python setup.py sdist bdist_wheel
	twine upload dist/*