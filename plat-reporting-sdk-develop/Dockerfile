FROM node:12.22.1
WORKDIR /app
COPY . .
RUN npm set registry http://npm-registry.channelprecision.com
RUN npm install
RUN rm .npmrc
RUN npm run build
EXPOSE 5000
CMD [ "node", "server.js" ]

