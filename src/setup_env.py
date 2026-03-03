from getpass import getpass

from dotenv import dotenv_values

from src.config import ENV_FILE_PATH
from src.constants import DEFAULT_REVIEW_PROMPT


def _escape_quoted(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _env_value(existing: dict[str, str | None], key: str, default: str = "") -> str:
    value = existing.get(key)
    if value is None:
        return default
    return value


def _mask(value: str) -> str:
    if not value:
        return "(未设置)"
    if len(value) <= 2:
        return "*" * len(value)
    return value[:1] + "*" * (len(value) - 2) + value[-1:]


def _print_header():
    print("=" * 58)
    print("  HUNAU 教学评价脚本 - 环境变量交互配置")
    print("=" * 58)
    print(f"配置文件路径: {ENV_FILE_PATH}")
    print("说明：直接回车可保留默认值；密码/API Key 输入不回显。")


def _print_section(title: str, description: str):
    print()
    print("-" * 58)
    print(f"[{title}]")
    print(description)
    print("-" * 58)


def _prompt_text(
    label: str,
    default: str = "",
    required: bool = False,
    hint: str = "",
    example: str = "",
) -> str:
    print()
    print(f"{label}")
    if hint:
        print(f"  说明: {hint}")
    if example:
        print(f"  示例: {example}")

    while True:
        suffix = f" [{default}]" if default else ""
        raw = input(f"  输入{suffix}: ").strip()
        if raw:
            return raw
        if default != "":
            return default
        if not required:
            return ""
        print("  该项不能为空，请重新输入")


def _prompt_secret(label: str, default: str = "", hint: str = "") -> str:
    print()
    print(f"{label}")
    if hint:
        print(f"  说明: {hint}")

    suffix = " [已设置，直接回车保持]" if default else ""
    raw = getpass(f"  输入{suffix}: ").strip()
    if raw:
        return raw
    return default


def _prompt_bool_text(label: str, default: str, hint: str = "") -> str:
    print()
    print(f"{label}")
    if hint:
        print(f"  说明: {hint}")

    normalized_default = default.strip().lower() if default else ""
    while True:
        suffix = f" [{normalized_default}]" if normalized_default else " [true/false]"
        raw = input(f"  输入{suffix}: ").strip().lower()
        if not raw and normalized_default:
            return normalized_default
        if raw in {"true", "false"}:
            return raw
        print("  请输入 true 或 false")


def _prompt_headless(default: str) -> str:
    print()
    print("HUNAU_HEADLESS")
    print("  说明: 控制浏览器是否无头运行；留空自动判断。")

    normalized_default = default.strip().lower() if default else ""
    while True:
        suffix = (
            f" [{normalized_default}]"
            if normalized_default
            else " [留空自动/true/false]"
        )
        raw = input(f"  输入{suffix}: ").strip().lower()
        if not raw:
            return normalized_default
        if raw in {"true", "false"}:
            return raw
        print("  请输入 true、false 或直接回车")


def main():
    existing = dotenv_values(ENV_FILE_PATH)

    _print_header()

    _print_section(
        "登录配置",
        "用于 WebVPN/CAS 登录；若账号密码留空，运行时将尝试二维码登录。",
    )

    username = _prompt_text(
        "HUNAU_USERNAME",
        _env_value(existing, "HUNAU_USERNAME", ""),
        hint="学号或用户名。",
        example="SX20250001",
    )
    password = _prompt_secret(
        "HUNAU_PASSWORD",
        _env_value(existing, "HUNAU_PASSWORD", ""),
        hint="登录密码，输入时不会回显。",
    )

    _print_section(
        "浏览器与驱动配置",
        "用于控制 Chrome/Chromedriver 行为；一般默认即可。",
    )

    headless = _prompt_headless(_env_value(existing, "HUNAU_HEADLESS", ""))
    chromedriver_path = _prompt_text(
        "HUNAU_CHROMEDRIVER_PATH",
        _env_value(existing, "HUNAU_CHROMEDRIVER_PATH", ""),
        hint="本地 chromedriver 绝对路径；留空时从 PATH 查找。",
        example="/usr/local/bin/chromedriver",
    )
    auto_install_driver = _prompt_bool_text(
        "HUNAU_AUTO_INSTALL_DRIVER",
        _env_value(existing, "HUNAU_AUTO_INSTALL_DRIVER", "true") or "true",
        hint="未找到 chromedriver 时是否自动下载。",
    )
    webdriver_proxy = _prompt_text(
        "HUNAU_WEBDRIVER_PROXY",
        _env_value(existing, "HUNAU_WEBDRIVER_PROXY", ""),
        hint="浏览器代理地址，可留空。",
        example="http://127.0.0.1:7890",
    )

    _print_section(
        "LLM 与主观题配置",
        "用于自动生成主观题评价意见；未配置 API Key 将自动使用静态文案随机兜底。",
    )

    llm_enabled = _prompt_bool_text(
        "HUNAU_LLM_ENABLED",
        _env_value(existing, "HUNAU_LLM_ENABLED", "true") or "true",
        hint="是否启用 LLM 生成主观题。",
    )
    llm_api_key = _prompt_secret(
        "HUNAU_LLM_API_KEY",
        _env_value(existing, "HUNAU_LLM_API_KEY", ""),
        hint="可留空；留空将走静态文案随机模式。",
    )
    llm_base_url = _prompt_text(
        "HUNAU_LLM_BASE_URL",
        _env_value(existing, "HUNAU_LLM_BASE_URL", "https://api.openai.com/v1")
        or "https://api.openai.com/v1",
        hint="OpenAI 兼容 API 的 base url。",
        example="https://api.openai.com/v1",
    )
    llm_endpoint = _prompt_text(
        "HUNAU_LLM_ENDPOINT",
        _env_value(existing, "HUNAU_LLM_ENDPOINT", ""),
        hint="可留空，程序会自动拼接为 <base_url>/chat/completions。",
    )
    llm_model = _prompt_text(
        "HUNAU_LLM_MODEL",
        _env_value(existing, "HUNAU_LLM_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
        hint="模型名称。",
        example="gpt-4o-mini",
    )
    llm_timeout = _prompt_text(
        "HUNAU_LLM_TIMEOUT",
        _env_value(existing, "HUNAU_LLM_TIMEOUT", "25") or "25",
        hint="LLM 请求超时时间（秒）。",
        example="25",
    )
    llm_temperature = _prompt_text(
        "HUNAU_LLM_TEMPERATURE",
        _env_value(existing, "HUNAU_LLM_TEMPERATURE", "0.7") or "0.7",
        hint="生成随机度，0~2 通常取 0.3~0.9。",
        example="0.7",
    )
    llm_max_tokens = _prompt_text(
        "HUNAU_LLM_MAX_TOKENS",
        _env_value(existing, "HUNAU_LLM_MAX_TOKENS", "180") or "180",
        hint="单次生成最大 token 数。",
        example="180",
    )

    review_style = _prompt_text(
        "HUNAU_REVIEW_STYLE",
        _env_value(existing, "HUNAU_REVIEW_STYLE", "积极向上、真诚、专业")
        or "积极向上、真诚、专业",
        hint="主观题文案整体风格。",
        example="积极向上、真诚、专业",
    )
    review_prompt = _prompt_text(
        "HUNAU_REVIEW_PROMPT",
        _env_value(existing, "HUNAU_REVIEW_PROMPT", DEFAULT_REVIEW_PROMPT)
        or DEFAULT_REVIEW_PROMPT,
        hint="支持占位符：{course_name} {teacher_name} {style}。",
    )
    subjective_max_chars = _prompt_text(
        "HUNAU_SUBJECTIVE_MAX_CHARS",
        _env_value(existing, "HUNAU_SUBJECTIVE_MAX_CHARS", "25") or "25",
        hint="主观题最终字数上限。",
        example="25",
    )

    print()
    print("即将写入配置摘要：")
    print(f"- HUNAU_USERNAME: {username or '(未设置)'}")
    print(f"- HUNAU_PASSWORD: {_mask(password)}")
    print(f"- HUNAU_HEADLESS: {headless or '(自动)'}")
    print(f"- HUNAU_CHROMEDRIVER_PATH: {chromedriver_path or '(从PATH查找)'}")
    print(f"- HUNAU_AUTO_INSTALL_DRIVER: {auto_install_driver}")
    print(f"- HUNAU_WEBDRIVER_PROXY: {webdriver_proxy or '(未设置)'}")
    print(f"- HUNAU_LLM_ENABLED: {llm_enabled}")
    print(f"- HUNAU_LLM_API_KEY: {_mask(llm_api_key)}")
    print(f"- HUNAU_LLM_BASE_URL: {llm_base_url}")
    print(
        f"- HUNAU_LLM_ENDPOINT: "
        f"{llm_endpoint or '(自动拼接为 <base_url>/chat/completions)'}"
    )
    print(f"- HUNAU_LLM_MODEL: {llm_model}")
    print(f"- HUNAU_REVIEW_STYLE: {review_style}")
    print(f"- HUNAU_SUBJECTIVE_MAX_CHARS: {subjective_max_chars}")

    confirm = input("确认写入 .env.local ? [Y/n]: ").strip().lower()
    if confirm in {"n", "no"}:
        print("已取消写入，配置保持不变。")
        return

    lines = [
        "# 湖南农业大学 WebVPN 登录账号",
        "# 请填入你的学号和密码（留空则使用二维码扫码登录）",
        f'HUNAU_USERNAME="{_escape_quoted(username)}"',
        f'HUNAU_PASSWORD="{_escape_quoted(password)}"',
        "",
        "# 浏览器是否无头运行：true / false；留空按环境自动判断",
        f"HUNAU_HEADLESS={headless}",
        "",
        "# chromedriver 本地路径（推荐绝对路径）；留空则从 PATH 查找",
        f"HUNAU_CHROMEDRIVER_PATH={chromedriver_path}",
        "",
        "# 本地无 chromedriver 时是否自动下载：true / false",
        f"HUNAU_AUTO_INSTALL_DRIVER={auto_install_driver}",
        "",
        "# 浏览器代理（可选），例如：http://127.0.0.1:7890",
        f"HUNAU_WEBDRIVER_PROXY={webdriver_proxy}",
        "",
        "# LLM 主观题评价配置（未配置 APIKEY 时自动使用静态评价库随机文案）",
        f"HUNAU_LLM_ENABLED={llm_enabled}",
        f"HUNAU_LLM_API_KEY={llm_api_key}",
        f"HUNAU_LLM_BASE_URL={llm_base_url}",
        f"HUNAU_LLM_ENDPOINT={llm_endpoint}",
        f"HUNAU_LLM_MODEL={llm_model}",
        f"HUNAU_LLM_TIMEOUT={llm_timeout}",
        f"HUNAU_LLM_TEMPERATURE={llm_temperature}",
        f"HUNAU_LLM_MAX_TOKENS={llm_max_tokens}",
        "",
        "# 主观题风格与提示词",
        f"HUNAU_REVIEW_STYLE={review_style}",
        f'HUNAU_REVIEW_PROMPT="{_escape_quoted(review_prompt)}"',
        f"HUNAU_SUBJECTIVE_MAX_CHARS={subjective_max_chars}",
    ]

    ENV_FILE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print(f"配置已写入: {ENV_FILE_PATH}")
    print("你可以运行 `python app.py` 启动自动评价。")


if __name__ == "__main__":
    main()
