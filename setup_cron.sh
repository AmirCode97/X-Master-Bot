#!/bin/bash
# اسکریپت تنظیم زمان‌بندی خودکار (هر ۲ ساعت)
# X Master Bot - Cron Setup Script

echo "=============================================="
echo "   X Master Bot - Cron Setup (Every 2 Hours)"
echo "=============================================="
echo ""

# ساخت دستور cron
CRON_CMD="0 */2 * * * cd ~/x-bot && ~/x-bot/venv/bin/python3 main.py >> ~/x-bot/cron_log.txt 2>&1"

# بررسی آیا قبلاً اضافه شده
(crontab -l 2>/dev/null | grep -v "x-bot/venv/bin/python3 main.py"; echo "$CRON_CMD") | crontab -

echo "✅ زمان‌بندی با موفقیت تنظیم شد!"
echo ""
echo "📋 جزئیات:"
echo "   - اجرا: هر ۲ ساعت یکبار"
echo "   - گزارش: ~/x-bot/cron_log.txt"
echo ""
echo "🔧 دستورات مفید:"
echo "   - مشاهده زمان‌بندی: crontab -l"
echo "   - مشاهده گزارش: tail -f ~/x-bot/cron_log.txt"
echo "   - حذف زمان‌بندی: crontab -r"
echo ""
