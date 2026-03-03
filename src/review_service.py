import json
import random
import re
import urllib.error
import urllib.request

from src.config import Settings


class ReviewService:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def normalize_teacher_name(raw_teacher: str) -> str:
        teacher_text = " ".join((raw_teacher or "").split()).strip()
        if not teacher_text:
            return "任课教师"

        reserved_tokens = {"任课教师", "任课老师", "教师", "老师"}
        if teacher_text in reserved_tokens:
            return "任课教师"

        parts = re.split(r"[、,，;/；&]+|\s+(?:和|与|及)\s+", teacher_text)
        normalized_parts: list[str] = []

        for part in parts:
            current = part.strip()
            if not current:
                continue

            current = re.sub(r"[\(\[（【][^\)\]）】]*[\)\]）】]", "", current).strip()
            current = re.sub(
                r"^(?:编号|工号|学号|ID|No\.?)[\s:：\-_.#]*",
                "",
                current,
                flags=re.I,
            ).strip()
            current = re.sub(
                r"^[\d０-９A-Za-z\-_#\.]+(?=[\u4e00-\u9fff])", "", current
            ).strip()
            current = re.sub(r"^[\d０-９\-_.:：\s]+", "", current).strip()
            current = re.sub(r"^[\-_.:：\s]+|[\-_.:：\s]+$", "", current).strip()
            if not current:
                continue

            if current in reserved_tokens:
                normalized_parts.append("任课教师")
                continue

            if current.endswith(("老师", "教授", "副教授", "讲师", "助教", "导师")):
                normalized_parts.append(current)
            else:
                normalized_parts.append(f"{current}老师")

        if not normalized_parts:
            return "任课教师"

        deduped_parts: list[str] = []
        seen: set[str] = set()
        for item in normalized_parts:
            if item not in seen:
                deduped_parts.append(item)
                seen.add(item)

        if not deduped_parts:
            return "任课教师"
        if len(deduped_parts) == 1 and deduped_parts[0] in reserved_tokens:
            return "任课教师"

        return "、".join(deduped_parts)

    @staticmethod
    def sanitize_text(text: str) -> str:
        return " ".join((text or "").replace("\r", " ").replace("\n", " ").split())

    def fit_review_length(self, course_title: str, teacher_name: str, text: str) -> str:
        cleaned = self.sanitize_text(text)
        if not cleaned:
            cleaned = "教学认真负责，收获很大。"

        max_chars = max(1, self.settings.subjective_review_max_chars)
        if len(cleaned) <= max_chars:
            return cleaned

        teacher = self.normalize_teacher_name(teacher_name)
        course_name = course_title.strip() if course_title.strip() else "本课程"

        compact_templates = [
            f"{teacher}授课认真，收获很大。",
            f"《{course_name}》教学扎实，收获明显。",
            f"{teacher}教学清晰，课堂高效。",
            "教学认真负责，学习收获明显。",
            "课程内容扎实，课堂互动良好。",
        ]
        for candidate in compact_templates:
            normalized_candidate = self.sanitize_text(candidate)
            if len(normalized_candidate) <= max_chars:
                return normalized_candidate

        return cleaned[:max_chars]

    def build_review_prompt(self, course_title: str, teacher_name: str) -> str:
        course_name = course_title.strip() if course_title.strip() else "本课程"
        teacher = self.normalize_teacher_name(teacher_name)

        try:
            prompt = self.settings.review_prompt.format(
                course_name=course_name,
                teacher_name=teacher,
                style=self.settings.review_style,
            )
        except Exception:
            prompt = (
                f"请为《{course_name}》课程的教师{teacher}写一段{self.settings.review_style}的课程评价意见，"
                "中文，不分点，15到25字。"
            )
        return self.sanitize_text(prompt)

    def request_llm_review(self, prompt: str) -> str:
        if not self.settings.llm_enabled:
            return ""
        if not self.settings.llm_api_key:
            return ""
        if not self.settings.llm_model:
            return ""
        if not self.settings.llm_endpoint:
            return ""

        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是高校课程评价助手，只输出一段中文评价，不要分点，语气积极正面。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.settings.llm_temperature,
            "max_tokens": self.settings.llm_max_tokens,
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.llm_api_key}",
        }
        request = urllib.request.Request(
            self.settings.llm_endpoint,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request, timeout=self.settings.llm_timeout
            ) as response:
                raw_text = response.read().decode("utf-8", errors="ignore")
            parsed = json.loads(raw_text)
            choices = parsed.get("choices", [])
            if not choices:
                return ""

            choice = choices[0]
            message = choice.get("message")
            if isinstance(message, dict):
                content = message.get("content", "")
                if isinstance(content, list):
                    chunks: list[str] = []
                    for part in content:
                        if isinstance(part, dict):
                            text_part = str(part.get("text", "")).strip()
                            if text_part:
                                chunks.append(text_part)
                    return self.sanitize_text(" ".join(chunks))
                return self.sanitize_text(str(content))

            return self.sanitize_text(str(choice.get("text", "")))
        except urllib.error.HTTPError as error:
            print(f"[WARN] LLM HTTP 错误: {error.code}")
        except Exception as error:
            print(f"[WARN] LLM 请求失败: {error}")
        return ""

    def generate_static_review(self, course_title: str, teacher_name: str) -> str:
        course_name = course_title.strip() if course_title.strip() else "本课程"
        teacher = self.normalize_teacher_name(teacher_name)

        template = random.choice(self.settings.static_review_library)
        try:
            content = template.format(course_name=course_name, teacher_name=teacher)
        except Exception:
            content = f"《{course_name}》教学扎实，{teacher}授课认真，收获明显。"
        return self.sanitize_text(content)

    def generate_review_text(self, course_title: str, teacher_name: str) -> str:
        prompt = self.build_review_prompt(course_title, teacher_name)
        llm_result = self.request_llm_review(prompt)
        if llm_result:
            return self.fit_review_length(course_title, teacher_name, llm_result)

        static_result = self.generate_static_review(course_title, teacher_name)
        return self.fit_review_length(course_title, teacher_name, static_result)
