FROM node:24-alpine

WORKDIR /app

# Kopiramo package.json i package-lock.json
COPY package*.json .
RUN npm install

# Kopiramo ostatak React koda
COPY . .

EXPOSE 3000

# Pokrećemo React
CMD ["npm", "run", "dev", "--", "--host"]