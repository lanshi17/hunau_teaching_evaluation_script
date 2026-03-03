import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from src.constants import DEFAULT_REVIEW_PROMPT, DEFAULT_STATIC_REVIEW_LIBRARY

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env.local"
_ = load_dotenv(ENV_FILE_PATH)


def read_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized == "":
        return default
    return normalized in {"1", "true", "yes", "on"}


def read_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value.strip())
    except Exception:
        return default


def read_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value.strip())
    except Exception:
        return default


@dataclass(frozen=True)
class Settings:
    username: str
    password: str
    headless: bool
    chromedriver_path: str
    chromedriver_bin: str
    auto_install_driver: bool
    webdriver_proxy: str
    llm_enabled: bool
    llm_api_key: str
    llm_base_url: str
    llm_endpoint: str
    llm_model: str
    llm_timeout: int
    llm_temperature: float
    llm_max_tokens: int
    review_style: str
    review_prompt: str
    subjective_review_max_chars: int
    static_review_library: tuple[str, ...]


def load_settings() -> Settings:
    username = os.getenv("HUNAU_USERNAME", "").strip()
    password = os.getenv("HUNAU_PASSWORD", "").strip()

    has_display = bool(os.getenv("DISPLAY"))
    headless = read_bool_env("HUNAU_HEADLESS", default=not has_display)

    chromedriver_path = os.getenv("HUNAU_CHROMEDRIVER_PATH", "").strip()
    chromedriver_bin = ""
    if chromedriver_path:
        expanded_driver_path = os.path.expanduser(chromedriver_path)
        if os.path.isfile(expanded_driver_path):
            chromedriver_bin = expanded_driver_path
        else:
            chromedriver_bin = shutil.which(expanded_driver_path) or ""
    else:
        chromedriver_bin = shutil.which("chromedriver") or ""

    auto_install_driver = read_bool_env(
        "HUNAU_AUTO_INSTALL_DRIVER", default=not bool(chromedriver_bin)
    )
    webdriver_proxy = os.getenv("HUNAU_WEBDRIVER_PROXY", "").strip()

    llm_enabled = read_bool_env("HUNAU_LLM_ENABLED", default=True)
    llm_api_key = os.getenv("HUNAU_LLM_API_KEY", "").strip()
    llm_base_url = (
        os.getenv("HUNAU_LLM_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
    )
    raw_llm_endpoint = os.getenv("HUNAU_LLM_ENDPOINT", "").strip()
    llm_endpoint = (
        raw_llm_endpoint if raw_llm_endpoint else f"{llm_base_url}/chat/completions"
    )
    llm_model = os.getenv("HUNAU_LLM_MODEL", "gpt-4o-mini").strip()
    llm_timeout = read_int_env("HUNAU_LLM_TIMEOUT", 25)
    llm_temperature = read_float_env("HUNAU_LLM_TEMPERATURE", 0.7)
    llm_max_tokens = read_int_env("HUNAU_LLM_MAX_TOKENS", 180)

    review_style = os.getenv("HUNAU_REVIEW_STYLE", "积极向上、真诚、专业").strip()
    review_prompt = os.getenv("HUNAU_REVIEW_PROMPT", DEFAULT_REVIEW_PROMPT).strip()
    subjective_review_max_chars = read_int_env("HUNAU_SUBJECTIVE_MAX_CHARS", 25)

    return Settings(
        username=username,
        password=password,
        headless=headless,
        chromedriver_path=chromedriver_path,
        chromedriver_bin=chromedriver_bin,
        auto_install_driver=auto_install_driver,
        webdriver_proxy=webdriver_proxy,
        llm_enabled=llm_enabled,
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
        llm_endpoint=llm_endpoint,
        llm_model=llm_model,
        llm_timeout=llm_timeout,
        llm_temperature=llm_temperature,
        llm_max_tokens=llm_max_tokens,
        review_style=review_style,
        review_prompt=review_prompt,
        subjective_review_max_chars=subjective_review_max_chars,
        static_review_library=DEFAULT_STATIC_REVIEW_LIBRARY,
    )
