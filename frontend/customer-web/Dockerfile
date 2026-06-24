FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

# Build application
RUN npm run build

# Expose port (documented port based on package.json)
EXPOSE 4000

# Start the application
CMD ["npm", "start"]
