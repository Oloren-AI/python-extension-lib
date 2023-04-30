FROM python:3.8-slim-buster

# Update package repository
RUN apt-get update

# Install Node.js
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_19.x | bash -
RUN apt-get install -y nodejs

RUN pip install Flask==2.2.3
RUN pip install Flask-Cors==3.0.10

WORKDIR /usr/app

RUN npm i -g pnpm

COPY package.json ./
COPY pnpm-workspace.yaml ./
COPY core/frontend/package.json ./core/frontend/package.json

RUN pnpm i

COPY . .

EXPOSE 80

ENV NODE_ENV=production

RUN pip install requests

RUN pnpm turbo build

CMD ["pnpm", "turbo", "dev"]