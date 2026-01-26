# -*- coding: utf-8 -*-
"""
X Automation Bot - Main Module
ربات هوشمند اتوماسیون X با امنیت پیشرفته و رفتار انسانی
"""

import os
import sys
import time
import random
import logging
import tempfile
import subprocess
import platform
from datetime import datetime
from typing import Optional, Dict, Any, List

from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser

# Load .env file if exists (for local execution)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, using system env vars

from config import Config, RateLimits
from stealth import apply_stealth

# ============================================
# تنظیمات لاگینگ
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class XBot:
    """
    ربات هوشمند X با قابلیت‌های:
    - بازدید ناشناس با Tor
    - لایک، ریتوییت، فالو/آنفالو امن
    - ضد-تشخیص پیشرفته
    - رفتار شبیه انسان
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        مقداردهی اولیه ربات
        
        Args:
            config: تنظیمات سفارشی (اختیاری)
        """
        self.config = config or Config.get_default()
        self.rate_limits = self.config.rate_limits
        
        # متغیرهای محیطی
        urls_string: str = os.getenv("X_TARGET_URL", "")
        self.target_urls: List[str] = Config.parse_target_urls(urls_string)
        self.current_url: str = ""  # URL فعلی در حال بازدید
        self.cookie_json: str = os.getenv("X_COOKIE_JSON", "")
        self.my_username: str = os.getenv("X_USERNAME", "")
        
        # آمار
        self.stats = {
            "views": 0,
            "likes": 0,
            "reposts": 0,
            "follows": 0,
            "unfollows": 0,
            "errors": 0,
        }
        
        # فایل موقت برای کوکی‌ها
        self._temp_cookie_file: Optional[str] = None
    
    # ============================================
    # متدهای کمکی
    # ============================================
    
    def _human_delay(self, min_s: Optional[float] = None, max_s: Optional[float] = None) -> None:
        """
        ایجاد وقفه تصادفی شبیه رفتار انسانی
        
        Args:
            min_s: حداقل ثانیه
            max_s: حداکثر ثانیه
        """
        min_delay = min_s or self.rate_limits.min_action_delay
        max_delay = max_s or self.rate_limits.max_action_delay
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _natural_scroll(self, page: Page, count: int = 3) -> None:
        """
        اسکرول طبیعی صفحه با سرعت متغیر
        
        Args:
            page: شیء صفحه
            count: تعداد اسکرول‌ها
        """
        for _ in range(count):
            scroll_amount = random.randint(300, 700)
            page.mouse.wheel(0, scroll_amount)
            self._human_delay(
                self.rate_limits.min_scroll_delay,
                self.rate_limits.max_scroll_delay
            )
    
    def _renew_tor_ip(self) -> bool:
        """
        تغییر IP با ریلود کردن سرویس Tor
        
        Returns:
            True اگر موفق بود
        """
        logger.info("🔄 در حال تغییر IP از طریق Tor...")
        
        try:
            system = platform.system()
            
            if system == "Linux":
                subprocess.run(
                    ["sudo", "service", "tor", "reload"],
                    check=True,
                    capture_output=True,
                    timeout=30
                )
            elif system == "Windows":
                # در ویندوز Tor باید به صورت service نصب باشد
                subprocess.run(
                    ["net", "stop", "tor"],
                    capture_output=True,
                    timeout=15
                )
                time.sleep(2)
                subprocess.run(
                    ["net", "start", "tor"],
                    capture_output=True,
                    timeout=15
                )
            elif system == "Darwin":  # macOS
                subprocess.run(
                    ["brew", "services", "restart", "tor"],
                    check=True,
                    capture_output=True,
                    timeout=30
                )
            
            time.sleep(self.rate_limits.tor_reload_wait)
            logger.info("✅ IP با موفقیت تغییر کرد")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout در تغییر IP")
            return False
        except Exception as e:
            logger.error(f"❌ خطا در تغییر IP: {e}")
            return False
    
    def _create_stealth_context(self, browser: Browser, with_cookies: bool = False) -> BrowserContext:
        """
        ایجاد context مرورگر با تنظیمات ضد-تشخیص
        
        Args:
            browser: شیء مرورگر
            with_cookies: استفاده از کوکی‌های ذخیره شده
            
        Returns:
            BrowserContext پیکربندی شده
        """
        fingerprint = self.config.get_random_fingerprint()
        
        context_opts = {
            "user_agent": fingerprint["user_agent"],
            "viewport": fingerprint["viewport"],
            "locale": fingerprint["locale"],
            "timezone_id": fingerprint["timezone_id"],
            "color_scheme": random.choice(["light", "dark"]),
            "reduced_motion": random.choice(["reduce", "no-preference"]),
            "has_touch": False,
            "is_mobile": False,
            "java_script_enabled": True,
            "bypass_csp": True,
            "ignore_https_errors": True,
        }
        
        # اضافه کردن کوکی‌ها به صورت امن
        if with_cookies and self.cookie_json:
            try:
                # ایجاد فایل موقت امن
                fd, temp_path = tempfile.mkstemp(suffix='.json', prefix='x_cookies_')
                with os.fdopen(fd, 'w') as f:
                    f.write(self.cookie_json)
                
                self._temp_cookie_file = temp_path
                context_opts["storage_state"] = temp_path
                logger.info("🔐 کوکی‌ها به صورت امن بارگذاری شدند")
                
            except Exception as e:
                logger.error(f"❌ خطا در بارگذاری کوکی: {e}")
        
        context = browser.new_context(**context_opts)
        
        # اضافه کردن headers اضافی
        context.set_extra_http_headers({
            "Accept-Language": f"{fingerprint['locale']},en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        })
        
        return context
    
    def _cleanup(self) -> None:
        """پاکسازی فایل‌های موقت"""
        if self._temp_cookie_file and os.path.exists(self._temp_cookie_file):
            try:
                os.remove(self._temp_cookie_file)
                logger.debug("🧹 فایل موقت کوکی پاک شد")
            except Exception as e:
                logger.warning(f"⚠️ خطا در پاکسازی فایل موقت: {e}")
            finally:
                self._temp_cookie_file = None
    
    # ============================================
    # عملیات اصلی
    # ============================================
    
    def view_and_interact(self, page: Page, target_url: str, is_admin: bool = False) -> bool:
        """
        بازدید از پست هدف و تعامل
        
        Args:
            page: شیء صفحه
            target_url: لینک پست هدف
            is_admin: آیا لاگین است؟
            
        Returns:
            True اگر موفق بود
        """
        self.current_url = target_url
        
        try:
            logger.info(f"🔗 در حال بارگذاری: {target_url}")
            page.goto(target_url, timeout=90000, wait_until="domcontentloaded")
            self._human_delay(3, 6)
            
            # بررسی و Retry اگر خطا داد
            for retry_attempt in range(3):
                # چک کردن خطای "Something went wrong"
                retry_btn = page.query_selector('button:has-text("Retry")')
                if retry_btn:
                    logger.warning(f"⚠️ خطای X - تلاش مجدد {retry_attempt + 1}/3...")
                    retry_btn.click()
                    self._human_delay(3, 5)
                else:
                    break
            
            # گرفتن اسکرین‌شات برای debug
            try:
                screenshot_name = f"debug_screenshot_{self.stats['views'] + 1}.png"
                page.screenshot(path=screenshot_name)
                logger.info(f"📸 اسکرین‌شات ذخیره شد: {screenshot_name}")
                
                # لاگ کردن URL فعلی و عنوان صفحه
                current_url = page.url
                page_title = page.title()
                logger.info(f"📍 URL فعلی: {current_url}")
                logger.info(f"📄 عنوان صفحه: {page_title}")
                
                # چک کردن آیا صفحه واقعاً لود شده
                page_content = page.content()
                if "Something went wrong" in page_content:
                    logger.warning("⚠️ صفحه هنوز خطا دارد")
                elif "Log in" in page_title or "login" in current_url.lower():
                    logger.warning("⚠️ صفحه لاگین نشان داده شد - کوکی کار نکرد")
                else:
                    logger.info("✅ صفحه با موفقیت لود شد")
            except Exception as e:
                logger.warning(f"⚠️ خطا در گرفتن اسکرین‌شات: {e}")
            
            # اسکرول طبیعی
            self._natural_scroll(page, random.randint(2, 4))
            
            self.stats["views"] += 1
            logger.info("👁️ بازدید ثبت شد")
            
            if is_admin:
                self._admin_actions(page)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در بازدید: {e}")
            self.stats["errors"] += 1
            return False
    
    def _admin_actions(self, page: Page) -> None:
        """
        عملیات ادمین: لایک، ریتوییت، فالو، آنفالو
        
        Args:
            page: شیء صفحه
        """
        # لایک
        try:
            like_btn = page.query_selector('button[data-testid="like"]')
            logger.info(f"🔍 جستجوی دکمه لایک: {'پیدا شد ✅' if like_btn else 'پیدا نشد ❌'}")
            
            if like_btn:
                like_btn.click()
                self.stats["likes"] += 1
                logger.info("❤️ پست لایک شد")
                self._human_delay()
            else:
                # شاید قبلاً لایک شده - بررسی unlike
                unlike_btn = page.query_selector('button[data-testid="unlike"]')
                if unlike_btn:
                    logger.info("💔 پست قبلاً لایک شده بود")
                else:
                    logger.warning("⚠️ نه دکمه like و نه unlike پیدا نشد!")
        except Exception as e:
            logger.warning(f"⚠️ خطا در لایک: {e}")
        
        # ریپست (ریتوییت) - غیرفعال شده
        # کاربر نمی‌خواهد پست خودش را ریتوییت کند
        # try:
        #     repost_btn = page.query_selector('button[data-testid="retweet"]')
        #     if repost_btn:
        #         repost_btn.click()
        #         self._human_delay(0.5, 1.5)
        #         
        #         confirm_btn = page.query_selector('div[data-testid="retweetConfirm"]')
        #         if confirm_btn:
        #             confirm_btn.click()
        #             self.stats["reposts"] += 1
        #             logger.info("🔁 پست ریپست شد")
        #             self._human_delay()
        # except Exception as e:
        #     logger.debug(f"Repost skipped: {e}")
        
        # فالو
        self._smart_follow(page)
        
        # آنفالو
        if self.my_username:
            self._smart_unfollow(page)
    
    def _smart_follow(self, page: Page) -> None:
        """
        فالو کردن هوشمند از لیست لایک‌کنندگان
        
        Args:
            page: شیء صفحه
        """
        follow_count = self.rate_limits.get_follow_count()
        logger.info(f"👥 تلاش برای فالو {follow_count} کاربر...")
        
        try:
            # رفتن به لیست لایک‌ها
            current_url = page.url.split('?')[0]
            likes_url = f"{current_url}/likes"
            page.goto(likes_url, timeout=30000)
            self._human_delay(3, 5)
            
            # پیدا کردن دکمه‌های فالو
            follow_buttons = page.query_selector_all('button[aria-label^="Follow"]')
            
            followed = 0
            for btn in follow_buttons:
                if followed >= follow_count:
                    break
                
                try:
                    text = btn.inner_text()
                    if "Follow" in text and "Following" not in text:
                        btn.click()
                        followed += 1
                        self.stats["follows"] += 1
                        logger.info(f"➕ فالو {followed}/{follow_count}")
                        self._human_delay()
                except Exception:
                    continue
            
            # برگشت به صفحه اصلی
            page.goto(self.current_url, timeout=30000)
            
        except Exception as e:
            logger.warning(f"⚠️ خطا در فالو: {e}")
    
    def _smart_unfollow(self, page: Page) -> None:
        """
        آنفالو کردن کسانی که فالوبک نداده‌اند
        
        Args:
            page: شیء صفحه
        """
        unfollow_count = self.rate_limits.get_unfollow_count()
        logger.info(f"👤 بررسی برای آنفالو {unfollow_count} کاربر...")
        
        try:
            # رفتن به لیست following
            following_url = f"https://x.com/{self.my_username}/following"
            page.goto(following_url, timeout=60000)
            self._human_delay(4, 7)
            
            user_cells = page.query_selector_all('div[data-testid="UserCell"]')
            
            unfollowed = 0
            for cell in user_cells:
                if unfollowed >= unfollow_count:
                    break
                
                try:
                    cell_text = cell.inner_text()
                    
                    # فقط آنفالو کسانی که بک ندادند
                    if "Follows you" not in cell_text:
                        following_btn = cell.query_selector('button[aria-label^="Following"]')
                        
                        if following_btn:
                            following_btn.click()
                            self._human_delay(0.8, 1.5)
                            
                            # تایید آنفالو
                            confirm_btn = page.query_selector('button[data-testid="confirmationSheetConfirm"]')
                            if confirm_btn:
                                confirm_btn.click()
                                unfollowed += 1
                                self.stats["unfollows"] += 1
                                logger.info(f"➖ آنفالو {unfollowed}/{unfollow_count}")
                                self._human_delay()
                except Exception:
                    continue
            
        except Exception as e:
            logger.warning(f"⚠️ خطا در آنفالو: {e}")
    
    # ============================================
    # گزارش و اجرا
    # ============================================
    
    def _send_telegram_message(self, text: str) -> bool:
        """ارسال پیام به تلگرام"""
        token = os.getenv("TELEGRAM_BOT_TOKEN", self.config.telegram_token)
        chat_id = os.getenv("TELEGRAM_CHAT_ID", self.config.telegram_chat_id)
        
        if not token or not chat_id:
            return False
            
        try:
            import requests
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            requests.post(url, json=payload, timeout=10)
            return True
        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیام تلگرام: {e}")
            return False

    def _save_report(self) -> None:
        """ذخیره گزارش عملیات و ارسال به تلگرام"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        stats_text = (
            f"👀 Views: {self.stats['views']}\n"
            f"❤️ Likes: {self.stats['likes']}\n"
            f"🔁 Reposts: {self.stats['reposts']}\n"
            f"➕ Follows: {self.stats['follows']}\n"
            f"➖ Unfollows: {self.stats['unfollows']}\n"
            f"⚠️ Errors: {self.stats['errors']}"
        )
        
        stats_single_line = stats_text.replace('\n', ' | ')
        report_line = f"[{timestamp}] {stats_single_line}\n"
        
        try:
            with open(self.config.report_file, "a", encoding="utf-8") as f:
                f.write(report_line)
            logger.info(f"📊 گزارش ذخیره شد: {self.config.report_file}")
            
            # ارسال به تلگرام
            telegram_msg = f"<b>🏰 X-Master-Bot Report</b>\n\n📅 {timestamp}\n\n{stats_text}\n\n✅ <i>اجرا با موفقیت به پایان رسید.</i>"
            self._send_telegram_message(telegram_msg)
            
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره گزارش: {e}")
    
    def run(self) -> None:
        """اجرای اصلی ربات"""
        logger.info("=" * 50)
        logger.info("🚀 شروع X Master Bot")
        logger.info("=" * 50)
        
        if not self.target_urls:
            logger.error("❌ لینک هدف (X_TARGET_URL) تنظیم نشده یا معتبر نیست!")
            return
        
        logger.info(f"🎯 تعداد URL های هدف: {len(self.target_urls)}")
        for idx, url in enumerate(self.target_urls, 1):
            logger.info(f"   {idx}. {url}")
        
        # هر URL به تعداد views_per_url بازدید می‌گیرد
        views_per_url = self.rate_limits.views_per_url
        total_views = views_per_url * len(self.target_urls)
        
        logger.info(f"📊 هر URL: {views_per_url} بازدید | کل: {total_views} بازدید")
        
        for i in range(total_views):
            # انتخاب URL به صورت چرخشی
            url_index = i % len(self.target_urls)
            current_target = self.target_urls[url_index]
            
            logger.info(f"\n{'='*20} دور {i+1}/{total_views} {'='*20}")
            logger.info(f"🎯 هدف: {current_target}")
            
            # تغییر IP (به جز دور اول) - فقط اگر Tor فعال باشد
            if i > 0 and self.config.tor.use_tor:
                self._renew_tor_ip()
            
            try:
                with sync_playwright() as p:
                    # تنظیمات launch
                    launch_opts = {
                        "headless": self.config.headless,
                        "args": [
                            "--disable-blink-features=AutomationControlled",
                            "--disable-dev-shm-usage",
                            "--no-sandbox",
                        ]
                    }
                    
                    # تنظیمات پروکسی
                    if self.config.proxy:
                        launch_opts["proxy"] = self.config.proxy
                    
                    browser = p.chromium.launch(**launch_opts)
                    
                    # فقط در دور اول از کوکی استفاده کن (برای همه URLها یکبار ادمین)
                    is_admin = (i < len(self.target_urls) and bool(self.cookie_json))
                    context = self._create_stealth_context(browser, with_cookies=is_admin)
                    
                    page = context.new_page()
                    
                    # اعمال stealth
                    apply_stealth(page)
                    
                    status = "Admin" if is_admin else "Anonymous"
                    logger.info(f"🌐 Status: {status}")
                    
                    # بازدید و تعامل
                    self.view_and_interact(page, current_target, is_admin=is_admin)
                    
                    # بستن مرورگر
                    context.close()
                    browser.close()
                    
            except Exception as e:
                logger.error(f"❌ خطای browser: {e}")
                self.stats["errors"] += 1
            
            finally:
                self._cleanup()
                self._human_delay(2, 4)
        
        # ذخیره گزارش نهایی
        self._save_report()
        
        logger.info("\n" + "=" * 50)
        logger.info("✅ اجرا تمام شد!")
        logger.info(f"📈 آمار: {self.stats}")
        logger.info("=" * 50)


# ============================================
# نقطه ورود
# ============================================

def main():
    """نقطه ورود اصلی"""
    # بررسی حالت تست
    test_mode = "--test-mode" in sys.argv
    
    config = Config.get_default()
    
    if test_mode:
        config.headless = False
        config.test_mode = True
        config.rate_limits.views_per_run = 2
        logger.info("🧪 حالت تست فعال است")
    
    bot = XBot(config)
    bot.run()


if __name__ == "__main__":
    main()
