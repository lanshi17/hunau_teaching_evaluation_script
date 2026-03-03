LOGIN_URL = (
    "https://webvpn.hunau.edu.cn/https/"
    "77777776706e697374686562657374210e03473ff678aae237e91e44aaddcc6d"
    "/cas/login?service=http://gmsstu.hunau.edu.cn/cas"
)

INDEX_URL = (
    "https://webvpn.hunau.edu.cn/http/"
    "77777776706e697374686562657374211a1d5b62ea78eaeb37a91a55f196cb76737e87/index"
)

LOGIN_ACCOUNT_TAB_XPATHS = [
    "//*[contains(normalize-space(text()), '账号登录')]",
    "//*[contains(normalize-space(text()), '密码登录')]",
    "//*[contains(@class, 'account') and (self::a or self::button or self::span)]",
]
LOGIN_USERNAME_XPATHS = [
    '//*[@id="loginways8"]/div/span[1]/input',
    "//input[@name='username' and not(@type='hidden')]",
    "//input[contains(@placeholder,'账号') or contains(@placeholder,'学号') or contains(@placeholder,'用户名')]",
    "//input[contains(@id,'user') and (@type='text' or not(@type))]",
]
LOGIN_PASSWORD_XPATHS = [
    '//*[@id="loginways8"]/div/span[2]/input',
    "//input[@name='password']",
    "//input[@type='password']",
]
LOGIN_BUTTON_XPATHS = [
    '//*[@id="loginways8"]/button',
    "//button[@type='submit']",
    "//input[@type='submit']",
    "//button[contains(normalize-space(text()), '登录')]",
]
QR_CODE_XPATHS = [
    '//*[@id="qrcodeImg1"]',
    "//img[contains(@id,'qrcode') or contains(@class,'qrcode')]",
    "//canvas[contains(@id,'qrcode') or contains(@class,'qrcode')]",
]

TEACHING_MANAGEMENT_XPATH = '//*[@id="jx"]'
COURSE_EVAL_MENU_XPATH = '//*[@id="nav_box"]/div[3]/ul/li[8]/a'
COURSE_LIST_CONTAINER_XPATH = "/html/body/div/div"
COURSE_LIST_TABLE_XPATH = (
    "/html/body/div/div/div/div[2]/div/div/div[2]/div[1]/div/table"
)
COURSE_LIST_ROWS_XPATH = "//*[starts-with(@id, 'datagrid-row-r1-2-')]"
COURSE_NAME_IN_ROW_XPATHS = ["./td[4]/div/span[1]", "./td[4]/div", "./td[4]"]
COURSE_TEACHER_IN_ROW_XPATHS = ["./td[6]/div/span[1]", "./td[6]/div", "./td[6]"]
COURSE_ACTION_IN_ROW_XPATH = "./td[10]//a | ./td[10]//*[@role='button' or @role='link']"
COURSE_ACTION_LINKS_XPATH = (
    "//*[starts-with(@id, 'datagrid-row-r1-2-')]/td[10]//a"
    " | "
    "//*[starts-with(@id, 'datagrid-row-r1-2-')]/td[10]//*[@role='button' or @role='link']"
)
COURSE_ACTION_BY_ROW_INDEX_XPATH = (
    "//*[@id='datagrid-row-r1-2-{index}']/td[10]//a"
    " | "
    "//*[@id='datagrid-row-r1-2-{index}']/td[10]//*[@role='button' or @role='link']"
)

SUBMIT_XPATH = '//*[@id="lnksubmit"]'
CONFIRM_XPATH = "/html/body/div[2]/div[2]/div[4]/a[1]/span/span"
BACK_XPATH = '//*[@id="btn_back"]'

EVAL_FIRST_OPTION_XPATH = '//*[@id="cc"]/table/tbody/tr[2]/td'
EVAL_ROWS_XPATH = '//*[@id="cc"]/table/tbody/tr[position()>=2]'
EVAL_SUBJECTIVE_ROW_XPATH = '//*[@id="cc"]/table/tbody/tr[33]/td'
EVAL_SUBJECTIVE_INPUT_XPATH = '//*[@id="txt017"]'
EVAL_EXCELLENT_IN_ROW_XPATHS = [
    ".//input[contains(@id,'6001')]",
    ".//label[normalize-space()='优']",
    ".//span[normalize-space()='优']",
    ".//td[normalize-space()='优']",
    "./td[2]",
]

QUESTION_COUNT = 16
RADIO_ID_TEMPLATE = "rdo{:02d}6001"

ACTION_POSITIVE_TEXT_MARKERS = [
    "评价",
    "评教",
    "评估",
    "问卷",
    "evaluate",
    "evaluation",
]
ACTION_NEGATIVE_TEXT_MARKERS = ["已评", "已完成", "已提交", "查看", "详情"]
ACTION_POSITIVE_CLASS_MARKERS = ["icon-edit", "icon-pencil", "edit", "evaluate"]
ACTION_NEGATIVE_CLASS_MARKERS = [
    "disabled",
    "icon-search",
    "icon-view",
    "icon-eye",
    "icon-check",
    "icon-ok",
]
ACTION_POSITIVE_ATTR_MARKERS = ["evaluate", "evaluation", "pingjia", "pj", "toeval"]

DEFAULT_REVIEW_PROMPT = (
    "请围绕课程《{course_name}》和教师{teacher_name}生成一段{style}的课程评价意见，"
    "中文，不分点，15到25字，突出教学认真、内容扎实与学习收获。"
)

DEFAULT_STATIC_REVIEW_LIBRARY = (
    "《{course_name}》课程体系完整、内容充实，{teacher_name}授课认真负责，讲解深入浅出，课堂节奏把握得当，让我受益很大。",
    "通过《{course_name}》学习，我对相关知识建立了更系统的理解。{teacher_name}教学思路清晰、案例丰富，课堂氛围积极，整体体验很好。",
    "{teacher_name}在《{course_name}》教学中注重理论与实践结合，讲解耐心细致，课堂互动充分，学习收获明显，课程质量优秀。",
    "《{course_name}》内容安排循序渐进，重点突出。{teacher_name}教学态度严谨、讲授生动，能够激发思考，帮助我提升了专业能力。",
    "这门《{course_name}》课程整体设计科学合理。{teacher_name}备课充分、表达清晰，课堂反馈及时，学习过程顺畅且富有启发性。",
    "在《{course_name}》学习过程中，{teacher_name}注重方法引导与能力培养，课堂互动效果良好，帮助我巩固了知识并拓展了视野。",
    "《{course_name}》课程目标明确、内容实用。{teacher_name}授课认真、讲解到位，课堂组织有序，学习成效显著，值得肯定。",
    "{teacher_name}在《{course_name}》教学中展现了很高的专业素养，课程内容深入且实用，课堂氛围积极，整体学习体验非常好。",
)
