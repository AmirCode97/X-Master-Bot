#!/bin/bash
# اسکریپت نصب خودکار برای Oracle Cloud Ubuntu
# X Master Bot - Auto Install Script

echo "=============================================="
echo "   X Master Bot - Oracle Cloud Installer"
echo "=============================================="
echo ""

# آپدیت سیستم
echo "[1/6] در حال آپدیت سیستم..."
sudo apt update && sudo apt upgrade -y

# نصب پایتون و ابزارها
echo "[2/6] در حال نصب پایتون..."
sudo apt install python3 python3-pip python3-venv git -y

# نصب وابستگی‌های مرورگر Playwright
echo "[3/6] در حال نصب وابستگی‌های مرورگر..."
sudo apt install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 -y

# ساخت محیط مجازی
echo "[4/6] در حال ساخت محیط مجازی پایتون..."
cd ~/x-bot
python3 -m venv venv
source venv/bin/activate

# نصب کتابخانه‌های پایتون
echo "[5/6] در حال نصب کتابخانه‌ها..."
pip install --upgrade pip
pip install playwright python-dotenv stem

# نصب مرورگر Chromium
echo "[6/6] در حال نصب مرورگر Chromium..."
playwright install chromium

echo ""
echo "=============================================="
echo "   ✅ نصب با موفقیت انجام شد!"
echo "=============================================="
echo ""
echo "مراحل بعدی:"
echo "1. فایل .env را ویرایش کنید: nano ~/x-bot/.env"
echo "2. برای تست دستی اجرا کنید: ./run.sh"
echo "3. برای زمان‌بندی خودکار: ./setup_cron.sh"
echo ""
