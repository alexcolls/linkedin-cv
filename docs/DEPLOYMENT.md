# Deployment Guide

This guide covers deploying the LinkedIn CV Generator in production environments using Docker, docker-compose, or bare metal installation.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment (Recommended)](#docker-deployment-recommended)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Bare Metal Installation](#bare-metal-installation)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum**:
- CPU: 1 core
- RAM: 512 MB
- Disk: 2 GB free space

**Recommended**:
- CPU: 2 cores
- RAM: 2 GB
- Disk: 5 GB free space

### Software Requirements

- Docker 20.10+ (for Docker deployment)
- Docker Compose 2.0+ (for Compose deployment)
- Python 3.9+ (for bare metal)
- Poetry 1.7+ (for bare metal)

---

## Docker Deployment (Recommended)

### 1. Build the Image

```bash
# Clone the repository
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv

# Build Docker image
docker build -t linkedin-cv:latest .
```

### 2. Prepare Environment

```bash
# Copy production environment template
cp .env.production.sample .env

# Generate encryption key
docker run --rm linkedin-cv:latest --generate-key

# Edit .env and add the generated key
nano .env
```

### 3. Create Required Directories

```bash
# Create directories for volumes
mkdir -p output sessions

# Set proper permissions
chmod 755 output sessions
```

### 4. Run Container

```bash
docker run -d \
  --name linkedin-cv-generator \
  --restart unless-stopped \
  -v $(pwd)/output:/data/output \
  -v $(pwd)/sessions:/app/sessions \
  -v $(pwd)/.env:/app/.env:ro \
  --env-file .env \
  linkedin-cv:latest
```

### 5. Usage

```bash
# Generate a CV
docker exec linkedin-cv-generator \
  python3 -m src.cli \
  --theme modern \
  https://linkedin.com/in/username

# Check container health
docker ps
docker logs linkedin-cv-generator

# Access generated CVs
ls -lh output/
```

---

## Docker Compose Deployment

### 1. Setup

```bash
# Clone repository
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv

# Copy and configure environment
cp .env.production.sample .env
nano .env  # Edit configuration
```

### 2. Start Services

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f linkedin-cv

# Check status
docker-compose ps
```

### 3. Using the Service

```bash
# Generate CV
docker-compose exec linkedin-cv \
  python3 -m src.cli \
  --theme modern \
  https://linkedin.com/in/username

# Interactive mode
docker-compose run --rm linkedin-cv \
  /bin/bash -c "./run.sh"
```

### 4. Management

```bash
# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Update and rebuild
git pull
docker-compose build
docker-compose up -d

# View resource usage
docker-compose stats

# Clean up
docker-compose down
docker-compose down -v  # Also remove volumes
```

---

## Bare Metal Installation

### 1. System Dependencies

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y \
  python3.9 \
  python3-pip \
  libcairo2 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info
```

**macOS**:
```bash
brew install python@3.9 cairo pango gdk-pixbuf libffi
```

### 2. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### 3. Clone and Install

```bash
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv

# Install dependencies
poetry install --only main

# Install Playwright browsers
poetry run playwright install chromium
```

### 4. Configuration

```bash
# Copy environment template
cp .env.sample .env

# Generate encryption key
poetry run python -m src.cli --generate-key

# Edit configuration
nano .env
```

### 5. Run Application

```bash
# Via Poetry
poetry run python -m src.cli \
  --theme modern \
  https://linkedin.com/in/username

# Via run.sh menu
./run.sh
```

### 6. System Service (Optional)

Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/linkedin-cv.service
```

```ini
[Unit]
Description=LinkedIn CV Generator
After=network.target

[Service]
Type=simple
User=linkedin
WorkingDirectory=/opt/linkedin-cv
Environment="PATH=/home/linkedin/.local/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/linkedin/.local/bin/poetry run python -m src.cli --help

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable linkedin-cv
sudo systemctl start linkedin-cv
sudo systemctl status linkedin-cv
```

---

## Configuration

### Environment Variables

Key configuration options (see `.env.production.sample` for complete list):

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENCRYPTION_KEY` | Session encryption key | - | ✅ |
| `OUTPUT_DIR` | CV output directory | `./output` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `DEFAULT_THEME` | Default CV theme | `modern` | ❌ |
| `ENABLE_QR_CODE` | Enable QR codes by default | `true` | ❌ |
| `HEADLESS` | Run browser headless | `true` | ❌ |
| `SESSION_DIR` | Session storage directory | `./sessions` | ❌ |

### Production Settings

Recommended production configuration:

```bash
# .env
ENCRYPTION_KEY=<generated-key>
LOG_LEVEL=INFO
DEBUG=false
HEADLESS=true
ENABLE_QR_CODE=true
DEFAULT_THEME=modern
SESSION_EXPIRY_DAYS=30
MAX_BROWSER_INSTANCES=3
ALLOW_INSECURE=false
```

---

## Security Considerations

### 1. Encryption Key Management

```bash
# Generate secure key
docker run --rm linkedin-cv:latest --generate-key

# Store securely (use secrets management in production)
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

### 2. File Permissions

```bash
# Set restrictive permissions
chmod 600 .env
chmod 700 sessions
chmod 755 output
```

### 3. Network Security

```bash
# Firewall rules (example for UFW)
sudo ufw allow from <your-ip> to any port 22  # SSH only from trusted IPs
sudo ufw enable
```

### 4. Container Security

```bash
# Run as non-root user (already configured in Dockerfile)
USER linkedin

# Enable security options in docker-compose.yml
security_opt:
  - no-new-privileges:true
```

### 5. Regular Updates

```bash
# Update dependencies
poetry update

# Rebuild Docker image
docker build -t linkedin-cv:latest .

# Check for security vulnerabilities
poetry audit  # Planned feature
```

---

## Monitoring & Logging

### Docker Logs

```bash
# View logs
docker logs linkedin-cv-generator

# Follow logs
docker logs -f linkedin-cv-generator

# Last 100 lines
docker logs --tail 100 linkedin-cv-generator

# With timestamps
docker logs -t linkedin-cv-generator
```

### Log Levels

Configure via `LOG_LEVEL` environment variable:

- `DEBUG`: Verbose output for development
- `INFO`: Normal operational messages (recommended)
- `WARNING`: Warning messages
- `ERROR`: Error messages only
- `CRITICAL`: Critical issues only

### Health Checks

```bash
# Docker health status
docker ps
docker inspect linkedin-cv-generator | grep Health

# Manual health check
docker exec linkedin-cv-generator \
  python3 -c "from src.config import Config; from src.pdf.generator import PDFGenerator; print('OK')"
```

### Resource Monitoring

```bash
# Container stats
docker stats linkedin-cv-generator

# Disk usage
du -sh output/ sessions/

# Docker system info
docker system df
```

---

## Troubleshooting

### Container Won't Start

**Issue**: Container exits immediately

**Solutions**:
```bash
# Check logs
docker logs linkedin-cv-generator

# Verify environment variables
docker exec linkedin-cv-generator env

# Test manually
docker run --rm -it linkedin-cv:latest /bin/bash
```

### Permission Denied Errors

**Issue**: Cannot write to output directory

**Solutions**:
```bash
# Fix ownership
sudo chown -R 1000:1000 output/ sessions/

# Fix permissions
chmod 755 output/ sessions/
```

### Browser/Playwright Errors

**Issue**: Chromium fails to start

**Solutions**:
```bash
# Reinstall Playwright browsers
docker exec linkedin-cv-generator \
  poetry run playwright install chromium --with-deps

# Check Playwright installation
docker exec linkedin-cv-generator \
  poetry run playwright --version
```

### Out of Memory

**Issue**: Container killed due to OOM

**Solutions**:
```bash
# Increase Docker memory limit
docker update --memory 2g linkedin-cv-generator

# In docker-compose.yml
services:
  linkedin-cv:
    deploy:
      resources:
        limits:
          memory: 2G
```

### PDF Generation Fails

**Issue**: WeasyPrint errors

**Solutions**:
```bash
# Check system dependencies
docker exec linkedin-cv-generator \
  python3 -c "import cairo, gi; print('OK')"

# Rebuild with dependencies
docker build --no-cache -t linkedin-cv:latest .
```

### Session/Authentication Issues

**Issue**: LinkedIn authentication fails

**Solutions**:
1. Generate new encryption key
2. Delete old sessions: `rm -rf sessions/*`
3. Login again: `docker exec -it linkedin-cv-generator python3 -m src.cli --login`
4. Check browser automation: Ensure Playwright is working

---

## Performance Optimization

### 1. Build Optimization

```dockerfile
# Use multi-stage builds (already implemented)
# Minimize layers
# Clean up package caches
```

### 2. Runtime Optimization

```bash
# Limit resources appropriately
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 512M
```

### 3. Caching (Future Enhancement)

```yaml
# Enable Redis caching (when implemented)
redis:
  image: redis:7-alpine
  restart: unless-stopped
```

---

## Backup & Recovery

### Backup

```bash
# Backup sessions and output
tar -czf linkedin-cv-backup-$(date +%Y%m%d).tar.gz \
  sessions/ \
  output/ \
  .env

# Backup to remote
rsync -avz sessions/ output/ user@backup-server:/backups/linkedin-cv/
```

### Restore

```bash
# Restore from backup
tar -xzf linkedin-cv-backup-YYYYMMDD.tar.gz

# Restore permissions
chmod 600 .env
chmod 700 sessions/
chmod 755 output/
```

---

## Scaling (Future)

### Horizontal Scaling

For high-volume deployments:

1. **Load Balancer**: Distribute requests across multiple instances
2. **Shared Storage**: Use NFS or S3 for output directory
3. **Session Store**: Use Redis or database for sessions
4. **Queue System**: Implement job queue (Celery + Redis)

### Example Architecture

```
                    ┌─────────────┐
                    │Load Balancer│
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │Instance 1 │    │Instance 2 │    │Instance 3 │
    └───────────┘    └───────────┘    └───────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼──────┐
                    │Shared Storage│
                    └─────────────┘
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t linkedin-cv:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag linkedin-cv:${{ github.sha }} registry.example.com/linkedin-cv:latest
          docker push registry.example.com/linkedin-cv:latest
      
      - name: Deploy to production
        run: |
          ssh user@prod-server "docker pull registry.example.com/linkedin-cv:latest && docker-compose up -d"
```

---

## Support

For deployment issues:

1. Check logs: `docker logs linkedin-cv-generator`
2. Verify configuration: `docker exec linkedin-cv-generator env`
3. Test manually: `docker exec -it linkedin-cv-generator /bin/bash`
4. Review this guide
5. Open an issue on GitHub with:
   - Deployment method (Docker/Compose/Bare metal)
   - Error messages and logs
   - System information

---

**Version**: v0.6.0  
**Last Updated**: 2025-11-05  
**Deployment Methods**: Docker, Docker Compose, Bare Metal
