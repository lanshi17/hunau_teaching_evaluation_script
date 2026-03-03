import sys

from src.config import load_settings
from src.spider import TeachingEvalSpider


def main():
    settings = load_settings()

    print("=" * 50)
    print("  湖南农业大学 - 教学评价自动化脚本")
    print("=" * 50)
    print()

    if settings.username and settings.password:
        print(f"[INFO] 当前账号: {settings.username}")
    else:
        print("[INFO] 未配置账号密码，将使用二维码扫码登录")

    print(f"[INFO] HEADLESS 模式: {settings.headless}")
    print(f"[INFO] CHROMEDRIVER: {settings.chromedriver_bin or 'PATH/AUTO'}")
    print(f"[INFO] AUTO_INSTALL_DRIVER: {settings.auto_install_driver}")
    if settings.webdriver_proxy:
        print(f"[INFO] WEBDRIVER_PROXY: {settings.webdriver_proxy}")

    if settings.chromedriver_path and not settings.chromedriver_bin:
        print(f"[ERROR] HUNAU_CHROMEDRIVER_PATH 无效: {settings.chromedriver_path}")
        print("[ERROR] 请提供可执行 chromedriver 绝对路径，或留空并开启自动下载")
        sys.exit(1)

    if not settings.chromedriver_bin and not settings.auto_install_driver:
        print("[ERROR] 未检测到 chromedriver，且已禁用自动下载")
        print("[ERROR] 请设置 HUNAU_CHROMEDRIVER_PATH 或将 chromedriver 加入 PATH")
        print("[ERROR] 或设置 HUNAU_AUTO_INSTALL_DRIVER=true")
        sys.exit(1)

    if settings.headless and not (settings.username and settings.password):
        print("[ERROR] 当前为无头模式且未配置账号密码，无法进行二维码扫码登录")
        print("[ERROR] 请在 .env.local 配置账号密码，或设置 HUNAU_HEADLESS=false")
        sys.exit(1)

    print()
    TeachingEvalSpider(thread_count=1).run()


if __name__ == "__main__":
    main()
