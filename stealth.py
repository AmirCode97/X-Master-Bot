# -*- coding: utf-8 -*-
"""
X Automation Bot - Stealth Module
ماژول ضد-تشخیص برای مخفی کردن Playwright از سیستم‌های تشخیص ربات
"""

# اسکریپت JavaScript برای مخفی کردن نشانه‌های Playwright
STEALTH_JS = """
() => {
    // 1. حذف خاصیت webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true
    });
    
    // 2. جعل plugins (مرورگر واقعی plugin دارد)
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const plugins = [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', filename: 'internal-nacl-plugin' }
            ];
            plugins.item = (i) => plugins[i] || null;
            plugins.namedItem = (name) => plugins.find(p => p.name === name) || null;
            plugins.refresh = () => {};
            return plugins;
        },
        configurable: true
    });
    
    // 3. جعل languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en', 'fa'],
        configurable: true
    });
    
    // 4. حذف خاصیت‌های اتوماسیون Chrome
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // 5. جعل permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    
    // 6. جعل WebGL Vendor و Renderer
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        // UNMASKED_RENDERER_WEBGL
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.call(this, parameter);
    };
    
    // 7. حذف Playwright از navigator
    for (const prop of ['__playwright', '__pw_manual', '__PW_inspect']) {
        if (prop in window) {
            delete window[prop];
        }
    }
    
    // 8. جعل connection (برای تشخیص سرعت واقعی)
    Object.defineProperty(navigator, 'connection', {
        get: () => ({
            effectiveType: '4g',
            rtt: 50,
            downlink: 10,
            saveData: false
        }),
        configurable: true
    });
    
    // 9. جعل hardwareConcurrency (تعداد هسته CPU)
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 8,
        configurable: true
    });
    
    // 10. جعل deviceMemory
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8,
        configurable: true
    });
    
    // 11. حذف Headless Chrome شناسه‌ها
    Object.defineProperty(navigator, 'userAgent', {
        get: () => navigator.userAgent.replace('Headless', ''),
        configurable: true
    });
    
    // 12. جعل screen properties
    Object.defineProperty(screen, 'colorDepth', {
        get: () => 24,
        configurable: true
    });
    
    Object.defineProperty(screen, 'pixelDepth', {
        get: () => 24,
        configurable: true
    });
    
    console.log('🛡️ Stealth mode activated');
}
"""


# اسکریپت برای حرکت طبیعی موس
NATURAL_MOUSE_JS = """
(startX, startY, endX, endY, steps) => {
    return new Promise((resolve) => {
        const points = [];
        
        // منحنی بزیه برای حرکت طبیعی
        const controlX = (startX + endX) / 2 + (Math.random() - 0.5) * 100;
        const controlY = (startY + endY) / 2 + (Math.random() - 0.5) * 100;
        
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const x = Math.pow(1-t, 2) * startX + 2 * (1-t) * t * controlX + Math.pow(t, 2) * endX;
            const y = Math.pow(1-t, 2) * startY + 2 * (1-t) * t * controlY + Math.pow(t, 2) * endY;
            points.push({x: Math.round(x), y: Math.round(y)});
        }
        
        resolve(points);
    });
}
"""


def apply_stealth(page) -> None:
    """
    اعمال تنظیمات ضد-تشخیص به صفحه
    
    Args:
        page: شیء Page از Playwright
    """
    # اجرای اسکریپت stealth قبل از هر navigation
    page.add_init_script(STEALTH_JS)


def get_natural_mouse_path(page, start_x: int, start_y: int, end_x: int, end_y: int, steps: int = 20) -> list:
    """
    محاسبه مسیر طبیعی موس با منحنی بزیه
    
    Args:
        page: شیء Page
        start_x, start_y: نقطه شروع
        end_x, end_y: نقطه پایان
        steps: تعداد گام‌ها
        
    Returns:
        لیست نقاط مسیر
    """
    return page.evaluate(
        NATURAL_MOUSE_JS,
        [start_x, start_y, end_x, end_y, steps]
    )


# لیست User-Agent های موبایل (برای استفاده آینده)
MOBILE_USER_AGENTS = [
    # iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    # Android
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]
