.PHONY: init
init:
	cd frontend/ ; pnpm install

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