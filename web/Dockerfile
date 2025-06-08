FROM node:24-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json /app/

# TODO(bliutech): remove --force once dependencies are fixed
RUN npm ci 

COPY . /app

EXPOSE 3000

RUN npm run build

RUN npm start
