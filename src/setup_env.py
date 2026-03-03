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


def _prompt_text(label: str, default: str = "", required: bool = False) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        raw = input(f"{label}{suffix}: ").strip()
        if raw:
            return raw
        if default != "":
            return default
        if not required:
            return ""
        print("该项不能为空，请重新输入")


def _prompt_secret(label: str, default: str = "") -> str:
    hint = " [已设置，直接回车保持]" if default else ""
    raw = getpass(f"{label}{hint}: ").strip()
    if raw:
        return raw
    return default


def _prompt_bool_text(label: str, default: str) -> str:
    normalized_default = default.strip().lower() if default else ""
    while True:
        suffix = f" [{normalized_default}]" if normalized_default else " [true/false]"
        raw = input(f"{label}{suffix}: ").strip().lower()
        if not raw and normalized_default:
            return normalized_default
        if raw in {"true", "false"}:
            return raw
        print("请输入 true 或 false")


def _prompt_headless(default: str) -> str:
    normalized_default = default.strip().lower() if default else ""
    while True:
        suffix = (
            f" [{normalized_default}]"
            if normalized_default
            else " [留空自动/true/false]"
        )
        raw = input(f"HUNAU_HEADLESS{suffix}: ").strip().lower()
        if not raw:
            return normalized_default
        if raw in {"true", "false"}:
            return raw
        print("请输入 true、false 或直接回车")


def main():
    existing = dotenv_values(ENV_FILE_PATH)

    print("开始交互配置 .env.local")
    print("直接回车将保留默认值")
    print()

    username = _prompt_text(
        "HUNAU_USERNAME", _env_value(existing, "HUNAU_USERNAME", "")
    )
    password = _prompt_secret(
        "HUNAU_PASSWORD", _env_value(existing, "HUNAU_PASSWORD", "")
    )

    headless = _prompt_headless(_env_value(existing, "HUNAU_HEADLESS", ""))
    chromedriver_path = _prompt_text(
        "HUNAU_CHROMEDRIVER_PATH",
        _env_value(existing, "HUNAU_CHROMEDRIVER_PATH", ""),
    )
    auto_install_driver = _prompt_bool_text(
        "HUNAU_AUTO_INSTALL_DRIVER",
        _env_value(existing, "HUNAU_AUTO_INSTALL_DRIVER", "true") or "true",
    )
    webdriver_proxy = _prompt_text(
        "HUNAU_WEBDRIVER_PROXY",
        _env_value(existing, "HUNAU_WEBDRIVER_PROXY", ""),
    )

    llm_enabled = _prompt_bool_text(
        "HUNAU_LLM_ENABLED",
        _env_value(existing, "HUNAU_LLM_ENABLED", "true") or "true",
    )
    llm_api_key = _prompt_secret(
        "HUNAU_LLM_API_KEY", _env_value(existing, "HUNAU_LLM_API_KEY", "")
    )
    llm_base_url = _prompt_text(
        "HUNAU_LLM_BASE_URL",
        _env_value(existing, "HUNAU_LLM_BASE_URL", "https://api.openai.com/v1")
        or "https://api.openai.com/v1",
    )
    llm_endpoint = _prompt_text(
        "HUNAU_LLM_ENDPOINT", _env_value(existing, "HUNAU_LLM_ENDPOINT", "")
    )
    llm_model = _prompt_text(
        "HUNAU_LLM_MODEL",
        _env_value(existing, "HUNAU_LLM_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
    )
    llm_timeout = _prompt_text(
        "HUNAU_LLM_TIMEOUT",
        _env_value(existing, "HUNAU_LLM_TIMEOUT", "25") or "25",
    )
    llm_temperature = _prompt_text(
        "HUNAU_LLM_TEMPERATURE",
        _env_value(existing, "HUNAU_LLM_TEMPERATURE", "0.7") or "0.7",
    )
    llm_max_tokens = _prompt_text(
        "HUNAU_LLM_MAX_TOKENS",
        _env_value(existing, "HUNAU_LLM_MAX_TOKENS", "180") or "180",
    )

    review_style = _prompt_text(
        "HUNAU_REVIEW_STYLE",
        _env_value(existing, "HUNAU_REVIEW_STYLE", "积极向上、真诚、专业")
        or "积极向上、真诚、专业",
    )
    review_prompt = _prompt_text(
        "HUNAU_REVIEW_PROMPT",
        _env_value(existing, "HUNAU_REVIEW_PROMPT", DEFAULT_REVIEW_PROMPT)
        or DEFAULT_REVIEW_PROMPT,
    )
    subjective_max_chars = _prompt_text(
        "HUNAU_SUBJECTIVE_MAX_CHARS",
        _env_value(existing, "HUNAU_SUBJECTIVE_MAX_CHARS", "25") or "25",
    )

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


if __name__ == "__main__":
    main()
