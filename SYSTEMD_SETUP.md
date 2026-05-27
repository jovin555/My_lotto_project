# Running Lotto Max Predictor as Systemd Service

## Overview

Running the predictor as a systemd service ensures:
- ✅ Automatically starts on system boot
- ✅ Runs continuously in background
- ✅ Auto-restart if it crashes
- ✅ Easy to manage with `systemctl`
- ✅ Logs saved to journal for debugging

---

## 🚀 Quick Setup

### Step 1: Copy Service File to Systemd
```bash
sudo cp /home/eva/workspace/My_lotto_project/lotto-predictor.service /etc/systemd/system/
```

### Step 2: Reload Systemd Daemon
```bash
sudo systemctl daemon-reload
```

### Step 3: Enable Service (Start on Boot)
```bash
sudo systemctl enable lotto-predictor
```

### Step 4: Start the Service
```bash
sudo systemctl start lotto-predictor
```

### Step 5: Verify It's Running
```bash
sudo systemctl status lotto-predictor
```

---

## 🤖 Automated Setup

**Or use the setup script (easier):**

```bash
cd /home/eva/workspace/My_lotto_project
sudo bash setup_systemd.sh
```

This does all 4 steps automatically!

---

## 📊 Managing the Service

### Check Status
```bash
sudo systemctl status lotto-predictor
```

### View Live Logs
```bash
sudo journalctl -u lotto-predictor -f
```

### View Last 50 Lines of Logs
```bash
sudo journalctl -u lotto-predictor -n 50
```

### Stop the Service
```bash
sudo systemctl stop lotto-predictor
```

### Start the Service
```bash
sudo systemctl start lotto-predictor
```

### Restart the Service
```bash
sudo systemctl restart lotto-predictor
```

### Disable from Starting on Boot
```bash
sudo systemctl disable lotto-predictor
```

### Re-enable on Boot
```bash
sudo systemctl enable lotto-predictor
```

---

## ⚙️ Customizing the Schedule

The service file runs predictions **every Friday at 6:00 PM** by default:
```
ExecStart=... scheduler.py --day friday --time 18:00
```

To change the schedule, edit the service file:

```bash
sudo nano /etc/systemd/system/lotto-predictor.service
```

Change the schedule in the `ExecStart` line:
```
# Monday at 9:00 AM
ExecStart=... scheduler.py --day monday --time 09:00

# Wednesday at 3:00 PM
ExecStart=... scheduler.py --day wednesday --time 15:00

# Daily at midnight
ExecStart=... scheduler.py --day monday --time 00:00
```

Then reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart lotto-predictor
```

---

## 📋 Service File Details

**Location:** `/etc/systemd/system/lotto-predictor.service`

```ini
[Unit]
Description=Lotto Max Weekly Prediction Service
After=network.target

[Service]
Type=simple
User=eva
WorkingDirectory=/home/eva/workspace/My_lotto_project
Environment="PATH=/home/eva/workspace/My_lotto_project/venv/bin"
ExecStart=/home/eva/workspace/My_lotto_project/venv/bin/python ...
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Key settings:**
- `User=eva` - Runs as eva user
- `Restart=always` - Auto-restarts if it crashes
- `RestartSec=10` - Waits 10 seconds before restarting
- `StandardOutput=journal` - Logs to systemd journal

---

## 🔍 Debugging

### Check if service is enabled
```bash
sudo systemctl is-enabled lotto-predictor
```

### Check if service is running
```bash
sudo systemctl is-active lotto-predictor
```

### View recent errors
```bash
sudo journalctl -u lotto-predictor --since "1 hour ago"
```

### Full service details
```bash
sudo systemctl show lotto-predictor
```

---

## 📱 Verify Predictions Are Being Sent

### Check Telegram messages
Your predictions should arrive in Telegram on the scheduled day/time.

### Check prediction files
```bash
ls -lh /home/eva/workspace/My_lotto_project/weekly_predictions/
```

You should see new `prediction_*.json` and `report_*.txt` files appear weekly.

---

## ⚠️ Troubleshooting

### Service won't start
```bash
sudo journalctl -u lotto-predictor -n 100
# Look for error messages
```

### Predictions not being sent to Telegram
- Check `.env` file has correct `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Verify credentials: `cat /home/eva/workspace/My_lotto_project/.env`

### Service crashes repeatedly
- Check logs: `sudo journalctl -u lotto-predictor -f`
- Verify venv is activated properly
- Run manually to test: `python /home/eva/workspace/My_lotto_project/weekly_lotto_predictor.py`

### Can't edit service file
```bash
# Edit with sudo
sudo systemctl edit lotto-predictor
```

---

## 🛑 Remove Service

If you want to remove the service:

```bash
# Stop the service
sudo systemctl stop lotto-predictor

# Disable it
sudo systemctl disable lotto-predictor

# Remove the service file
sudo rm /etc/systemd/system/lotto-predictor.service

# Reload systemd
sudo systemctl daemon-reload
```

---

## 🎯 Summary Commands

```bash
# Install
sudo cp lotto-predictor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lotto-predictor
sudo systemctl start lotto-predictor

# Check status
sudo systemctl status lotto-predictor

# View logs
sudo journalctl -u lotto-predictor -f

# Manage
sudo systemctl stop lotto-predictor
sudo systemctl restart lotto-predictor
```

---

**For more information on systemd:**
- `man systemctl`
- `man systemd.service`
- [systemd documentation](https://systemd.io/)
