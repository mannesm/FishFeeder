# Deploying to Raspberry Pi

## Recommended Directory Structure

Use a permanent location for your project, **not /tmp**.

### Option 1: User Home Directory (Recommended)

```bash
# Create a projects directory
mkdir -p ~/projects
cd ~/projects

# Clone or copy your project here
# Result: /home/mannes/projects/FishFeeder
```

### Option 2: /opt Directory (For System Services)

```bash
# Create directory (requires sudo)
sudo mkdir -p /opt/fishfeeder
sudo chown -R $USER:$USER /opt/fishfeeder
cd /opt/fishfeeder

# Copy your project here
# Result: /opt/fishfeeder
```

### Option 3: Dedicated Apps Directory

```bash
# Create apps directory
mkdir -p ~/apps
cd ~/apps

# Copy your project here
# Result: /home/mannes/apps/FishFeeder
```

## Deployment Methods

### Method 1: Git (Best Practice)

#### On Your Development Machine:
```bash
# Initialize git repo if not already done
cd /Users/mannes/PycharmProjects/FishFeeder
git init
git add .
git commit -m "Initial commit"

# Push to GitHub/GitLab (create repo first)
git remote add origin https://github.com/yourusername/fishfeeder.git
git push -u origin main
```

#### On Your Raspberry Pi:
```bash
# Clone the repository
cd ~/projects
git clone https://github.com/yourusername/fishfeeder.git
cd fishfeeder

# Copy environment file
cp .env.example .env
nano .env  # Customize settings

# Deploy
./start.sh
```

#### To Update:
```bash
cd ~/projects/fishfeeder
git pull
docker-compose down
docker-compose up -d --build
```

### Method 2: rsync (Quick Development Sync)

This is better than PyCharm's /tmp sync!

#### On Your Development Machine:
```bash
# Sync to Pi (excludes unnecessary files)
rsync -avz --exclude='.git' \
           --exclude='.venv' \
           --exclude='__pycache__' \
           --exclude='.idea' \
           --exclude='*.pyc' \
  /Users/mannes/PycharmProjects/FishFeeder/ \
  mannes@raspberrypi:~/projects/fishfeeder/

# Or use the sync script we'll create
```

#### Create a Sync Script:

Create this on your Mac at `/Users/mannes/PycharmProjects/FishFeeder/sync-to-pi.sh`:

```bash
#!/bin/bash
# Sync script for development

PI_USER="mannes"
PI_HOST="raspberrypi"
PI_PATH="~/projects/fishfeeder"
LOCAL_PATH="/Users/mannes/PycharmProjects/FishFeeder"

echo "🔄 Syncing FishFeeder to Raspberry Pi..."

rsync -avz --delete \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.idea' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  "$LOCAL_PATH/" \
  "$PI_USER@$PI_HOST:$PI_PATH/"

echo "✅ Sync complete!"
echo ""
echo "To deploy on Pi:"
echo "  ssh $PI_USER@$PI_HOST 'cd $PI_PATH && docker-compose up -d --build'"
```

Then:
```bash
chmod +x sync-to-pi.sh
./sync-to-pi.sh
```

### Method 3: PyCharm Remote Deployment (Configured Properly)

#### Configure PyCharm to use permanent directory:

1. **Tools → Deployment → Configuration**
2. Add new SFTP connection to your Pi
3. Set **Root path** to: `/home/mannes/projects/fishfeeder`
4. Set **Mappings**:
   - Local path: `/Users/mannes/PycharmProjects/FishFeeder`
   - Deployment path: `/`
5. **Excluded Paths**: Add `.venv`, `__pycache__`, `.git`, `.idea`

#### Auto-upload on save:
1. **Tools → Deployment → Options**
2. Check "Upload changed files automatically to the default server"
3. Select "On explicit save action"

## Setting Up on Raspberry Pi (First Time)

```bash
# 1. Create project directory
mkdir -p ~/projects/fishfeeder
cd ~/projects/fishfeeder

# 2. Copy/sync your files here (using one of the methods above)

# 3. Create .env file
cp .env.example .env
nano .env  # Adjust settings

# 4. Make scripts executable
chmod +x start.sh

# 5. Start the service
./start.sh

# 6. Verify it's running
docker ps
curl http://localhost:8000/health
```

## Running as a System Service (Production)

For a production fish feeder that should always run:

### Create systemd service:

```bash
sudo nano /etc/systemd/system/fishfeeder.service
```

Add this content:

```ini
[Unit]
Description=Fish Feeder Servo Controller
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/mannes/projects/fishfeeder
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=mannes
Group=mannes

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fishfeeder.service
sudo systemctl start fishfeeder.service

# Check status
sudo systemctl status fishfeeder.service
```

Now it will start automatically on boot!

## Backup Strategy

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups/fishfeeder
mkdir -p $BACKUP_DIR

tar -czf $BACKUP_DIR/fishfeeder_backup_$DATE.tar.gz \
  -C ~/projects \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  fishfeeder

echo "✅ Backup created: $BACKUP_DIR/fishfeeder_backup_$DATE.tar.gz"
```

## Quick Reference

### Current Setup (❌ Not Good):
```
/tmp/pycharm_project_280  # Gets deleted on reboot!
```

### Recommended Setup (✅ Good):
```
/home/mannes/projects/fishfeeder  # Permanent location
```

### Your Workflow Should Be:

**Development (on Mac):**
```bash
# Make changes in PyCharm
# Sync to Pi
./sync-to-pi.sh
```

**Deployment (on Pi):**
```bash
cd ~/projects/fishfeeder
docker-compose up -d --build
```

## Migration from /tmp

If you currently have it running in /tmp:

```bash
# On Raspberry Pi:

# 1. Stop current container
cd /tmp/pycharm_project_280
docker-compose down

# 2. Create new permanent location
mkdir -p ~/projects/fishfeeder

# 3. Copy everything
cp -r /tmp/pycharm_project_280/* ~/projects/fishfeeder/

# 4. Move to new location and start
cd ~/projects/fishfeeder
./start.sh

# 5. Verify it works
docker ps
curl http://localhost:8000/health

# 6. Remove old temp files (after confirming it works)
rm -rf /tmp/pycharm_project_280
```

## Next Steps

1. ✅ Choose a permanent directory location
2. ✅ Set up proper sync method (Git or rsync)
3. ✅ Configure PyCharm deployment to use permanent path
4. ✅ Set up systemd service for auto-start
5. ✅ Create backup script

This ensures your fish feeder survives reboots and your fish keep getting fed! 🐟

