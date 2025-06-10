FROM node:24-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json /app/

RUN npm ci 

COPY . /app

EXPOSE 8080

ARG SERVER_URL

ENV SERVER_URL=$SERVER_URL

RUN npm run build

ENV PORT=8080

CMD ["node", ".next/standalone/server.js"]
