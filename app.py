"""
原神圣遗物期望计算器 — Streamlit 交互界面
==========================================
自由选择各部位主词条，通过概率公式计算刷出一套目标圣遗物的期望次数。

运行方式:
  streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from simulator import (
    TargetBuild,
    theoretical_expected_runs,
)
from artifact_data import (
    SLOT_FLOWER, SLOT_PLUME, SLOT_SANDS, SLOT_GOBLET, SLOT_CIRCLET,
    ALL_SLOTS, SLOT_NAMES_CN, MAIN_STAT_NAMES_CN,
    MAIN_STAT_DISTRIBUTION,
    EXPECTED_DROPS_PER_RUN, TARGET_SET_PROB, SLOT_PROB,
)

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="原神圣遗物期望计算器",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 自定义 CSS
# ============================================================
st.markdown("""
<style>
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .highlight-box {
        background: linear-gradient(135deg, #667eea18, #764ba218);
        border-left: 3px solid #667eea;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 辅助函数：构建主词条选择器
# ============================================================

def build_stat_options(slot: str):
    """
    根据圣遗物部位，返回 (显示名 → 内部key) 的选项映射。
    按概率从高到低排列。
    """
    dist = MAIN_STAT_DISTRIBUTION[slot]
    # 按概率降序排列
    sorted_stats = sorted(dist.items(), key=lambda x: -x[1])
    options = {}
    for key, prob in sorted_stats:
        label = MAIN_STAT_NAMES_CN.get(key, key)
        # 非固定词条显示概率
        if prob < 1.0:
            label = f"{label}　({prob*100:.1f}%)"
        options[label] = key
    return options


# ============================================================
# 侧边栏 — 主词条选择
# ============================================================

with st.sidebar:
    st.markdown("## 🎲 圣遗物期望计算")
    st.markdown("---")

    st.markdown("### 选择目标主词条")
    st.caption("选择你想要的每个部位的主词条，查看刷取难度。")

    # 沙漏
    st.markdown("#### ⏳ 时之沙（沙漏）")
    sands_options = build_stat_options(SLOT_SANDS)
    sands_choice = st.selectbox(
        "沙漏主词条",
        list(sands_options.keys()),
        label_visibility="collapsed",
    )
    sands_key = sands_options[sands_choice]

    # 杯子
    st.markdown("#### 🍷 空之杯（杯子）")
    goblet_options = build_stat_options(SLOT_GOBLET)
    goblet_choice = st.selectbox(
        "杯子主词条",
        list(goblet_options.keys()),
        label_visibility="collapsed",
    )
    goblet_key = goblet_options[goblet_choice]

    # 头冠
    st.markdown("#### 👑 理之冠（头冠）")
    circlet_options = build_stat_options(SLOT_CIRCLET)
    circlet_choice = st.selectbox(
        "头冠主词条",
        list(circlet_options.keys()),
        label_visibility="collapsed",
    )
    circlet_key = circlet_options[circlet_choice]

    st.markdown("---")
    st.caption("📖 数据来源: KQM / Genshin Wiki / 游戏解包")


# ============================================================
# 主页面
# ============================================================
st.markdown('<p class="main-title">原神圣遗物期望计算器</p>', unsafe_allow_html=True)
st.markdown("自由选择各部位目标主词条，基于实际游戏概率计算刷取期望。")

# ============================================================
# 数据速览
# ============================================================
st.markdown("---")
st.markdown("### 📊 数据速览")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("每次副本期望", f"{EXPECTED_DROPS_PER_RUN:.1f} 个五星", help="20树脂")
with col2:
    st.metric("目标套装概率", "50%", help="两个套装各半")
with col3:
    st.metric("部位均匀分布", "20%", help="五个部位各20%")
with col4:
    # 显示当前杯子概率
    goblet_prob = MAIN_STAT_DISTRIBUTION[SLOT_GOBLET].get(goblet_key, 0)
    st.metric("杯子目标概率", f"{goblet_prob*100:.1f}%", help="特定主词条在杯子中的出现概率")

# ============================================================
# 当前目标展示
# ============================================================
st.markdown("### 🎯 当前目标")

cols = st.columns(5)
slot_info = [
    ("🌸 生之花", "生命值", 1.0),
    ("🪶 死之羽", "攻击力", 1.0),
    ("⏳ 时之沙", MAIN_STAT_NAMES_CN.get(sands_key, sands_key),
     MAIN_STAT_DISTRIBUTION[SLOT_SANDS].get(sands_key, 0)),
    ("🍷 空之杯", MAIN_STAT_NAMES_CN.get(goblet_key, goblet_key),
     MAIN_STAT_DISTRIBUTION[SLOT_GOBLET].get(goblet_key, 0)),
    ("👑 理之冠", MAIN_STAT_NAMES_CN.get(circlet_key, circlet_key),
     MAIN_STAT_DISTRIBUTION[SLOT_CIRCLET].get(circlet_key, 0)),
]

for i, (slot_name, stat_name, prob) in enumerate(slot_info):
    with cols[i]:
        st.markdown(f"**{slot_name}**")
        st.caption(f"{stat_name}")
        if prob >= 1.0:
            st.caption("固定")
        else:
            st.caption(f"概率: {prob*100:.1f}%")

# ============================================================
# 计算按钮
# ============================================================
st.markdown("---")

calc_col, _ = st.columns([1, 3])
with calc_col:
    calculate = st.button("🚀 开始计算", type="primary", use_container_width=True)

if calculate:
    target = TargetBuild(
        sands_main=sands_key,
        goblet_main=goblet_key,
        circlet_main=circlet_key,
    )

    with st.spinner("正在计算理论期望..."):
        results = theoretical_expected_runs(target)

    # ============================================================
    # 结果展示
    # ============================================================
    st.markdown("---")
    st.markdown("### 📐 计算结果")

    # 各部位详细数据表
    st.markdown("#### 各部位期望明细")
    piece_data = []
    for slot in ALL_SLOTS:
        p = results["piece_probabilities"][slot]
        er = results["single_expected_runs"][slot]
        ed = er * 20 / 180
        piece_data.append({
            "部位": SLOT_NAMES_CN[slot],
            "综合概率": f"{p*100:.3f}%",
            "期望副本次数": f"{er:,.0f} 次",
            "期望体力": f"{er*20:,.0f} 树脂",
            "期望天数": f"{ed:.1f} 天" if er < float('inf') else "∞",
        })
    st.dataframe(piece_data, use_container_width=True, hide_index=True)

    # 全套期望 — 高亮卡片
    st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
    st.markdown("#### ⭑ 全套期望")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("期望副本次数", f"{results['total_expected_runs']:,.0f} 次")
    with c2:
        st.metric("期望体力消耗", f"{results['total_expected_resin']:,.0f} 树脂")
    with c3:
        days = results['total_expected_resin'] / 180
        st.metric("期望天数（自回体）", f"{days:.1f} 天",
                  help="按每天180自回树脂计算，不含脆弱树脂")

    st.markdown(f"**瓶颈部位:** {results['hardest_piece_name']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 瓶颈分析
    st.markdown("#### 💡 分析与建议")
    hardest = results["hardest_piece"]

    if hardest == SLOT_GOBLET:
        st.info(
            f"杯子是最大的瓶颈——特定元素伤害加成的杯子只有 "
            f"**{MAIN_STAT_DISTRIBUTION[SLOT_GOBLET].get(goblet_key, 0)*100:.1f}%** 的出现概率。\n\n"
            f"💡 **省肝技巧:** 很多玩家选择用「散件杯子」——即杯子不要求是目标套装，"
            f"只要主词条对就行，另外四个部位凑齐四件套。这样瓶颈就转移到头冠或沙漏上，"
            f"大幅降低总期望次数。"
        )
    elif hardest == SLOT_CIRCLET:
        circlet_prob = MAIN_STAT_DISTRIBUTION[SLOT_CIRCLET].get(circlet_key, 0)
        st.info(
            f"头冠是当前的瓶颈部位，目标主词条概率为 **{circlet_prob*100:.1f}%**。\n\n"
            f"如果杯子已经放宽为散件，头冠就是新的瓶颈。双暴头（暴击率/暴击伤害）各 "
            f"10%，是头冠中最稀有的词条。"
        )
    elif hardest == SLOT_SANDS:
        sand_prob = MAIN_STAT_DISTRIBUTION[SLOT_SANDS].get(sands_key, 0)
        st.info(
            f"沙漏是当前的瓶颈部位，目标主词条概率为 **{sand_prob*100:.1f}%**。\n\n"
            f"大攻击/大生命/大防御各约 26.7%，充能和精通各 10%。如果沙漏要充能或精通，"
            f"会成为瓶颈。"
        )
    else:
        st.info(
            f"当前瓶颈在 **{results['hardest_piece_name']}**，不过花和羽毛主词条固定，"
            f"一般不构成瓶颈。建议检查沙漏/杯子/头冠的目标词条选择。"
        )

else:
    # 空状态
    st.info("👈 在左侧选择各部位目标主词条，然后点击「开始计算」查看期望结果。")

# ============================================================
# 页脚
# ============================================================
st.markdown("---")
st.caption("🎲 数据来源: KQM · Genshin Fandom Wiki · 游戏解包 | 仅供学习参考")
