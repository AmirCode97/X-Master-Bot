# -*- coding: utf-8 -*-
"""
X Automation Bot - Configuration Module
تنظیمات مرکزی ربات با پارامترهای امنیتی و ضد-تشخیص
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict

# ============================================
# نرخ‌های محدودیت (Rate Limits)
# ============================================

@dataclass
class RateLimits:
    """محدودیت‌های امن برای جلوگیری از شناسایی"""
    
    views_per_run: int = 7            # تعداد بازدید در هر اجرا
    min_follow_per_run: int = 0      # فالو غیرفعال - فقط بازدید و لایک
    max_follow_per_run: int = 0      # فالو غیرفعال
    min_unfollow_per_run: int = 0    # آنفالو غیرفعال
    max_unfollow_per_run: int = 0    # آنفالو غیرفعال
    
    # تاخیرهای انسانی (ثانیه) - افزایش برای رفتار طبیعی‌تر
    min_action_delay: float = 3.0
    max_action_delay: float = 8.0
    min_scroll_delay: float = 1.0
    max_scroll_delay: float = 3.0
    page_load_wait: float = 8.0
    
    # Tor
    tor_reload_wait: int = 10
    
    def get_follow_count(self) -> int:
        """تعداد تصادفی فالو برای این اجرا"""
        return random.randint(self.min_follow_per_run, self.max_follow_per_run)
    
    def get_unfollow_count(self) -> int:
        """تعداد تصادفی آنفالو برای این اجرا"""
        return random.randint(self.min_unfollow_per_run, self.max_unfollow_per_run)


# ============================================
# هویت‌های جعلی (Fingerprints)
# ============================================

USER_AGENTS: List[str] = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # Safari Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    
    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Chrome Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

VIEWPORTS: List[Dict[str, int]] = [
    {"width": 1920, "height": 1080},
    {"width": 1680, "height": 1050},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 800},
    {"width": 1280, "height": 720},
]

TIMEZONES: List[str] = [
    "America/New_York",
    "America/Chicago",
    "America/Los_Angeles",
    "America/Denver",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Australia/Sydney",
]

LOCALES: List[str] = [
    "en-US",
    "en-GB",
    "en-CA",
    "en-AU",
]


# ============================================
# تنظیمات Tor
# ============================================

@dataclass
class TorConfig:
    """تنظیمات پروکسی Tor"""
    
    # Tor غیرفعال - X آی‌پی‌های Tor را بلاک می‌کند
    use_tor: bool = False
    host: str = "127.0.0.1"
    port: int = 9050
    control_port: int = 9051
    
    @property
    def proxy_url(self) -> str:
        return f"socks5://{self.host}:{self.port}" if self.use_tor else None


# ============================================
# تنظیمات اصلی
# ============================================

@dataclass
class Config:
    """تنظیمات کامل ربات"""
    
    rate_limits: RateLimits = field(default_factory=RateLimits)
    tor: TorConfig = field(default_factory=TorConfig)
    
    # تنظیمات پروکسی
    custom_proxy: str = ""           # پروکسی سفارشی (مثل http://user:pass@ip:port)
    
    # فایل‌ها
    report_file: str = "report.txt"
    
    @property
    def proxy(self) -> dict:
        """برگرداندن تنظیمات پروکسی برای Playwright"""
        import os
        proxy_str = os.getenv("X_PROXY", self.custom_proxy)
        
        if proxy_str:
            return {"server": proxy_str}
        
        if self.tor.use_tor:
            return {"server": self.tor.proxy_url}
            
        return None
    
    @staticmethod
    def parse_target_urls(urls_string: str) -> List[str]:
        """
        تبدیل رشته URLها به لیست
        پشتیبانی از جداکننده‌های: کاما، خط جدید، پایپ
        
        Args:
            urls_string: رشته حاوی URLها
            
        Returns:
            لیست URLهای معتبر
        """
        if not urls_string:
            return []
        
        # جایگزینی جداکننده‌های مختلف با کاما
        normalized = urls_string.replace('\n', ',').replace('|', ',')
        
        # جدا کردن و تمیز کردن
        urls = [url.strip() for url in normalized.split(',')]
        
        # فیلتر URLهای خالی و معتبر
        valid_urls = [url for url in urls if url and url.startswith('https://x.com/')]
        
        return valid_urls
    
    def get_random_fingerprint(self) -> Dict:
        """تولید اثرانگشت تصادفی برای هر session"""
        return {
            "user_agent": random.choice(USER_AGENTS),
            "viewport": random.choice(VIEWPORTS),
            "timezone_id": random.choice(TIMEZONES),
            "locale": random.choice(LOCALES),
        }
    
    @staticmethod
    def get_default() -> "Config":
        """برگرداندن تنظیمات پیش‌فرض"""
        return Config()
