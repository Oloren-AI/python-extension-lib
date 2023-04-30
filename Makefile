.PHONY: init
init: react-init

.PHONY: frontend
frontend: react-build

.PHONY: react-init
react-init:
	cd frontend/ ; pnpm install

.PHONY: react-build
react-build:
	cd frontend/ ; pnpm run build
	rsync -av --delete --delete-excluded --exclude=reports \
		frontend/dist/ oloren/static/
