import html
import re
from collections import OrderedDict

import streamlit as st


st.set_page_config(
    page_title="AI 简历优化助手",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# 岗位关键词库：展示名称对应若干常见表达，便于覆盖不同 JD 写法。
KEYWORD_LIBRARY = OrderedDict(
    {
        "数据分析": ["数据分析", "数据驱动", "数据监控", "数据指标", "数据报表", "数据"],
        "用户增长": ["用户增长", "增长策略", "拉新", "促活", "留存", "增长"],
        "竞品分析": ["竞品分析", "竞品调研", "行业调研", "市场调研", "竞品"],
        "内容运营": ["内容运营", "内容策划", "内容生产", "内容创作", "选题", "内容"],
        "AIGC": ["aigc", "生成式ai", "生成式人工智能", "ai生成", "人工智能生成内容"],
        "AI 工具": ["ai工具", "ai 工具", "大模型", "chatgpt", "提示词", "prompt"],
        "项目管理": ["项目管理", "项目推进", "项目协同", "进度管理", "项目"],
        "用户需求": ["用户需求", "需求分析", "需求调研", "用户痛点", "用户研究", "需求"],
        "产品优化": ["产品优化", "功能优化", "迭代优化", "产品迭代", "体验优化", "迭代"],
        "活动策划": ["活动策划", "营销活动", "运营活动", "活动执行", "活动"],
        "产品设计": ["产品设计", "原型设计", "产品方案", "功能设计", "原型"],
        "需求文档": ["需求文档", "prd", "产品文档", "需求说明书"],
        "用户运营": ["用户运营", "社群运营", "用户维护", "用户分层", "社群"],
        "新媒体运营": ["新媒体运营", "公众号", "小红书", "抖音", "视频号", "新媒体"],
        "市场推广": ["市场推广", "品牌推广", "品牌传播", "营销推广", "市场营销"],
        "转化优化": ["转化率", "转化路径", "转化优化", "转化"],
        "复盘优化": ["复盘分析", "项目复盘", "运营复盘", "复盘"],
        "文案策划": ["文案策划", "文案撰写", "脚本撰写", "视频脚本", "文案"],
        "跨部门协作": ["跨部门", "协同", "沟通协调", "团队协作", "协作"],
        "执行落地": ["执行落地", "落地执行", "推进落地", "执行能力", "执行"],
    }
)

CAPABILITY_MAP = OrderedDict(
    {
        "数据分析能力": ["数据分析", "用户增长", "转化优化", "复盘优化"],
        "用户理解能力": ["用户需求", "用户运营", "用户增长"],
        "产品思维": ["竞品分析", "用户需求", "产品优化", "产品设计", "需求文档"],
        "内容策划能力": ["内容运营", "新媒体运营", "文案策划", "活动策划"],
        "AI 工具应用能力": ["AIGC", "AI 工具"],
        "项目推进能力": ["项目管理", "执行落地", "跨部门协作"],
        "增长与转化意识": ["用户增长", "转化优化", "市场推广"],
        "市场与品牌洞察": ["市场推广", "竞品分析"],
        "沟通协作能力": ["跨部门协作", "项目管理"],
    }
)

TARGET_FOCUS = {
    "产品运营": ["用户需求", "产品优化", "数据分析", "用户增长", "竞品分析", "项目管理"],
    "AI 产品助理": ["AIGC", "AI 工具", "用户需求", "产品设计", "需求文档", "竞品分析"],
    "内容运营": ["内容运营", "文案策划", "数据分析", "用户需求", "复盘优化", "转化优化"],
    "AIGC 运营": ["AIGC", "AI 工具", "内容运营", "数据分析", "用户需求", "复盘优化"],
    "新媒体运营": ["新媒体运营", "内容运营", "文案策划", "数据分析", "用户增长", "活动策划"],
    "市场/品牌运营": ["市场推广", "竞品分析", "活动策划", "内容运营", "数据分析", "跨部门协作"],
}

ACTION_WORDS = ["负责", "参与", "完成", "策划", "推进", "优化", "分析", "搭建", "运营", "撰写", "执行"]
BONUS_WORDS = ["数据", "增长", "复盘", "分析", "转化", "用户", "aigc", "ai", "竞品", "项目", "策划", "执行"]
RESULT_WORDS = ["提升", "增长", "降低", "优化", "达成", "转化", "沉淀", "产出", "完成", "改善"]
NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*(?:%|％|万|千|百|人|次|篇|条|个|项|场|天|小时|元)?")


def normalize_text(text):
    """统一大小写与空白，提升规则匹配稳定性。"""
    return re.sub(r"\s+", "", text.lower())


def contains_alias(text, aliases):
    normalized = normalize_text(text)
    return any(normalize_text(alias) in normalized for alias in aliases)


def extract_keywords(jd_text, target_role):
    """优先提取 JD 明确出现的词，再用岗位类型补足分析维度。"""
    explicit = [
        keyword
        for keyword, aliases in KEYWORD_LIBRARY.items()
        if contains_alias(jd_text, aliases)
    ]
    for keyword in TARGET_FOCUS[target_role]:
        if keyword not in explicit and len(explicit) < 10:
            explicit.append(keyword)
    return explicit[:10]


def extract_capabilities(keywords):
    capabilities = []
    for capability, related_keywords in CAPABILITY_MAP.items():
        if any(keyword in keywords for keyword in related_keywords):
            capabilities.append(capability)
    return capabilities[:7]


def keyword_is_matched(resume_text, keyword):
    return contains_alias(resume_text, KEYWORD_LIBRARY[keyword])


def calculate_score(resume_text, keywords, capabilities):
    matched_keywords = [keyword for keyword in keywords if keyword_is_matched(resume_text, keyword)]
    keyword_ratio = len(matched_keywords) / max(len(keywords), 1)
    keyword_score = round(keyword_ratio * 55)

    normalized_resume = normalize_text(resume_text)
    bonus_hits = [word for word in BONUS_WORDS if word in normalized_resume]
    ability_score = min(20, len(bonus_hits) * 2)

    numbers = NUMBER_PATTERN.findall(resume_text)
    result_hits = [word for word in RESULT_WORDS if word in resume_text]
    if len(numbers) >= 3 and len(result_hits) >= 2:
        data_score = 15
        data_status = "较充分"
    elif numbers:
        data_score = 9
        data_status = "有数据，仍可加强"
    elif len(result_hits) >= 2:
        data_score = 5
        data_status = "有结果表达，缺少数字"
    else:
        data_score = 0
        data_status = "缺少数据指标"

    text_length = len(normalize_text(resume_text))
    if text_length >= 500:
        completeness_score = 10
    elif text_length >= 280:
        completeness_score = 8
    elif text_length >= 150:
        completeness_score = 5
    else:
        completeness_score = 2

    score = keyword_score + ability_score + data_score + completeness_score
    penalties = []
    if not numbers:
        score -= 8
        penalties.append("缺少量化指标")
    if text_length < 150:
        score -= 10
        penalties.append("简历内容偏短")
    elif text_length < 280:
        score -= 4
        penalties.append("经历信息不够完整")
    if keyword_ratio < 0.2:
        score = min(score, 55)
        penalties.append("岗位关键词覆盖较低")

    score = max(0, min(100, score))
    if score >= 85:
        evaluation = "整体匹配度较高，岗位相关经历较明确，可进一步强化成果与差异化表达。"
    elif score >= 70:
        evaluation = "具备较好的岗位匹配基础，但关键词覆盖和数据化表达仍有提升空间。"
    elif score >= 50:
        evaluation = "已有部分可迁移经验，建议围绕目标岗位重组经历并补充结果证明。"
    else:
        evaluation = "当前简历与目标岗位的直接关联较弱，需要优先补强关键能力与经历表达。"

    return {
        "score": score,
        "evaluation": evaluation,
        "matched_keywords": matched_keywords,
        "keyword_score": keyword_score,
        "ability_score": ability_score,
        "data_score": data_score,
        "completeness_score": completeness_score,
        "data_status": data_status,
        "numbers": numbers,
        "penalties": penalties,
        "capability_coverage": min(
            len(capabilities),
            sum(
                1
                for capability in capabilities
                if any(
                    keyword_is_matched(resume_text, keyword)
                    for keyword in CAPABILITY_MAP[capability]
                    if keyword in KEYWORD_LIBRARY
                )
            ),
        ),
    }


def build_strengths(resume_text, matched_keywords, target_role, numbers):
    strengths = []
    matched_set = set(matched_keywords)

    if matched_set & {"内容运营", "新媒体运营", "文案策划", "活动策划"}:
        strengths.append("具备内容策划与执行基础，经历能够覆盖从选题、产出到落地的运营环节。")
    if matched_set & {"用户需求", "用户运营", "用户增长"}:
        strengths.append("简历中体现了对用户、需求或增长目标的关注，与岗位的用户导向较一致。")
    if matched_set & {"AIGC", "AI 工具"}:
        strengths.append("已有 AI 或 AIGC 工具应用意识，这对目标岗位形成了较直接的能力加分。")
    if matched_set & {"数据分析", "转化优化", "复盘优化"}:
        strengths.append("能够将数据分析、复盘或转化意识带入工作，不局限于单纯执行任务。")
    if matched_set & {"项目管理", "跨部门协作", "执行落地"}:
        strengths.append("具备项目推进与协作经验，能够支撑多角色配合和任务落地。")
    if numbers:
        strengths.append("已有量化信息作为成果证据，能够提升经历描述的可信度和说服力。")
    if any(word in resume_text for word in ["优化", "复盘", "迭代", "改进"]):
        strengths.append("经历中出现持续优化和复盘动作，体现了一定的问题意识与迭代思维。")

    fallback = [
        f"现有经历具备向“{target_role}”迁移的基础，可以通过重组表达突出岗位相关价值。",
        "简历中包含明确的执行动作，说明具备将任务推进到落地阶段的实践基础。",
        "经历信息具有进一步提炼空间，经过岗位化表达后能够形成更清晰的个人优势。",
    ]
    for item in fallback:
        if len(strengths) >= 3:
            break
        strengths.append(item)
    return strengths[:5]


def build_weaknesses(resume_text, keywords, matched_keywords, numbers):
    weaknesses = []
    missing_keywords = [keyword for keyword in keywords if keyword not in matched_keywords]

    if not numbers:
        weaknesses.append("缺少可量化的数据指标，招聘方难以快速判断工作的规模、效果和个人贡献。")
    elif len(numbers) < 3:
        weaknesses.append("量化成果较少，建议为重点经历补充规模、效率、增长或转化等指标。")
    if not any(word in resume_text for word in ["复盘", "优化", "迭代", "洞察"]):
        weaknesses.append("经历偏重任务过程，尚未充分体现复盘、判断和持续优化能力。")
    if not any(word in resume_text.lower() for word in ["ai", "aigc", "大模型", "提示词"]):
        weaknesses.append("AI 工具应用经验不够突出，难以体现对新工具的理解和提效能力。")
    if not any(word in resume_text for word in ["用户需求", "用户痛点", "用户反馈", "用户研究"]):
        weaknesses.append("没有明确呈现用户需求分析过程，产品思维和用户视角仍不够直观。")
    if missing_keywords:
        weaknesses.append(
            f"与 JD 相关的“{'、'.join(missing_keywords[:3])}”尚未在简历中形成明确证据。"
        )
    if len(normalize_text(resume_text)) < 280:
        weaknesses.append("简历内容较短，项目背景、关键动作和结果之间的逻辑链条不够完整。")

    fallback = [
        "重点经历还可以进一步区分团队成果与个人贡献，让招聘方更快判断你的具体作用。",
        "部分项目缺少明确的背景与目标说明，建议补充“为什么做”以及判断成功的标准。",
        "能力覆盖较全面，但差异化标签还不够集中，建议围绕目标岗位强化一项最有说服力的核心优势。",
        "项目之间的能力递进关系不够明显，可以通过调整顺序呈现从执行到分析、优化和推进的成长路径。",
    ]
    for item in fallback:
        if len(weaknesses) >= 3:
            break
        weaknesses.append(item)

    return weaknesses[:5]


def build_suggestions(resume_text, target_role, missing_keywords, numbers):
    suggestions = []
    if "负责" in resume_text:
        suggestions.append(
            "减少“负责某项工作”的职责式表述，改成“围绕目标完成什么动作，并产生什么结果”的成果式结构。"
        )
    if not numbers:
        suggestions.append(
            "回溯真实工作记录，补充内容产出量、阅读量、用户数、活动场次、效率变化等可验证指标；没有数据时不要编造。"
        )
    if any(word in resume_text for word in ["公众号", "内容", "文案"]):
        suggestions.append(
            "将“负责公众号内容”细化为“参与内容选题、撰写与发布，结合用户反馈和竞品表现优化标题及内容结构”。"
        )
    if any(word in resume_text for word in ["视频", "脚本"]):
        suggestions.append(
            "将“做过视频脚本”改为“围绕传播目标完成短视频选题、脚本策划与分镜设计，协同推进制作发布”。"
        )
    if any(keyword in missing_keywords for keyword in ["AIGC", "AI 工具"]):
        suggestions.append(
            "补充真实的 AI 工具使用场景，例如资料整理、竞品归纳、文案初稿或信息结构化，并说明人工校验流程。"
        )
    if any(keyword in missing_keywords for keyword in ["用户需求", "产品优化", "竞品分析"]):
        suggestions.append(
            "在重点项目中增加“如何发现问题—如何分析用户或竞品—如何提出优化方案”的完整思考链路。"
        )
    suggestions.append(
        f"调整经历排序，把与“{target_role}”最相关的项目放在前面，并在每段首句直接写出业务目标和个人角色。"
    )
    return suggestions[:6]


def split_resume_sentences(resume_text):
    lines = re.split(r"[\n；。]+", resume_text)
    return [re.sub(r"^[\s\-•·\d.、]+", "", line).strip() for line in lines if len(line.strip()) >= 8]


def select_source_points(resume_text):
    sentences = split_resume_sentences(resume_text)
    scored = []
    for index, sentence in enumerate(sentences):
        score = sum(1 for word in ACTION_WORDS + BONUS_WORDS if word in sentence.lower())
        score += 2 if NUMBER_PATTERN.search(sentence) else 0
        scored.append((score, -index, sentence))
    selected = [item[2] for item in sorted(scored, reverse=True)[:3]]
    return selected or ["参与相关项目执行与内容产出"]


def clean_source_sentence(sentence):
    sentence = re.sub(r"^(负责|参与|协助|主要负责)[:：]?", "", sentence).strip()
    return sentence[:65].rstrip("，,；;。")


def rewrite_experience(resume_text, target_role, matched_keywords):
    sources = select_source_points(resume_text)
    lines = []
    first = clean_source_sentence(sources[0])
    lines.append(f"围绕{target_role}相关目标，梳理任务重点并推进{first}，确保关键事项按计划落地。")

    if len(sources) > 1:
        second = clean_source_sentence(sources[1])
        lines.append(f"结合目标用户与实际业务需求，完成{second}，持续优化内容结构与执行流程。")
    else:
        lines.append("结合目标用户与业务需求拆解工作任务，关注用户反馈并持续优化交付质量。")

    if {"AIGC", "AI 工具"} & set(matched_keywords) or re.search(r"ai|aigc|大模型", resume_text, re.I):
        lines.append("应用 AI 工具辅助资料整理、信息归纳与内容初稿生成，通过人工校验保障输出质量，提升内容表达效率。")
    else:
        lines.append("尝试将 AI 工具用于资料整理、竞品归纳与内容辅助，提升信息处理效率并沉淀可复用流程。")

    if NUMBER_PATTERN.search(resume_text):
        number_text = "、".join(NUMBER_PATTERN.findall(resume_text)[:3])
        lines.append(f"围绕核心指标开展数据记录与复盘，保留原经历中的真实成果数据（{number_text}），提炼后续优化方向。")
    else:
        lines.append("结合执行反馈复盘关键问题，优化内容表达与协作方式，沉淀可复用的项目方法论。")
    return lines


def build_greeting(target_role, matched_keywords, resume_text):
    highlights = []
    if set(matched_keywords) & {"内容运营", "新媒体运营", "文案策划"}:
        highlights.append("内容策划与运营执行")
    if set(matched_keywords) & {"数据分析", "复盘优化", "转化优化"}:
        highlights.append("数据复盘")
    if set(matched_keywords) & {"AIGC", "AI 工具"} or re.search(r"ai|aigc", resume_text, re.I):
        highlights.append("AI 工具应用")
    if set(matched_keywords) & {"项目管理", "跨部门协作"}:
        highlights.append("项目协作推进")
    if not highlights:
        highlights = ["内容执行", "项目推进"]
    highlight_text = "、".join(highlights[:3])
    return (
        f"您好，我正在关注贵公司的{target_role}岗位。我有{highlight_text}相关实践，"
        "能够从用户需求和业务目标出发推进任务，也会主动复盘并优化工作方法。"
        "我对岗位方向很感兴趣，希望有机会进一步沟通，感谢您查看我的简历。"
    )


def build_interview_highlights(target_role, matched_keywords):
    highlights = [
        "我不是只完成执行任务，而是会先拆解目标用户、业务目标和关键路径，再确定内容或产品动作。",
        "我会结合竞品表现、用户反馈和过程数据进行复盘，把一次性经验沉淀为后续可复用的方法。",
        "我尝试使用 AI 工具辅助信息整理、方案构思和内容生产，同时保留人工判断与结果校验。",
    ]
    if "用户需求" in matched_keywords:
        highlights[0] = "我会从用户需求和使用场景出发拆解问题，再将需求转化为可执行的内容或产品方案。"
    if {"数据分析", "用户增长", "转化优化"} & set(matched_keywords):
        highlights[1] = "我会围绕核心指标观察执行效果，通过数据复盘定位问题，并提出下一轮优化方向。"
    if target_role == "AI 产品助理":
        highlights[2] = "我能把 AI 能力与具体用户场景结合，关注工具边界、输出质量和可复用工作流程，而不只是调用工具。"
    return highlights


def build_keyword_table(keywords, matched_keywords, target_role):
    focus_keywords = TARGET_FOCUS[target_role]
    rows = []
    for keyword in keywords:
        matched = keyword in matched_keywords
        if keyword in focus_keywords[:3]:
            importance = "高"
        elif keyword in focus_keywords:
            importance = "中"
        else:
            importance = "一般"
        suggestion = (
            "已命中，建议补充具体动作或成果证明。"
            if matched
            else f"建议在真实经历中补充“{keyword}”相关场景；没有相关经验时不要生硬堆词。"
        )
        rows.append(
            {
                "JD 关键词": keyword,
                "简历是否命中": "是" if matched else "否",
                "重要程度": importance,
                "修改建议": suggestion,
            }
        )
    return rows


def build_diagnostics(resume_text, keywords, matched_keywords, score_info):
    normalized = normalize_text(resume_text)
    keyword_ratio = len(matched_keywords) / max(len(keywords), 1)
    result_count = sum(word in resume_text for word in RESULT_WORDS)

    dimensions = [
        (
            "数据化表达",
            90 if len(score_info["numbers"]) >= 3 else 65 if score_info["numbers"] else 30,
            "已有多处数据支撑，注意说明指标口径。"
            if len(score_info["numbers"]) >= 3
            else "有少量数字，建议补充重点经历的规模、效率或结果。"
            if score_info["numbers"]
            else "缺少量化证据，优先回溯真实业务数据。",
        ),
        (
            "岗位关键词覆盖",
            round(keyword_ratio * 100),
            "核心词覆盖较充分，可继续强化证据。"
            if keyword_ratio >= 0.7
            else "部分岗位关键词尚未在经历中形成明确证明。",
        ),
        (
            "结果意识",
            min(100, 30 + result_count * 15),
            "已体现优化或成果意识。"
            if result_count >= 3
            else "描述仍偏任务过程，建议增加结果、复盘和后续影响。",
        ),
        (
            "AI 工具使用",
            90 if any(word in normalized for word in ["ai", "aigc", "大模型", "提示词"]) else 25,
            "已体现 AI 工具应用，建议补充使用场景和人工校验。"
            if any(word in normalized for word in ["ai", "aigc", "大模型", "提示词"])
            else "未体现 AI 工具应用，可补充真实的提效场景。",
        ),
        (
            "项目经验",
            85 if any(word in resume_text for word in ["项目", "实习", "活动"]) and len(normalized) >= 280 else 55,
            "项目信息较完整，建议进一步明确个人贡献。"
            if len(normalized) >= 280
            else "项目背景、个人动作和结果链路仍需补充。",
        ),
        (
            "产品/运营思维",
            min(
                100,
                35
                + 12
                * sum(
                    word in resume_text
                    for word in ["用户", "需求", "竞品", "数据", "复盘", "优化"]
                ),
            ),
            "已体现用户、数据或优化视角。"
            if any(word in resume_text for word in ["用户", "需求", "竞品", "复盘"])
            else "建议补充用户需求、问题判断和优化思路。",
        ),
    ]
    return [
        {"诊断维度": name, "评分": max(0, min(100, score)), "诊断结论": conclusion}
        for name, score, conclusion in dimensions
    ]


def build_comparison(resume_text, rewrite_lines):
    sources = select_source_points(resume_text)
    rows = []
    for index, optimized in enumerate(rewrite_lines[:3]):
        original = sources[index] if index < len(sources) else "原简历未明确体现该能力。"
        rows.append({"原始表达": original, "优化表达": optimized})
    return rows


def build_risk_tips(score_info, missing_keywords, resume_text):
    risks = []
    if not score_info["numbers"]:
        risks.append("成果可信度风险：缺少真实数据，招聘方难以判断工作效果。")
    if len(missing_keywords) >= 4:
        risks.append("岗位匹配风险：多个核心关键词未命中，可能影响简历初筛。")
    if "负责" in resume_text and not any(word in resume_text for word in ["提升", "增长", "优化"]):
        risks.append("表达同质化风险：职责描述较多，个人贡献与结果不够突出。")
    if len(normalize_text(resume_text)) < 280:
        risks.append("信息完整性风险：经历较短，项目背景、动作和结果链路不足。")
    if not risks:
        risks.append("当前无明显结构性风险，重点检查数据真实性、岗位名称和时间信息是否准确。")
    return risks[:3]


def build_project_resume_description():
    return (
        "设计并开发“AI 简历优化助手”产品 Demo，面向大学生及转岗求职者，"
        "将 JD 解析、关键词匹配、六维简历诊断、经历改写和求职话术整合为完整分析流程；"
        "使用 Python、Streamlit 与本地规则引擎构建可解释的 100 分评分模型，"
        "在无外部 API 的条件下实现低成本、可运行且便于迭代的产品 MVP。"
    )


def build_markdown_report(result, target_role):
    score_info = result["score_info"]
    keyword_lines = "\n".join(
        f"- {row['JD 关键词']}：{row['简历是否命中']}｜重要程度：{row['重要程度']}"
        for row in result["keyword_table"]
    )
    diagnostic_lines = "\n".join(
        f"- {row['诊断维度']}：{row['评分']} 分｜{row['诊断结论']}"
        for row in result["diagnostics"]
    )
    suggestion_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(result["suggestions"], 1))
    risk_lines = "\n".join(f"- {item}" for item in result["risk_tips"])
    rewrite_lines = "\n".join(f"- {item}" for item in result["rewrite"])
    return f"""# AI 简历优化分析报告

## 分析概览

- 目标岗位：{target_role}
- 简历匹配度：{score_info['score']} / 100
- 关键词命中：{len(score_info['matched_keywords'])} / {len(result['keywords'])}
- 能力覆盖：{score_info['capability_coverage']} / {len(result['capabilities'])}
- 数据化表达：{score_info['data_status']}

## 综合评价

{score_info['evaluation']}

## 岗位关键词命中

{keyword_lines}

## 六维问题诊断

{diagnostic_lines}

## 优先优化建议

{suggestion_lines}

## 简历风险提示

{risk_lines}

## 经历改写建议

{rewrite_lines}

> 本报告由本地规则生成，请结合真实经历核对内容与数据。
"""


def analyze_resume(jd_text, resume_text, target_role):
    keywords = extract_keywords(jd_text, target_role)
    capabilities = extract_capabilities(keywords)
    score_info = calculate_score(resume_text, keywords, capabilities)
    matched_keywords = score_info["matched_keywords"]
    missing_keywords = [keyword for keyword in keywords if keyword not in matched_keywords]

    rewrite_lines = rewrite_experience(resume_text, target_role, matched_keywords)
    result = {
        "keywords": keywords,
        "capabilities": capabilities,
        "score_info": score_info,
        "strengths": build_strengths(
            resume_text, matched_keywords, target_role, score_info["numbers"]
        ),
        "weaknesses": build_weaknesses(
            resume_text, keywords, matched_keywords, score_info["numbers"]
        ),
        "suggestions": build_suggestions(
            resume_text, target_role, missing_keywords, score_info["numbers"]
        ),
        "rewrite": rewrite_lines,
        "greeting": build_greeting(target_role, matched_keywords, resume_text),
        "interview_highlights": build_interview_highlights(target_role, matched_keywords),
        "keyword_table": build_keyword_table(keywords, matched_keywords, target_role),
        "diagnostics": build_diagnostics(
            resume_text, keywords, matched_keywords, score_info
        ),
        "comparison": build_comparison(resume_text, rewrite_lines),
        "risk_tips": build_risk_tips(score_info, missing_keywords, resume_text),
        "project_resume_description": build_project_resume_description(),
    }
    result["markdown_report"] = build_markdown_report(result, target_role)
    return result


def render_tags(items, tag_type="primary"):
    class_name = "tag tag-success" if tag_type == "success" else "tag"
    tags = "".join(f'<span class="{class_name}">{item}</span>' for item in items)
    st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)


def render_numbered_cards(items, tone="default"):
    for index, item in enumerate(items, 1):
        st.markdown(
            f"""
            <div class="list-card {tone}">
                <span class="list-index">{index:02d}</span>
                <span>{item}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric_card(title, value, caption, highlight=False):
    highlight_class = "metric-highlight" if highlight else ""
    st.markdown(
        f"""
        <div class="metric-card {highlight_class}">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_iteration_roadmap():
    items = [
        ("V1 规则匹配版", "完成本地规则库、关键词命中、基础评分和求职文案生成。"),
        ("V2 视觉优化版", "升级蓝白 AI SaaS 工作台界面，增强报告、诊断和展示体验。"),
        ("V3 AI API 智能分析版", "接入大模型进行语义理解、个性化改写和多轮追问。"),
        ("V4 在线部署版", "支持在线访问、报告分享、历史版本管理和更多岗位模板。"),
    ]
    cards = "".join(
        f"""
        <div class="roadmap-card">
            <div class="roadmap-version">{title}</div>
            <div class="roadmap-text">{text}</div>
        </div>
        """
        for title, text in items
    )
    st.markdown(
        f"""
        <div class="roadmap-section">
            <div id="iteration-section"></div>
            <div class="section-label">产品迭代方向</div>
            <div class="section-note">用版本路线说明这个 Demo 的产品规划和后续可扩展性。</div>
            <div class="roadmap-grid">{cards}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_nav():
    st.markdown(
        """
        <div class="top-nav">
            <a class="top-brand" href="#ai-resume-home">
                <span class="top-logo">AI</span>
                <span>AI 简历优化助手</span>
            </a>
            <div class="top-links">
                <a class="active" href="#hero-section">首页</a>
                <a href="#features-section">产品功能</a>
                <a href="#workflow-section">使用流程</a>
                <a href="#report-section">分析报告</a>
                <a href="#iteration-section">迭代方向</a>
            </div>
            <div class="top-actions">
                <span class="top-version">Demo Version 2.0</span>
                <a class="top-cta" href="#analysis-section">开始分析</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --blue: #2563EB;
            --blue-dark: #1D4ED8;
            --ink: #111827;
            --muted: #6B7280;
            --line: #E5E7EB;
            --panel: #FFFFFF;
            --bg: #F6F8FC;
            --soft-blue: #EFF6FF;
            --green: #15803D;
            --soft-green: #ECFDF5;
            --orange: #C2410C;
            --soft-orange: #FFF7ED;
            --shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
            --small-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }
        .stApp { background: linear-gradient(180deg, #F6F9FF 0%, #F6F8FC 42%, #FFFFFF 100%); color: var(--ink); }
        .block-container { max-width: 1160px; padding-top: 0.55rem; padding-bottom: 4rem; }
        [data-testid="stHeader"] {
            background: transparent !important; height: 0 !important; min-height: 0 !important;
        }
        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
        }
        [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
        .top-nav {
            position: sticky; top: 0; z-index: 50; height: 60px; display: flex; align-items: center;
            justify-content: space-between; gap: 1.2rem; padding: 0 1rem 0 0.85rem; margin-bottom: 1rem;
            background: rgba(255,255,255,0.94); border: 1px solid #E5E7EB; border-bottom-color: #DBEAFE;
            border-radius: 16px; backdrop-filter: blur(14px); box-shadow: 0 8px 22px rgba(15,23,42,0.045);
        }
        .top-brand {
            display: inline-flex; align-items: center; gap: 0.62rem; color: #0F172A !important;
            text-decoration: none !important; font-weight: 850; white-space: nowrap;
        }
        .top-logo {
            width: 32px; height: 32px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center;
            color: #FFFFFF; font-size: 0.82rem; font-weight: 900; background: linear-gradient(135deg, #2563EB, #1D4ED8);
            box-shadow: 0 8px 18px rgba(37,99,235,0.2);
        }
        .top-links { display: flex; align-items: center; gap: 1.25rem; font-size: 0.88rem; }
        .top-links a { color: #475569 !important; text-decoration: none !important; font-weight: 680; }
        .top-links a:hover, .top-links a.active { color: #2563EB !important; }
        .top-actions { display: flex; align-items: center; gap: 0.7rem; white-space: nowrap; }
        .top-version { color: #64748B; background: #F1F5F9; border-radius: 999px; padding: 0.28rem 0.65rem; font-size: 0.78rem; font-weight: 720; }
        .top-cta {
            color: #FFFFFF !important; text-decoration: none !important; background: linear-gradient(135deg, #2563EB, #1D4ED8);
            border-radius: 999px; padding: 0.45rem 0.9rem; font-size: 0.84rem; font-weight: 780;
            box-shadow: 0 8px 18px rgba(37,99,235,0.22);
        }
        .hero {
            position: relative; overflow: hidden; padding: 2.05rem 2.25rem 1.8rem; border-radius: 26px;
            background:
                radial-gradient(circle at 86% 12%, rgba(37,99,235,0.12), rgba(37,99,235,0) 30%),
                linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 62%, #FFFFFF 100%);
            color: var(--ink); border: 1px solid rgba(219, 234, 254, 0.9);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05); margin-bottom: 0.75rem;
        }
        .hero::after {
            content: ""; position: absolute; right: -80px; top: -70px; width: 260px; height: 260px;
            border-radius: 999px; background: rgba(37, 99, 235, 0.12); filter: blur(2px);
        }
        .hero-kicker {
            display: inline-flex; align-items: center; padding: 0.34rem 0.72rem;
            border-radius: 999px; background: #DBEAFE; color: var(--blue-dark);
            font-size: 0.78rem; letter-spacing: 0.08em; font-weight: 800;
        }
        .hero h1 { margin: 0.6rem 0 0.42rem; font-size: 2.58rem; line-height: 1.14; letter-spacing: -0.04em; color: #0F172A; }
        .hero-subtitle { color: #1E40AF; font-weight: 750; font-size: 1.02rem; margin-bottom: 0.42rem; }
        .hero p { max-width: 760px; margin: 0; color: #475569; line-height: 1.72; font-size: 0.96rem; }
        .hero-badges { margin-top: 0.85rem; display: flex; gap: 0.6rem; flex-wrap: wrap; }
        .hero-badge {
            border: 1px solid #BFDBFE; background: rgba(255,255,255,0.82); color: #1D4ED8;
            border-radius: 999px; padding: 0.34rem 0.78rem; font-size: 0.8rem; font-weight: 700;
        }
        .hero-actions { margin-top: 1.05rem; display: flex; gap: 0.75rem; flex-wrap: wrap; }
        .hero-primary, .hero-secondary {
            display: inline-flex; align-items: center; justify-content: center; border-radius: 999px;
            padding: 0.66rem 1.08rem; text-decoration: none !important; font-size: 0.92rem; font-weight: 820;
        }
        .hero-primary { color: #FFFFFF !important; background: linear-gradient(135deg, #2563EB, #1D4ED8); box-shadow: 0 10px 22px rgba(37,99,235,0.22); }
        .hero-secondary { color: #1D4ED8 !important; background: #FFFFFF; border: 1px solid #BFDBFE; }
        .hero-grid { position: relative; z-index: 1; display: grid; grid-template-columns: minmax(0, 1.45fr) 330px; gap: 2rem; align-items: center; }
        .hero-panel {
            background: rgba(255,255,255,0.9); border: 1px solid #DBEAFE; border-radius: 22px; padding: 0.95rem;
            box-shadow: 0 14px 32px rgba(37,99,235,0.1); backdrop-filter: blur(8px);
        }
        .hero-panel-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.9rem; }
        .hero-panel-title { color: #0F172A; font-weight: 850; }
        .hero-panel-pill { color: #1D4ED8; background: #DBEAFE; border-radius: 999px; padding: 0.22rem 0.58rem; font-size: 0.74rem; font-weight: 800; }
        .hero-mini-card {
            background: #FFFFFF; border: 1px solid #E0E7FF; border-radius: 16px; padding: 0.82rem 0.9rem;
            margin-top: 0.62rem; box-shadow: 0 8px 18px rgba(15,23,42,0.045);
        }
        .hero-mini-label { color: #64748B; font-size: 0.78rem; font-weight: 750; }
        .hero-mini-value { color: #0F172A; font-size: 1.02rem; font-weight: 850; margin-top: 0.2rem; }
        .hero-bar { height: 8px; border-radius: 999px; background: #E5E7EB; overflow: hidden; margin-top: 0.58rem; }
        .hero-bar span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #60A5FA, #2563EB); }
        .problem-card {
            background: #FFFFFF; border: 1px solid #E0E7FF; border-radius: 18px; padding: 1.15rem 1.25rem;
            box-shadow: var(--small-shadow); margin: 1.2rem 0 1.45rem;
        }
        .feature-strip {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.7rem; margin: 0.65rem 0 0.8rem;
        }
        .feature-pill-card {
            background: rgba(255,255,255,0.78); border: 1px solid #E0E7FF; border-radius: 16px;
            padding: 0.72rem 0.85rem; color: #334155; font-size: 0.86rem; font-weight: 720;
        }
        .one-line-value {
            color: #475569; font-size: 0.9rem; line-height: 1.65; margin: 0.25rem 0 0.75rem;
        }
        .problem-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.9rem; }
        .problem-block {
            background: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 16px; padding: 0.95rem 1rem;
            color: #374151; line-height: 1.72;
        }
        .problem-block strong { color: #0F172A; display: block; margin-bottom: 0.35rem; }
        .info-strip {
            margin-top: 0.95rem; padding: 0.72rem 0.9rem; border-radius: 14px;
            background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; font-size: 0.86rem;
        }
        .workbench-card {
            background: #FFFFFF; border: 1px solid #E0E7FF; border-radius: 22px; padding: 1.25rem;
            box-shadow: 0 14px 34px rgba(15,23,42,0.06); margin: 0.65rem 0 1.7rem;
        }
        .workbench-head { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; margin-bottom: 1rem; }
        .workbench-kicker { color: #1D4ED8; font-size: 0.78rem; font-weight: 850; letter-spacing: 0.08em; }
        .workbench-title { color: #0F172A; font-size: 1.25rem; font-weight: 850; margin-top: 0.2rem; }
        .workbench-tip { color: #64748B; font-size: 0.86rem; line-height: 1.65; max-width: 360px; text-align: right; }
        .form-action-note { color: #64748B; font-size: 0.84rem; padding-top: 0.55rem; line-height: 1.55; }
        .product-grid {
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin: 1rem 0 1.5rem;
        }
        .product-card {
            background: var(--panel); border: 1px solid #E0E7FF; border-radius: 18px;
            padding: 1.05rem 1.15rem; color: var(--ink); min-height: 112px; box-shadow: var(--small-shadow);
        }
        .product-card-label {
            color: var(--blue-dark); font-size: 0.78rem; font-weight: 800; letter-spacing: 0.04em;
            margin-bottom: 0.45rem;
        }
        .product-card-text { color: #374151; font-size: 0.91rem; line-height: 1.68; }
        .section-label { font-size: 1.16rem; font-weight: 800; margin: 0.4rem 0 0.22rem; color: #0F172A; }
        .section-note { color: var(--muted); font-size: 0.9rem; margin-bottom: 1rem; }
        .info-card {
            background: var(--panel); border: 1px solid #E0E7FF; border-radius: 18px;
            padding: 1rem 1.1rem; min-height: 100px; color: var(--ink); box-shadow: var(--small-shadow);
        }
        .info-card strong { color: var(--ink); }
        div[data-testid="stForm"] { border: 0; padding: 0; background: transparent; box-shadow: none; }
        .tag-wrap { display: flex; flex-wrap: wrap; gap: 0.55rem; margin: 0.6rem 0 1rem; }
        .tag {
            display: inline-block; color: var(--blue-dark); background: #DBEAFE; border: 1px solid #BFDBFE;
            border-radius: 999px; padding: 0.4rem 0.78rem; font-size: 0.86rem; font-weight: 750;
        }
        .tag-success { color: #166534; background: #DCFCE7; border-color: #BBF7D0; }
        .list-card {
            display: flex; gap: 0.9rem; align-items: flex-start; background: var(--panel);
            border: 1px solid #E5E7EB; border-left: 4px solid var(--blue); border-radius: 16px;
            padding: 0.92rem 1rem; margin: 0.65rem 0; line-height: 1.68; color: var(--ink);
            box-shadow: 0 4px 14px rgba(15,23,42,0.04);
        }
        .list-card span:not(.list-index) { color: var(--ink); }
        .list-card.positive { border-left-color: #16A34A; }
        .list-card.warning { border-left-color: #F97316; background: #FFFBF5; }
        .list-index { color: var(--blue); font-size: 0.75rem; font-weight: 800; padding-top: 0.22rem; }
        .copy-card {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%); border: 1px solid #DBEAFE; border-radius: 18px;
            padding: 1.15rem 1.25rem; line-height: 1.85; margin: 0.65rem 0; color: var(--ink); box-shadow: var(--small-shadow);
        }
        .summary-card {
            background: var(--panel); border: 1px solid #E0E7FF; border-radius: 18px;
            padding: 1.1rem 1.2rem; color: var(--ink); height: 100%; box-shadow: var(--small-shadow);
        }
        .summary-card.risk-summary { background: #FFFBF5; border-color: #FED7AA; }
        .summary-title { color: #0F172A; font-weight: 800; margin-bottom: 0.45rem; }
        .summary-text { color: #374151; line-height: 1.75; font-size: 0.91rem; }
        .risk-card {
            background: #fffaf2; border: 1px solid #f1dfbd; border-left: 3px solid #d38b32;
            border-radius: 10px; padding: 0.8rem 1rem; margin: 0.55rem 0; color: #4b3621;
        }
        .diagnosis-card {
            background: var(--panel); border: 1px solid #E0E7FF; border-radius: 18px;
            padding: 1.08rem; margin-bottom: 0.8rem; color: var(--ink); box-shadow: var(--small-shadow);
        }
        .diagnosis-head { display: flex; justify-content: space-between; font-weight: 800; margin-bottom: 0.5rem; }
        .diagnosis-score { color: var(--blue); }
        .diagnosis-note { color: #4B5563; font-size: 0.88rem; line-height: 1.62; margin-top: 0.55rem; }
        .progress-shell {
            width: 100%; height: 9px; background: #E5E7EB; border-radius: 999px; overflow: hidden; margin: 0.55rem 0;
        }
        .progress-bar {
            height: 100%; background: linear-gradient(90deg, #60A5FA, #2563EB); border-radius: 999px;
        }
        .metric-card {
            background: var(--panel); border: 1px solid #E0E7FF; border-radius: 20px;
            padding: 1.1rem 1.2rem; min-height: 128px; box-shadow: var(--small-shadow);
        }
        .metric-title { color: #64748B; font-size: 0.84rem; font-weight: 750; margin-bottom: 0.55rem; }
        .metric-value { color: #0F172A; font-size: 1.72rem; line-height: 1.15; font-weight: 850; letter-spacing: -0.02em; }
        .metric-caption { color: #6B7280; font-size: 0.82rem; margin-top: 0.55rem; }
        .metric-highlight { border-color: #BFDBFE; background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 100%); }
        .metric-highlight .metric-value { color: var(--blue); font-size: 2.08rem; }
        .compare-card {
            border-radius: 18px; padding: 1rem 1.1rem; min-height: 150px; line-height: 1.75;
            border: 1px solid #E5E7EB; box-shadow: 0 5px 16px rgba(15,23,42,0.04); color: var(--ink);
        }
        .compare-card.original { background: #F8FAFC; border-color: #E2E8F0; }
        .compare-card.optimized { background: #F0FDF4; border-color: #BBF7D0; }
        .compare-title { font-weight: 800; color: #334155; margin-bottom: 0.45rem; }
        .rewrite-card, .report-card {
            background: var(--panel); border: 1px solid #E0E7FF; border-radius: 20px;
            padding: 1rem; box-shadow: var(--small-shadow);
        }
        .markdown-report {
            white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            background: #FFFFFF; color: #111827; border: 1px solid #E0E7FF; border-radius: 18px;
            padding: 1.25rem; line-height: 1.72; box-shadow: var(--small-shadow); overflow-x: auto;
        }
        .roadmap-section { margin-top: 1.8rem; }
        .roadmap-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.85rem; }
        .roadmap-card {
            background: #FFFFFF; border: 1px solid #E0E7FF; border-radius: 18px; padding: 1rem;
            box-shadow: var(--small-shadow); min-height: 130px;
        }
        .roadmap-version { color: var(--blue-dark); font-weight: 850; margin-bottom: 0.5rem; }
        .roadmap-text { color: #4B5563; font-size: 0.88rem; line-height: 1.62; }
        .score-caption { color: #4b5563; font-size: 0.82rem; }
        div[data-testid="stDataFrame"] {
            border: 1px solid #E0E7FF; border-radius: 16px; overflow: hidden; box-shadow: var(--small-shadow);
            background: #FFFFFF;
        }
        div[data-testid="stMetric"] {
            background: #ffffff; border: 1px solid #e6eaf1; padding: 1rem 1.1rem;
            border-radius: 14px; box-shadow: 0 4px 16px rgba(32, 55, 91, 0.04);
        }
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricValue"] { color: #1f2937; }
        div[data-testid="stMetricValue"] { color: #1d4f91; }

        /* 输入控件：覆盖浅色与深色主题，确保内容始终清晰。 */
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            background-color: #ffffff !important;
            color: #111827 !important;
            caret-color: #111827 !important;
            border-color: #d1d5db !important;
            border-radius: 10px;
            -webkit-text-fill-color: #111827 !important;
            opacity: 1 !important;
        }
        div[data-testid="stTextArea"] textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder {
            color: #6b7280 !important;
            -webkit-text-fill-color: #6b7280 !important;
            opacity: 1 !important;
        }
        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stTextInput"] input:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 1px #2563eb !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #111827 !important;
            border-color: #d1d5db !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
            color: #111827 !important;
            fill: #374151 !important;
            -webkit-text-fill-color: #111827 !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #ffffff !important;
        }
        li[role="option"],
        li[role="option"] span {
            background-color: #ffffff !important;
            color: #111827 !important;
        }
        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {
            background-color: #eff6ff !important;
            color: #111827 !important;
        }
        div[data-testid="stTextArea"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label {
            color: #1f2937 !important;
        }
        .stButton > button, .stFormSubmitButton > button {
            width: 100%; border-radius: 14px; border: 0; background: linear-gradient(135deg, #2563EB, #1D4ED8);
            color: white; font-weight: 800; min-height: 3.05rem; box-shadow: 0 10px 22px rgba(37, 99, 235, 0.24);
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background: linear-gradient(135deg, #1D4ED8, #1E40AF); color: white; border: 0;
        }
        div[data-testid="stTabs"] button { font-weight: 750; color: #475569; }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--blue-dark); background: #EFF6FF; border-radius: 999px;
        }
        div[data-testid="stProgress"] > div > div > div { background-color: var(--blue); }
        .footer-note { text-align: center; color: #8a94a5; font-size: 0.8rem; margin-top: 2rem; }
        @media (max-width: 700px) {
            .hero { padding: 1.5rem; }
            .hero h1 { font-size: 1.75rem; }
            .hero-grid { grid-template-columns: 1fr; }
            .top-nav { position: relative; top: auto; height: auto; flex-direction: column; align-items: flex-start; padding: 0.9rem; }
            .top-links { flex-wrap: wrap; gap: 0.75rem; }
            .top-actions { width: 100%; justify-content: space-between; }
            .feature-strip { grid-template-columns: 1fr 1fr; }
            .product-grid { grid-template-columns: 1fr; }
            .problem-grid { grid-template-columns: 1fr; }
            .workbench-head { flex-direction: column; }
            .workbench-tip { text-align: left; }
            .roadmap-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_result(result):
    score_info = result["score_info"]
    st.markdown("---")
    st.markdown('<div class="section-label">分析结果概览</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">基于 JD 关键词覆盖、能力信号、数据表达和简历完整度综合计算。</div>',
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(4)
    with metric_columns[0]:
        render_metric_card("简历匹配度", f'{score_info["score"]} 分', "满分 100", highlight=True)
    with metric_columns[1]:
        render_metric_card(
            "关键词命中",
            f'{len(score_info["matched_keywords"])} / {len(result["keywords"])}',
            "JD 核心词",
        )
    with metric_columns[2]:
        render_metric_card(
            "能力覆盖",
            f'{score_info["capability_coverage"]} / {len(result["capabilities"])}',
            "核心能力",
        )
    with metric_columns[3]:
        render_metric_card("数据化表达", score_info["data_status"], f'{len(score_info["numbers"])} 处数字')

    st.subheader("决策摘要")
    summary_left, summary_middle, summary_right = st.columns(3)
    with summary_left:
        st.markdown(
            f'<div class="summary-card"><div class="summary-title">综合评价</div>'
            f'<div class="summary-text">{score_info["evaluation"]}</div></div>',
            unsafe_allow_html=True,
        )
    with summary_middle:
        priority_items = "".join(f"<li>{item}</li>" for item in result["suggestions"][:3])
        st.markdown(
            '<div class="summary-card"><div class="summary-title">优先优化建议</div>'
            f'<div class="summary-text"><ol>{priority_items}</ol></div></div>',
            unsafe_allow_html=True,
        )
    with summary_right:
        risk_items = "".join(f"<li>{item}</li>" for item in result["risk_tips"])
        st.markdown(
            '<div class="summary-card risk-summary"><div class="summary-title">简历风险提示</div>'
            f'<div class="summary-text"><ul>{risk_items}</ul></div></div>',
            unsafe_allow_html=True,
        )

    tab_match, tab_diagnosis, tab_rewrite, tab_report, tab_job_search = st.tabs(
        ["岗位匹配", "问题诊断", "改写对比", "分析报告", "求职展示"]
    )

    with tab_match:
        st.markdown('<div id="job-match-section"></div>', unsafe_allow_html=True)
        st.subheader("JD 核心关键词")
        render_tags(result["keywords"])
        if score_info["matched_keywords"]:
            st.caption("其中，以下关键词已在简历中形成匹配：")
            render_tags(score_info["matched_keywords"], "success")

        st.subheader("岗位核心能力要求")
        capability_descriptions = {
            "数据分析能力": "能够建立指标意识，通过数据观察问题并支持运营或产品决策。",
            "用户理解能力": "能够识别目标用户、核心场景和真实需求，并转化为执行方案。",
            "产品思维": "能够从问题、需求、方案到验证形成完整思考链路。",
            "内容策划能力": "能够围绕传播目标完成选题、内容组织、生产和效果优化。",
            "AI 工具应用能力": "能够选择合适的 AI 工具提效，并对生成结果进行判断和校验。",
            "项目推进能力": "能够拆解任务、协调资源、跟进节点并推动结果落地。",
            "增长与转化意识": "能够关注用户路径与业务指标，持续寻找增长和转化机会。",
            "市场与品牌洞察": "能够理解市场环境、竞品策略和品牌传播目标。",
            "沟通协作能力": "能够与不同角色对齐信息、明确分工并解决协作问题。",
        }
        for capability in result["capabilities"]:
            st.markdown(
                f'<div class="info-card"><strong>{capability}</strong><br>'
                f'<span class="score-caption">{capability_descriptions[capability]}</span></div>',
                unsafe_allow_html=True,
            )
            st.write("")

        st.subheader("岗位关键词命中表")
        st.caption("优先处理“重要程度高且未命中”的关键词，但只补充真实发生过的经历。")
        st.dataframe(result["keyword_table"], use_container_width=True, hide_index=True)

    with tab_diagnosis:
        st.markdown('<div id="diagnosis-section"></div>', unsafe_allow_html=True)
        st.subheader("简历问题诊断")
        st.caption("六个维度用于定位当前简历的主要短板，分数仅作为修改优先级参考。")
        diagnostic_columns = st.columns(2)
        for index, item in enumerate(result["diagnostics"]):
            with diagnostic_columns[index % 2]:
                st.markdown(
                    f'<div class="diagnosis-card"><div class="diagnosis-head">'
                    f'<span>{item["诊断维度"]}</span><span class="diagnosis-score">{item["评分"]} 分</span></div>'
                    f'<div class="progress-shell"><div class="progress-bar" style="width:{item["评分"]}%;"></div></div>'
                    f'<div class="diagnosis-note">{item["诊断结论"]}</div></div>',
                    unsafe_allow_html=True,
                )

        left, right = st.columns(2)
        with left:
            st.subheader("我的简历优势")
            render_numbered_cards(result["strengths"], "positive")
        with right:
            st.subheader("我的简历不足")
            render_numbered_cards(result["weaknesses"], "warning")

        with st.expander("查看评分构成与扣分项"):
            score_table = {
                "评分维度": ["JD 关键词覆盖", "能力信号", "数据化表达", "简历完整度"],
                "当前得分": [
                    score_info["keyword_score"],
                    score_info["ability_score"],
                    score_info["data_score"],
                    score_info["completeness_score"],
                ],
                "该项上限": [55, 20, 15, 10],
            }
            st.dataframe(score_table, use_container_width=True, hide_index=True)
            if score_info["penalties"]:
                st.caption("扣分或限分原因：" + "、".join(score_info["penalties"]))
            else:
                st.caption("当前未触发额外扣分项。")

    with tab_rewrite:
        st.markdown('<div id="rewrite-section"></div>', unsafe_allow_html=True)
        st.subheader("简历改写前后对比")
        st.caption("优化版本仅重组原始信息，并使用克制的结果表达，不虚构业务数据。")
        for index, comparison in enumerate(result["comparison"], 1):
            st.markdown(f"**对比 {index}**")
            original_column, optimized_column = st.columns(2)
            with original_column:
                st.markdown(
                    f'<div class="compare-card original"><div class="compare-title">原始表达</div>{html.escape(comparison["原始表达"])}</div>',
                    unsafe_allow_html=True,
                )
            with optimized_column:
                st.markdown(
                    f'<div class="compare-card optimized"><div class="compare-title">优化表达</div>{html.escape(comparison["优化表达"])}</div>',
                    unsafe_allow_html=True,
                )

        st.subheader("完整经历改写版本")
        rewrite_text = "\n".join(f"• {line}" for line in result["rewrite"])
        st.markdown('<div class="rewrite-card">', unsafe_allow_html=True)
        st.text_area("可直接编辑和复制", value=rewrite_text, height=250)
        st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("全部修改建议")
        render_numbered_cards(result["suggestions"])

    with tab_report:
        st.markdown('<div id="report-section"></div>', unsafe_allow_html=True)
        st.subheader("分析报告汇总")
        st.caption("报告为 Markdown 格式，可直接下载后保存到作品集资料中。")
        st.download_button(
            "下载 Markdown 分析报告",
            data=result["markdown_report"],
            file_name="AI简历优化分析报告.md",
            mime="text/markdown",
            use_container_width=True,
        )
        with st.expander("预览完整报告", expanded=True):
            st.markdown(
                f'<pre class="markdown-report">{html.escape(result["markdown_report"])}</pre>',
                unsafe_allow_html=True,
            )

    with tab_job_search:
        st.markdown('<div id="job-search-section"></div>', unsafe_allow_html=True)
        st.subheader("Boss 直聘打招呼语")
        st.markdown(f'<div class="copy-card">{result["greeting"]}</div>', unsafe_allow_html=True)
        st.caption(f'当前约 {len(result["greeting"])} 字，可按具体公司和岗位名称微调。')

        st.subheader("面试可讲项目亮点")
        render_numbered_cards(result["interview_highlights"], "positive")

    st.markdown("---")
    st.subheader("这个项目如何写进简历")
    st.caption("适合用于作品集或简历项目经历，可结合你的实际分工继续调整。")
    st.markdown(
        f'<div class="copy-card">{result["project_resume_description"]}</div>',
        unsafe_allow_html=True,
    )


def main():
    inject_styles()
    render_top_nav()
    st.markdown(
        """
        <div id="hero-section"></div>
        <div class="hero">
            <div class="hero-grid">
                <div>
                    <div class="hero-kicker">AI 产品 Demo · Version 2.0</div>
                    <h1>AI 简历优化助手</h1>
                    <div class="hero-subtitle">面向中文实习求职者的 JD-简历匹配诊断工具</div>
                    <p>输入岗位 JD 与个人简历，快速生成匹配评分、关键词命中、六维诊断和修改建议。</p>
                    <div class="hero-actions">
                        <a class="hero-primary" href="#analysis-section">开始分析</a>
                        <a class="hero-secondary" href="#features-section">查看示例</a>
                    </div>
                    <div class="hero-badges">
                        <span class="hero-badge">本地运行</span>
                        <span class="hero-badge">无需 API Key</span>
                        <span class="hero-badge">不上传个人信息</span>
                    </div>
                </div>
                <div class="hero-panel">
                    <div class="hero-panel-top">
                        <div class="hero-panel-title">AI 分析面板</div>
                        <div class="hero-panel-pill">Local Demo</div>
                    </div>
                    <div class="hero-mini-card">
                        <div class="hero-mini-label">JD 关键词识别</div>
                        <div class="hero-mini-value">数据分析 · AIGC · 用户需求</div>
                        <div class="hero-bar"><span style="width: 86%;"></span></div>
                    </div>
                    <div class="hero-mini-card">
                        <div class="hero-mini-label">匹配度评分</div>
                        <div class="hero-mini-value">0-100 可解释模型</div>
                        <div class="hero-bar"><span style="width: 72%;"></span></div>
                    </div>
                    <div class="hero-mini-card">
                        <div class="hero-mini-label">六维诊断</div>
                        <div class="hero-mini-value">数据 · 结果 · 产品思维</div>
                        <div class="hero-bar"><span style="width: 78%;"></span></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div id="features-section"></div>
        <div class="one-line-value">从岗位 JD 到简历诊断，一站式完成匹配分析、问题定位与表达优化。</div>
        <div class="feature-strip">
            <div class="feature-pill-card">匹配度评分</div>
            <div class="feature-pill-card">关键词命中</div>
            <div class="feature-pill-card">六维诊断</div>
            <div class="feature-pill-card">报告导出</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div id="workflow-section"></div>
        <div id="analysis-section"></div>
        <div class="workbench-card">
            <div class="workbench-head">
                <div>
                    <div class="workbench-kicker">AI ANALYSIS WORKBENCH</div>
                    <div class="workbench-title">开始一次 JD-简历匹配分析</div>
                </div>
                <div class="workbench-tip">建议粘贴完整 JD 与至少一段真实项目经历。输入内容仅在本地页面中用于规则分析。</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("resume_analysis_form"):
        left, right = st.columns(2)
        with left:
            jd_text = st.text_area(
                "岗位 JD",
                height=260,
                placeholder="请粘贴岗位职责、任职要求等完整 JD 内容……",
            )
        with right:
            resume_text = st.text_area(
                "个人简历",
                height=260,
                placeholder="请粘贴教育背景、实习经历、项目经历、技能等简历内容……",
            )

        role_column, note_column, button_column = st.columns([1.5, 1.2, 1])
        with role_column:
            target_role = st.selectbox(
                "目标岗位类型",
                ["产品运营", "AI 产品助理", "内容运营", "AIGC 运营", "新媒体运营", "市场/品牌运营"],
            )
        with note_column:
            st.markdown(
                '<div class="form-action-note">点击后将生成匹配度、关键词命中、六维诊断、改写对比和报告。</div>',
                unsafe_allow_html=True,
            )
        with button_column:
            st.write("")
            submitted = st.form_submit_button("开始分析", type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not jd_text.strip() or not resume_text.strip():
            st.error("请先填写岗位 JD 和个人简历，再开始分析。")
        elif len(normalize_text(jd_text)) < 50:
            st.warning("岗位 JD 内容较短，建议补充完整的岗位职责和任职要求，以获得更准确的分析。")
        elif len(normalize_text(resume_text)) < 50:
            st.warning("简历内容较短，建议至少补充一段完整的实习或项目经历。")
        else:
            with st.spinner("正在拆解岗位要求并诊断简历……"):
                st.session_state["analysis_result"] = analyze_resume(
                    jd_text, resume_text, target_role
                )
                st.session_state["analysis_signature"] = (
                    jd_text,
                    resume_text,
                    target_role,
                )

    if "analysis_result" in st.session_state:
        render_result(st.session_state["analysis_result"])

    render_iteration_roadmap()

    st.markdown(
        '<div class="footer-note">AI 简历优化助手 V2 · 本地规则分析 Demo · 请勿输入身份证号等敏感信息</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
