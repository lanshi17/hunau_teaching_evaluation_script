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
    "{teacher_name}的《{course_name}》课程内容新颖实用，教学方法多样，课堂气氛活跃，让我对学科有了更深的认识和兴趣。",
    "《{course_name}》教学设计巧妙，{teacher_name}善于启发学生思考，知识点覆盖全面，课堂讨论充分，学习效果非常显著。",
    "{teacher_name}在《{course_name}》授课中表现出色，备课精心，教学热情高，能够因材施教，课堂互动自然，深受学生喜爱。",
    "《{course_name}》课程难度适中，{teacher_name}讲解透彻易懂，作业布置合理，考核方式公平，真正做到了教书育人。",
    "{teacher_name}的《{course_name}》课堂氛围融洽，师生关系和谐，教学内容前沿，方法创新，极大提升了我的专业素养。",
    "这门《{course_name}》课程安排合理，{teacher_name}讲课生动有趣，理论与实践并重，激发了我的学习兴趣和主动性。",
    "{teacher_name}在《{course_name}》教学中展现出了深厚的学术功底，课程内容丰富，讲解条理清晰，对学生指导耐心周到。",
    "《{course_name}》课程内容前沿实用，{teacher_name}教学经验丰富，课堂管理得当，知识传授到位，受益匪浅。",
    "{teacher_name}授课的《{course_name}》课程逻辑清晰，层次分明，案例贴切，能够很好地帮助学生理解和掌握知识要点。",
    "《{course_name}》课程质量上乘，{teacher_name}治学严谨，教学态度端正，注重培养学生独立思考能力，收获颇丰。",
    "{teacher_name}在《{course_name}》教学中倾注了大量心血，课程设计精良，教学手段多样，学生参与度高，效果显著。",
    "《{course_name}》教学内容丰富，{teacher_name}讲解生动形象，课堂气氛活跃，知识传授与能力培养并重，令人印象深刻。",
    "{teacher_name}的《{course_name}》课程规划合理，教学进度适中，注重理论联系实际，对学生的专业发展起到了很好的促进作用。",
    "这门《{course_name}》课程内容充实，{teacher_name}教学方法灵活，善于调动学生积极性，课堂效率高，学习成果显著。",
    "{teacher_name}在《{course_name}》授课中展现了优秀的教学水平，知识点讲解透彻，重视学生反馈，教学质量很高。",
    "《{course_name}》课程体系完善，{teacher_name}教学风格独特，内容深入浅出，能够激发学生的学习热情和探索精神。",
    "{teacher_name}的《{course_name}》课堂组织有序，教学内容丰富，注重学生能力培养，教学效果优秀，深受学生好评。",
    "《{course_name}》课程设计科学，{teacher_name}备课充分，授课认真，讲解耐心，能够针对学生特点进行个性化指导。",
    "{teacher_name}在《{course_name}》教学中展现了极高的专业水准，课程内容前沿，教学方法得当，学生收获满满。",
    "这门《{course_name}》课程安排合理紧凑，{teacher_name}教学态度认真，课堂互动良好，知识传授到位，满意度很高。",
    "{teacher_name}授课的《{course_name}》内容精彩，讲解细致入微，能够将复杂概念简单化，便于学生理解和掌握。",
    "《{course_name}》教学设计用心，{teacher_name}教学经验丰富，课堂管理有序，注重培养学生的创新思维和实践能力。",
)
