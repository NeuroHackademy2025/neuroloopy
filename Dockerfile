# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY src/neuroloopy/dashboard/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy dashboard source files
COPY src/neuroloopy/dashboard/ .

# Expose the port the dashboard runs on
EXPOSE 5001

# Health check to ensure the server is running
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5001/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the dashboard server
CMD ["npm", "start"] 