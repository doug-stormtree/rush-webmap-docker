# web/Dockerfile
# Base stage
FROM node:lts-alpine AS base
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .

# Development stage
FROM base AS development
EXPOSE 3000
CMD ["npm", "run", "dev"]
