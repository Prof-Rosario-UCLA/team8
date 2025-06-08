FROM node:24-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json /app/

RUN npm ci 

COPY . /app

EXPOSE 3000

RUN npm run build

CMD ["npm", "start"]