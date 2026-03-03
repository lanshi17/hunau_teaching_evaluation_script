# 湖南农业大学教学评价自动化

基于 `feapder + Selenium` 的教学评价自动化脚本，支持：

- 账号密码登录 / 二维码登录
- 课程列表循环评价（自动跳过已完成）
- 16道客观题自动选择“优”
- 主观题自动填写（`LLM` 或静态文案随机）
- 主观题字数限制（默认 `<=25` 字）

## 工程结构

```text
.
├─ src/
│  ├─ main.py            # 入口
│  ├─ spider.py          # 核心自动化流程
│  ├─ review_service.py  # 主观题文案生成与清洗
│  ├─ config.py          # 环境变量读取与设置
│  ├─ constants.py       # URL / XPath / 固定常量
│  └─ setup_env.py       # 交互式环境变量配置
├─ app.py                # 根入口包装（调用 src.main）
├─ setup_env.py          # 根CLI包装（调用 src.setup_env）
├─ .env.local            # 本地配置（已被 .gitignore 忽略）
└─ pyproject.toml
```

## 安装

```bash
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install "feapder[render]" python-dotenv setuptools
```

## 配置方式

### 方式1：交互式配置（推荐）

```bash
.venv/bin/python setup_env.py
```

会交互填写并生成 `.env.local`。

### 方式2：手动编辑 `.env.local`

先复制示例文件：

```bash
cp .env.example .env.local
```

关键字段：

- 登录
  - `HUNAU_USERNAME`
  - `HUNAU_PASSWORD`
  - 留空时走二维码登录
- 驱动
  - `HUNAU_CHROMEDRIVER_PATH`
  - `HUNAU_AUTO_INSTALL_DRIVER=true/false`
  - `HUNAU_HEADLESS=true/false`（留空自动）
- 主观题文案
  - `HUNAU_LLM_ENABLED=true/false`
  - `HUNAU_LLM_API_KEY`
  - `HUNAU_LLM_BASE_URL`
  - `HUNAU_LLM_ENDPOINT`（留空自动拼接）
  - `HUNAU_LLM_MODEL`
  - `HUNAU_REVIEW_STYLE`
  - `HUNAU_REVIEW_PROMPT`
  - `HUNAU_SUBJECTIVE_MAX_CHARS`（默认 `25`）

如果需要使用 `apikey` 来调用大模型，可以使用 `https://linxi.chat`，并参考 `https://linxi.apifox.cn/` 文档进行配置。

## 运行

```bash
.venv/bin/python app.py
```

或：

```bash
.venv/bin/python src/main.py
```

## 评价流程

1. 登录系统（账号密码或扫码）
2. 进入 `教学管理` -> `课程教学评价`
3. 获取课程列表并筛选可评价课程
4. 进入课程评价页
5. 客观题自动选“优”
6. 主观题填写
   - 优先调用 LLM
   - LLM 未配置或失败时，从静态评价库随机选择
   - 最终文本强制限制为 `<=25` 字
7. 提交并返回列表，继续下一门直到结束

## 注意事项

- `.env.local` 含敏感信息，已在 `.gitignore` 中忽略。
- 无图形界面且未配置账号密码时，二维码登录不可用。
- 如遇到课程状态刷新延迟，脚本有去重与停止重复机制，避免同一课程反复提交。
