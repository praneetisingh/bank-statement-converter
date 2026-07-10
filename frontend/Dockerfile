# Stage 1: Build the React application
FROM node:20-slim AS build

WORKDIR /app

# Install package dependencies using local cache and legacy peer dependencies
COPY package.json .
RUN npm install --legacy-peer-deps

# Copy source and build static files
COPY . .
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:stable-alpine

# Copy built frontend assets from builder stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration for SPA routing and API reverse-proxying
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
