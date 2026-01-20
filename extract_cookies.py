# -*- coding: utf-8 -*-
"""
Cookie Extractor for X.com
این اسکریپت را در کامپیوتر خود اجرا کنید تا کوکی‌ها را استخراج کند
"""

from playwright.sync_api import sync_playwright
import json

def extract_cookies():
    """
    مرورگر را باز می‌کند تا لاگین کنید، سپس کوکی‌ها را ذخیره می‌کند
    """
    print("=" * 50)
    print("[COOKIE] X.com Cookie Extractor")
    print("=" * 50)
    
    with sync_playwright() as p:
        # باز کردن مرورگر قابل مشاهده
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        # رفتن به صفحه لاگین
        print("\n[INFO] Opening X.com...")
        page.goto("https://x.com/login")
        
        print("\n" + "=" * 50)
        print("[ACTION] Please login to your X account in the browser")
        print("         After successful login, press Enter here...")
        print("=" * 50)
        
        input("\n>>> Press Enter when done: ")
        
        # استخراج کوکی‌ها
        print("\n[INFO] Extracting cookies...")
        
        # دریافت storage state کامل
        storage = context.storage_state()
        
        # ذخیره در فایل
        output_file = "x_cookies.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(storage, f, indent=2)
        
        print(f"\n[SUCCESS] Cookies saved to: {output_file}")
        
        # نمایش برای کپی در GitHub Secrets
        print("\n" + "=" * 50)
        print("[COPY] Copy this text to GitHub Secret (X_COOKIE_JSON):")
        print("=" * 50)
        
        # فشرده‌سازی برای Secret
        compact_json = json.dumps(storage, separators=(',', ':'))
        
        # ذخیره نسخه فشرده
        with open("x_cookies_compact.txt", "w", encoding="utf-8") as f:
            f.write(compact_json)
        
        print(f"\n[SAVED] Compact version saved to: x_cookies_compact.txt")
        
        # نمایش خلاصه کوکی‌ها
        cookie_count = len(storage.get("cookies", []))
        print(f"[INFO] Total cookies extracted: {cookie_count}")
        
        browser.close()
        
        print("\n" + "=" * 50)
        print("[DONE] Now add this to GitHub Secrets:")
        print("  1. Go to your repo Settings > Secrets > Actions")
        print("  2. Click 'New repository secret'")
        print("  3. Name: X_COOKIE_JSON")
        print("  4. Value: Copy content from x_cookies_compact.txt")
        print("=" * 50)


if __name__ == "__main__":
    extract_cookies()
