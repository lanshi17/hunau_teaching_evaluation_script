import time
from urllib.parse import urlparse

import feapder
from feapder.utils.webdriver import SeleniumDriver
from selenium.webdriver.remote.webelement import WebElement

from src.config import load_settings
from src.constants import (
    ACTION_NEGATIVE_CLASS_MARKERS,
    ACTION_NEGATIVE_TEXT_MARKERS,
    ACTION_POSITIVE_ATTR_MARKERS,
    ACTION_POSITIVE_CLASS_MARKERS,
    ACTION_POSITIVE_TEXT_MARKERS,
    BACK_XPATH,
    CONFIRM_XPATH,
    COURSE_ACTION_BY_ROW_INDEX_XPATH,
    COURSE_ACTION_IN_ROW_XPATH,
    COURSE_ACTION_LINKS_XPATH,
    COURSE_EVAL_MENU_XPATH,
    COURSE_LIST_CONTAINER_XPATH,
    COURSE_LIST_ROWS_XPATH,
    COURSE_LIST_TABLE_XPATH,
    COURSE_NAME_IN_ROW_XPATHS,
    COURSE_TEACHER_IN_ROW_XPATHS,
    EVAL_EXCELLENT_IN_ROW_XPATHS,
    EVAL_FIRST_OPTION_XPATH,
    EVAL_ROWS_XPATH,
    EVAL_SUBJECTIVE_INPUT_XPATH,
    EVAL_SUBJECTIVE_ROW_XPATH,
    INDEX_URL,
    LOGIN_ACCOUNT_TAB_XPATHS,
    LOGIN_BUTTON_XPATHS,
    LOGIN_PASSWORD_XPATHS,
    LOGIN_URL,
    LOGIN_USERNAME_XPATHS,
    QR_CODE_XPATHS,
    QUESTION_COUNT,
    RADIO_ID_TEMPLATE,
    SUBMIT_XPATH,
    TEACHING_MANAGEMENT_XPATH,
)
from src.review_service import ReviewService

SETTINGS = load_settings()
REVIEW_SERVICE = ReviewService(SETTINGS)


class TeachingEvalSpider(feapder.AirSpider):
    __custom_setting__: dict[str, object] = dict(
        RENDER_DOWNLOADER="feapder.network.downloader.SeleniumDownloader",
        SPIDER_MAX_RETRY_TIMES=1,
        WEBDRIVER=dict(
            pool_size=1,
            load_images=True,
            proxy=SETTINGS.webdriver_proxy or None,
            headless=SETTINGS.headless,
            driver_type="CHROME",
            timeout=30,
            window_size=(1280, 900),
            custom_argument=[
                "--ignore-certificate-errors",
                "--disable-blink-features=AutomationControlled",
            ],
            executable_path=SETTINGS.chromedriver_bin or None,
            auto_install_driver=SETTINGS.auto_install_driver,
            use_stealth_js=True,
        ),
    )

    def distribute_task(self):
        request = feapder.Request(LOGIN_URL, render=True, parser_name=self.name)
        self._request_buffer.put_request(request, ignore_max_size=False)

    @staticmethod
    def wait_any_xpath(browser: SeleniumDriver, xpaths: list[str], timeout: int = 15):
        end_time = time.time() + timeout
        last_error = None
        while time.time() < end_time:
            try:
                browser.switch_to.default_content()
                frames = browser.find_elements("tag name", "iframe")
            except Exception as error:
                last_error = error
                frames = []

            contexts: list[WebElement | None] = [None]
            contexts.extend(frames)

            for context in contexts:
                try:
                    browser.switch_to.default_content()
                    if context is not None:
                        browser.switch_to.frame(context)
                except Exception as error:
                    last_error = error
                    continue

                for xpath in xpaths:
                    try:
                        element = browser.find_element("xpath", xpath)
                        if element.is_displayed():
                            return element
                    except Exception as error:
                        last_error = error
                        continue

            time.sleep(0.4)

        raise TimeoutError(f"等待元素超时: {xpaths}; last_error={last_error}")

    @classmethod
    def wait_xpath(cls, browser: SeleniumDriver, xpath: str, timeout: int = 15):
        return cls.wait_any_xpath(browser, [xpath], timeout=timeout)

    @classmethod
    def wait_xpath_candidates(
        cls, browser: SeleniumDriver, xpaths: list[str], timeout: int = 15
    ):
        return cls.wait_any_xpath(browser, xpaths, timeout=timeout)

    @staticmethod
    def find_elements_any_xpath(browser: SeleniumDriver, xpath: str):
        elements: list[WebElement] = []
        try:
            browser.switch_to.default_content()
            frames = browser.find_elements("tag name", "iframe")
        except Exception:
            frames = []

        contexts: list[WebElement | None] = [None]
        contexts.extend(frames)

        for context in contexts:
            try:
                browser.switch_to.default_content()
                if context is not None:
                    browser.switch_to.frame(context)
                current_elements = browser.find_elements("xpath", xpath)
                visible_elements = [
                    element
                    for element in current_elements
                    if getattr(element, "is_displayed", lambda: True)()
                ]
                if visible_elements:
                    return visible_elements
                if current_elements:
                    elements = current_elements
            except Exception:
                continue

        return elements

    @classmethod
    def input_xpath(
        cls, browser: SeleniumDriver, xpath: str, value: str, timeout: int = 15
    ):
        element = cls.wait_xpath(browser, xpath, timeout=timeout)
        element.clear()
        element.send_keys(value)

    @classmethod
    def input_xpath_candidates(
        cls, browser: SeleniumDriver, xpaths: list[str], value: str, timeout: int = 15
    ):
        element = cls.wait_xpath_candidates(browser, xpaths, timeout=timeout)
        element.clear()
        element.send_keys(value)

    @classmethod
    def click_xpath(cls, browser: SeleniumDriver, xpath: str, timeout: int = 15):
        element = cls.wait_xpath(browser, xpath, timeout=timeout)
        element.click()

    @classmethod
    def click_xpath_candidates(
        cls, browser: SeleniumDriver, xpaths: list[str], timeout: int = 15
    ):
        element = cls.wait_xpath_candidates(browser, xpaths, timeout=timeout)
        element.click()

    @staticmethod
    def wait_login_success(browser: SeleniumDriver, timeout: int):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if "cas/login" not in browser.current_url:
                return True
            time.sleep(1)
        return False

    @staticmethod
    def parse_row_index(row: WebElement) -> int:
        row_id = (row.get_attribute("id") or "").strip()
        prefix = "datagrid-row-r1-2-"
        if row_id.startswith(prefix):
            tail = row_id[len(prefix) :]
            if tail.isdigit():
                return int(tail)

        for attr_name in ("data-row-index", "data-index", "row-index"):
            attr_value = (row.get_attribute(attr_name) or "").strip()
            if attr_value.isdigit():
                return int(attr_value)

        return -1

    @staticmethod
    def read_course_title(row: WebElement, position: int) -> str:
        for xpath in COURSE_NAME_IN_ROW_XPATHS:
            try:
                name_node = row.find_element("xpath", xpath)
                name_text = (name_node.text or "").strip()
                if name_text:
                    return name_text
            except Exception:
                continue

        row_text = (row.text or "").strip()
        if row_text:
            first_line = row_text.splitlines()[0].strip()
            if first_line:
                return first_line
        return f"course-{position}"

    @staticmethod
    def read_teacher_name(row: WebElement) -> str:
        for xpath in COURSE_TEACHER_IN_ROW_XPATHS:
            try:
                teacher_node = row.find_element("xpath", xpath)
                teacher_text = (teacher_node.text or "").strip()
                if teacher_text:
                    return teacher_text
            except Exception:
                continue
        return "任课教师"

    @staticmethod
    def normalize_action_text(element: WebElement) -> str:
        text = (element.text or "").strip()
        title = (element.get_attribute("title") or "").strip()
        aria_label = (element.get_attribute("aria-label") or "").strip()
        alt_text = (element.get_attribute("alt") or "").strip()
        chunks = [chunk for chunk in [text, title, aria_label, alt_text] if chunk]
        return " ".join(chunks).strip()

    @classmethod
    def classify_action_element(cls, element: WebElement) -> tuple[bool, int, str, str]:
        try:
            if not getattr(element, "is_displayed", lambda: True)():
                return False, -1, "", ""
        except Exception:
            return False, -1, "", ""

        classes = (element.get_attribute("class") or "").lower()
        aria_disabled = (element.get_attribute("aria-disabled") or "").lower()
        disabled_attr = (element.get_attribute("disabled") or "").lower()
        if (
            "disabled" in classes
            or aria_disabled in {"true", "1"}
            or disabled_attr in {"true", "1", "disabled"}
        ):
            return False, -1, "", ""

        label = cls.normalize_action_text(element)
        label_lower = label.lower()
        href = (element.get_attribute("href") or "").strip()
        href_lower = href.lower()
        onclick = (element.get_attribute("onclick") or "").strip()
        onclick_lower = onclick.lower()

        positive_text = any(
            marker in label for marker in ACTION_POSITIVE_TEXT_MARKERS
        ) or any(marker in label_lower for marker in ACTION_POSITIVE_TEXT_MARKERS)
        negative_text = any(marker in label for marker in ACTION_NEGATIVE_TEXT_MARKERS)

        positive_class = any(
            marker in classes for marker in ACTION_POSITIVE_CLASS_MARKERS
        )
        negative_class = any(
            marker in classes for marker in ACTION_NEGATIVE_CLASS_MARKERS
        )

        href_positive = any(
            marker in href_lower for marker in ACTION_POSITIVE_ATTR_MARKERS
        )
        onclick_positive = any(
            marker in onclick_lower for marker in ACTION_POSITIVE_ATTR_MARKERS
        )

        if negative_text or negative_class:
            return False, -1, "", ""

        actionable = (
            positive_text or positive_class or href_positive or onclick_positive
        )
        if not actionable:
            return False, -1, "", ""

        score = 0
        if positive_text:
            score += 3
        if href_positive:
            score += 2
        if onclick_positive:
            score += 2
        if positive_class:
            score += 1
        if not label:
            score += 1

        return True, score, href, label

    @classmethod
    def pick_best_action_element(
        cls, elements: list[WebElement]
    ) -> tuple[WebElement | None, str, str]:
        best_element: WebElement | None = None
        best_href = ""
        best_label = ""
        best_score = -1

        for element in elements:
            actionable, score, href, label = cls.classify_action_element(element)
            if not actionable:
                continue
            if score > best_score:
                best_element = element
                best_href = href
                best_label = label
                best_score = score

        return best_element, best_href, best_label

    @classmethod
    def collect_course_status(
        cls, browser: SeleniumDriver
    ) -> tuple[list[dict[str, str | int | bool]], list[dict[str, str | int | bool]]]:
        cls.wait_xpath(browser, COURSE_LIST_CONTAINER_XPATH, timeout=20)
        rows = cls.find_elements_any_xpath(browser, COURSE_LIST_ROWS_XPATH)

        all_courses: list[dict[str, str | int | bool]] = []
        pending_courses: list[dict[str, str | int | bool]] = []

        for position, row in enumerate(rows, start=1):
            row_index = cls.parse_row_index(row)
            title = cls.read_course_title(row, position)
            teacher_name = cls.read_teacher_name(row)

            if (row_index == -1 and position == 1) or title in {
                "课程名称",
                "序号",
                "操作",
            }:
                continue

            # 更新判断逻辑：检查操作列中的内容来确定是否可以评价
            try:
                # 获取操作列元素
                action_td = row.find_element("xpath", "./td[10]")
                
                # 检查是否有链接或按钮
                links = action_td.find_elements("xpath", ".//a | .//button | .//*[@role='button' or @role='link']")
                
                # 检查文本内容以判断状态
                action_text = action_td.text.lower() if action_td.text else ""
                
                # 判断是否可以评价的逻辑
                can_evaluate = False
                
                if links:
                    # 如果有链接，检查每个链接的文字内容和类名
                    for link in links:
                        link_text = link.text.lower() if link.text else ""
                        link_classes = (link.get_attribute("class") or "").lower()
                        
                        # 检查链接内的子元素的类名（如图标）
                        child_spans = link.find_elements("tag name", "span")
                        child_icons = []
                        for span in child_spans:
                            span_class = span.get_attribute("class")
                            if span_class:
                                child_icons.append(span_class.lower())
                        
                        # 检查链接文本、类名和子元素类名是否包含负面关键词
                        is_negative_text = any(marker in link_text for marker in ACTION_NEGATIVE_TEXT_MARKERS)
                        is_negative_class = any(marker in link_classes for marker in ACTION_NEGATIVE_CLASS_MARKERS)
                        is_negative_icon = any("icon-finish" in icon_class for icon_class in child_icons)
                        
                        if is_negative_text or is_negative_class or is_negative_icon:
                            # 如果是负面状态（已评价、已完成等），不能评价
                            can_evaluate = False
                            break
                        else:
                            # 检查是否包含正面关键词（如"评价"、"评教"等）或正面图标
                            is_positive_text = any(marker in link_text for marker in ACTION_POSITIVE_TEXT_MARKERS)
                            is_positive_class = any(marker in link_classes for marker in ACTION_POSITIVE_CLASS_MARKERS)
                            is_positive_icon = any("icon-edit" in icon_class for icon_class in child_icons)
                            
                            if is_positive_text or is_positive_class or is_positive_icon:
                                # 如果是正面状态（评价、评教等），可以评价
                                can_evaluate = True
                                break
                else:
                    # 如果没有链接，检查单元格本身的内容
                    # 如果单元格内没有任何链接，检查是否包含负面关键词
                    is_negative_td = any(marker in action_text for marker in ACTION_NEGATIVE_TEXT_MARKERS)
                    
                    if is_negative_td or not action_text.strip():
                        # 单元格为空或包含负面关键词（如"未开放"），不能评价
                        can_evaluate = False
                    else:
                        # 单元格有内容但不包含负面关键词，暂时认为不能评价（因为没有可点击元素）
                        can_evaluate = False
                        
            except Exception:
                # 如果无法获取操作列，尝试使用旧逻辑
                links = row.find_elements("xpath", COURSE_ACTION_IN_ROW_XPATH)
                best_link, href, _ = cls.pick_best_action_element(links)
                can_evaluate = best_link is not None

            course = {
                "position": position,
                "row_index": row_index,
                "title": title,
                "teacher_name": teacher_name,
                "can_evaluate": can_evaluate,
                "href": "" if "href" not in locals() else href,
            }
            all_courses.append(course)
            if can_evaluate:
                pending_courses.append(course)

        return all_courses, pending_courses

    @staticmethod
    def course_key(entry: dict[str, str | int | bool]) -> str:
        row_index = int(entry.get("row_index", -1))
        position = int(entry.get("position", -1))
        title = str(entry.get("title", "")).strip()
        href = str(entry.get("href", "")).strip()
        index_part = row_index if row_index >= 0 else position
        identity = href if href else title
        return f"{index_part}-{identity}"

    @classmethod
    def click_element_safe(cls, element: WebElement, browser: SeleniumDriver):
        try:
            element.click()
        except Exception:
            browser.execute_script("arguments[0].click();", element)

    @classmethod
    def choose_excellent_for_row(cls, row: WebElement, browser: SeleniumDriver) -> bool:
        for xpath in EVAL_EXCELLENT_IN_ROW_XPATHS:
            try:
                candidates = row.find_elements("xpath", xpath)
            except Exception:
                candidates = []

            for candidate in candidates:
                try:
                    cls.click_element_safe(candidate, browser)
                    return True
                except Exception:
                    continue

        return False

    @classmethod
    def fill_subjective_review(
        cls,
        browser: SeleniumDriver,
        course_title: str,
        teacher_name: str,
    ) -> bool:
        review_text = REVIEW_SERVICE.generate_review_text(course_title, teacher_name)
        if not review_text:
            return False

        try:
            cls.wait_xpath(browser, EVAL_SUBJECTIVE_ROW_XPATH, timeout=10)
        except Exception:
            pass

        try:
            textbox = cls.wait_xpath(browser, EVAL_SUBJECTIVE_INPUT_XPATH, timeout=10)
            textbox.clear()
            textbox.send_keys(review_text)
            print(f"[INFO] 主观题已填写({len(review_text)}字): {review_text}")
            return True
        except Exception:
            pass

        try:
            done = browser.execute_script(
                "var e=document.getElementById('txt017');"
                "if(!e){return false;}"
                "e.value=arguments[0];"
                "if(window.jQuery){window.jQuery(e).val(arguments[0]).trigger('input').trigger('change');}"
                "return true;",
                review_text,
            )
            if bool(done):
                print(f"[INFO] 主观题已填写({len(review_text)}字): {review_text}")
                return True
        except Exception as error:
            print(f"[WARN] 主观题填写失败: {error}")

        return False

    @classmethod
    def evaluate_current_course(
        cls,
        browser: SeleniumDriver,
        course_title: str,
        teacher_name: str,
    ) -> tuple[bool, int]:
        cls.wait_xpath(browser, EVAL_FIRST_OPTION_XPATH, timeout=20)
        rows = cls.find_elements_any_xpath(browser, EVAL_ROWS_XPATH)

        selected_count = 0
        for row in rows:
            if cls.choose_excellent_for_row(row, browser):
                selected_count += 1

        if selected_count == 0:
            for question_index in range(1, QUESTION_COUNT + 1):
                radio_id = RADIO_ID_TEMPLATE.format(question_index)
                radio_xpath = f"//*[@id='{radio_id}']"
                try:
                    cls.click_xpath(browser, radio_xpath, timeout=2)
                    selected_count += 1
                except Exception:
                    continue

        if selected_count == 0:
            return False, 0

        subjective_ok = cls.fill_subjective_review(browser, course_title, teacher_name)
        if not subjective_ok:
            print("[WARN] 主观题未能成功填写")
            return False, selected_count

        print(f"[INFO] 课程 {course_title} 已选择评价项: {selected_count}")
        return True, selected_count

    @classmethod
    def submit_and_back(cls, browser: SeleniumDriver):
        cls.click_xpath(browser, SUBMIT_XPATH, timeout=12)
        time.sleep(1)

        try:
            cls.click_xpath(browser, CONFIRM_XPATH, timeout=8)
            time.sleep(1)
        except Exception:
            pass

        try:
            cls.click_xpath(browser, BACK_XPATH, timeout=12)
            time.sleep(2)
        except Exception:
            browser.back()
            time.sleep(2)

    @classmethod
    def open_course_eval_page(
        cls,
        browser: SeleniumDriver,
        entry: dict[str, str | int | bool],
    ):
        row_index = int(entry.get("row_index", -1))
        position = int(entry.get("position", 1))

        if row_index >= 0:
            row_index_xpath = COURSE_ACTION_BY_ROW_INDEX_XPATH.format(index=row_index)
            try:
                cls.click_xpath(browser, row_index_xpath, timeout=20)
                time.sleep(2)
                return
            except Exception:
                pass

        row_xpath = f"({COURSE_LIST_ROWS_XPATH})[{position}]"
        try:
            row = cls.wait_xpath(browser, row_xpath, timeout=15)
            action_links = row.find_elements("xpath", COURSE_ACTION_IN_ROW_XPATH)
            best_link, _, _ = cls.pick_best_action_element(action_links)
            if best_link is not None:
                cls.click_element_safe(best_link, browser)
                time.sleep(2)
                return
        except Exception:
            pass

        indexed_xpath = f"({COURSE_ACTION_LINKS_XPATH})[{position}]"
        try:
            cls.click_xpath(browser, indexed_xpath, timeout=20)
            time.sleep(2)
            return
        except Exception as click_error:
            href = str(entry.get("href", "")).strip()
            parsed = urlparse(href)
            if (
                parsed.scheme in {"http", "https"}
                and parsed.netloc
                and "webvpn.hunau.edu.cn" in parsed.netloc
            ):
                browser.get(href)
                time.sleep(2)
                return

            raise RuntimeError(
                f"打开课程页面失败 position={position} row_index={row_index} href={href} error={click_error}"
            )

    def login(self, browser: SeleniumDriver):
        if SETTINGS.username and SETTINGS.password:
            print("[INFO] 使用账号密码登录...")
            try:
                self.click_xpath_candidates(
                    browser, LOGIN_ACCOUNT_TAB_XPATHS, timeout=5
                )
                time.sleep(0.6)
            except Exception:
                pass

            self.input_xpath_candidates(
                browser, LOGIN_USERNAME_XPATHS, SETTINGS.username, timeout=20
            )
            self.input_xpath_candidates(
                browser, LOGIN_PASSWORD_XPATHS, SETTINGS.password, timeout=20
            )
            self.click_xpath_candidates(browser, LOGIN_BUTTON_XPATHS, timeout=20)
            if not self.wait_login_success(browser, timeout=30):
                raise RuntimeError("账号密码登录超时，仍停留在登录页")
            print("[INFO] 登录成功")
            time.sleep(2)
            return

        print("[INFO] 使用二维码扫码登录")
        print("[INFO] 请用手机扫描浏览器中的二维码...")
        self.wait_xpath_candidates(browser, QR_CODE_XPATHS, timeout=20)
        print("[INFO] 等待扫码（120 秒超时）...")
        if not self.wait_login_success(browser, timeout=120):
            raise RuntimeError("扫码登录超时，请重新运行")
        print("[INFO] 扫码登录成功")
        time.sleep(2)

    def open_course_list(self, browser: SeleniumDriver):
        last_error = None
        for attempt in range(1, 4):
            try:
                browser.get(INDEX_URL)
                time.sleep(2)

                self.click_xpath(browser, TEACHING_MANAGEMENT_XPATH, timeout=15)
                time.sleep(1)

                submenu_error = None
                for _ in range(2):
                    try:
                        self.click_xpath(browser, COURSE_EVAL_MENU_XPATH, timeout=20)
                        time.sleep(2)

                        try:
                            self.wait_xpath(browser, COURSE_LIST_TABLE_XPATH, timeout=8)
                            return
                        except Exception:
                            pass

                        rows = self.find_elements_any_xpath(
                            browser, COURSE_LIST_ROWS_XPATH
                        )
                        if rows:
                            return

                        links = self.find_elements_any_xpath(
                            browser, COURSE_ACTION_LINKS_XPATH
                        )
                        if links:
                            return

                        raise RuntimeError("课程教学评价页面未加载完成")
                    except Exception as error:
                        submenu_error = error
                        time.sleep(1)
                        try:
                            self.click_xpath(
                                browser, TEACHING_MANAGEMENT_XPATH, timeout=8
                            )
                            time.sleep(0.8)
                        except Exception:
                            pass

                raise RuntimeError(f"点击课程教学评价失败: {submenu_error}")
            except Exception as error:
                last_error = error
                print(f"[WARN] 进入课程教学评价失败，第 {attempt} 次重试: {error}")
                time.sleep(1)

        raise RuntimeError(f"无法进入课程教学评价页面: {last_error}")

    def parse(self, request, response):
        browser = response.browser
        if not isinstance(browser, SeleniumDriver):
            raise RuntimeError("渲染浏览器初始化失败")

        self.login(browser)
        self.open_course_list(browser)
        submitted_count = 0
        failed_course_keys: set[str] = set()
        submitted_course_keys: set[str] = set()
        unchanged_pending_rounds = 0
        last_pending_signature = ""

        while True:
            try:
                all_courses, pending_courses = self.collect_course_status(browser)
            except Exception:
                self.open_course_list(browser)
                all_courses, pending_courses = self.collect_course_status(browser)

            if not all_courses:
                print("[INFO] 课程列表为空，结束流程")
                break

            course_summaries: list[str] = []
            for course in all_courses:
                status = (
                    "待评价" if bool(course.get("can_evaluate", False)) else "已完成"
                )
                course_summaries.append(f"{course.get('title', '')}:{status}")
            print(f"[INFO] 课程列表: {' | '.join(course_summaries)}")

            available_courses: list[dict[str, str | int | bool]] = []
            for course in pending_courses:
                course_key = self.course_key(course)
                if (
                    course_key not in failed_course_keys
                    and course_key not in submitted_course_keys
                ):
                    available_courses.append(course)

            if not available_courses:
                if pending_courses:
                    pending_signature = "|".join(
                        sorted(self.course_key(course) for course in pending_courses)
                    )
                    if pending_signature == last_pending_signature:
                        unchanged_pending_rounds += 1
                    else:
                        unchanged_pending_rounds = 0
                    last_pending_signature = pending_signature

                    if unchanged_pending_rounds >= 1:
                        print("[WARN] 待评价状态未更新，停止重复处理同一课程")
                        break

                    self.open_course_list(browser)
                    time.sleep(1)
                    continue
                break

            current_course = available_courses[0]
            course_title = str(current_course.get("title", ""))
            teacher_name = str(current_course.get("teacher_name", "任课教师"))
            course_key = self.course_key(current_course)

            try:
                print(f"[INFO] 开始评价课程: {course_title}")
                self.open_course_eval_page(browser, current_course)
                selected_ok, selected_count = self.evaluate_current_course(
                    browser,
                    course_title,
                    teacher_name,
                )
                if not selected_ok:
                    raise RuntimeError("未找到可点击的评价选项")

                self.submit_and_back(browser)
                submitted_count += 1
                submitted_course_keys.add(course_key)
                unchanged_pending_rounds = 0
                last_pending_signature = ""
                print(
                    f"[INFO] 课程 {course_title} 提交成功，本轮选择项数量: {selected_count}"
                )
            except Exception as error:
                failed_course_keys.add(course_key)
                print(f"[WARN] 课程 {course_title} 评价失败: {error}")

        print(f"[INFO] 自动评价结束，共提交 {submitted_count} 门课程")
        response.text = browser.page_source
