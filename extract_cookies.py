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
    print("🍪 X.com Cookie Extractor")
    print("=" * 50)
    
    with sync_playwright() as p:
        # باز کردن مرورگر قابل مشاهده
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        # رفتن به صفحه لاگین
        print("\n📱 در حال باز کردن X.com...")
        page.goto("https://x.com/login")
        
        print("\n" + "=" * 50)
        print("👆 لطفاً در مرورگر وارد حساب خود شوید")
        print("   پس از لاگین موفق، اینجا Enter بزنید...")
        print("=" * 50)
        
        input("\n>>> Enter را بزنید: ")
        
        # استخراج کوکی‌ها
        print("\n🔄 در حال استخراج کوکی‌ها...")
        
        # دریافت storage state کامل
        storage = context.storage_state()
        
        # ذخیره در فایل
        output_file = "x_cookies.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(storage, f, indent=2)
        
        print(f"\n✅ کوکی‌ها ذخیره شدند: {output_file}")
        
        # نمایش برای کپی در GitHub Secrets
        print("\n" + "=" * 50)
        print("📋 این متن را در GitHub Secret کپی کنید:")
        print("   (X_COOKIE_JSON)")
        print("=" * 50)
        
        # فشرده‌سازی برای Secret
        compact_json = json.dumps(storage, separators=(',', ':'))
        print(f"\n{compact_json}")
        
        # همچنین ذخیره نسخه فشرده
        with open("x_cookies_compact.txt", "w", encoding="utf-8") as f:
            f.write(compact_json)
        
        print(f"\n💾 همچنین در فایل ذخیره شد: x_cookies_compact.txt")
        
        browser.close()
        
        print("\n" + "=" * 50)
        print("🎉 تمام! حالا این مقدار را در GitHub Secrets اضافه کنید:")
        print("   Settings → Secrets → Actions → New repository secret")
        print("   Name: X_COOKIE_JSON")
        print("   Value: محتوای x_cookies_compact.txt")
        print("=" * 50)


if __name__ == "__main__":
    extract_cookies()
