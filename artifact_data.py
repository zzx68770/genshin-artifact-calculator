"""
原神圣遗物概率数据
=====================
数据来源：
  - KeqingMains (KQM) Artifacts Guide: https://keqingmains.com/misc/artifacts/
  - Genshin Impact Fandom Wiki - Artifact/Distribution
  - 解包数据 (datamined game files)
  - 社区验证数据

所有概率权重基于游戏文件解包数据，经社区大量验证。
本模块作为爬虫的备选方案——当Wiki无法访问时使用内嵌数据。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import json

# ============================================================
# 圣遗物部位定义
# ============================================================
SLOT_FLOWER = "flower"      # 生之花
SLOT_PLUME = "plume"       # 死之羽
SLOT_SANDS = "sands"       # 时之沙
SLOT_GOBLET = "goblet"     # 空之杯
SLOT_CIRCLET = "circlet"   # 理之冠

ALL_SLOTS = [SLOT_FLOWER, SLOT_PLUME, SLOT_SANDS, SLOT_GOBLET, SLOT_CIRCLET]

SLOT_NAMES_CN = {
    SLOT_FLOWER: "生之花",
    SLOT_PLUME: "死之羽",
    SLOT_SANDS: "时之沙",
    SLOT_GOBLET: "空之杯",
    SLOT_CIRCLET: "理之冠",
}

# ============================================================
# 主词条定义
# ============================================================

# --- 花（生之花）- 固定生命值 ---
FLOWER_MAIN_STATS = {
    "flat_hp": 1.0,
}

# --- 羽毛（死之羽）- 固定攻击力 ---
PLUME_MAIN_STATS = {
    "flat_atk": 1.0,
}

# --- 沙漏（时之沙）- 五种可能 ---
# 权重来自 KQM / 解包数据
SANDS_MAIN_STATS = {
    "hp_percent":      0.2668,   # 生命值%
    "atk_percent":     0.2666,   # 攻击力%
    "def_percent":     0.2666,   # 防御力%
    "energy_recharge": 0.1000,   # 元素充能效率
    "elemental_mastery": 0.1000, # 元素精通
}

# --- 杯子（空之杯）- 十二种可能 ---
# 权重来自 KQM / 解包数据
GOBLET_MAIN_STATS = {
    "hp_percent":          0.1925,  # 生命值%
    "atk_percent":         0.1925,  # 攻击力%
    "def_percent":         0.1900,  # 防御力%
    "elemental_mastery":   0.0250,  # 元素精通
    "physical_dmg":        0.0500,  # 物理伤害加成
    "anemo_dmg":           0.0500,  # 风元素伤害加成
    "cryo_dmg":            0.0500,  # 冰元素伤害加成
    "dendro_dmg":          0.0500,  # 草元素伤害加成
    "electro_dmg":         0.0500,  # 雷元素伤害加成
    "geo_dmg":             0.0500,  # 岩元素伤害加成
    "hydro_dmg":           0.0500,  # 水元素伤害加成
    "pyro_dmg":            0.0500,  # 火元素伤害加成
}

# --- 头（理之冠）- 七种可能 ---
CIRCLET_MAIN_STATS = {
    "hp_percent":       0.22,  # 生命值%
    "atk_percent":      0.22,  # 攻击力%
    "def_percent":      0.22,  # 防御力%
    "crit_rate":        0.10,  # 暴击率
    "crit_dmg":         0.10,  # 暴击伤害
    "healing_bonus":    0.10,  # 治疗加成
    "elemental_mastery": 0.04, # 元素精通
}

# 主词条中文名
MAIN_STAT_NAMES_CN = {
    "flat_hp":           "生命值",
    "flat_atk":          "攻击力",
    "hp_percent":        "生命值%",
    "atk_percent":       "攻击力%",
    "def_percent":       "防御力%",
    "elemental_mastery": "元素精通",
    "energy_recharge":   "元素充能效率",
    "physical_dmg":      "物理伤害加成",
    "anemo_dmg":         "风元素伤害加成",
    "cryo_dmg":          "冰元素伤害加成",
    "dendro_dmg":        "草元素伤害加成",
    "electro_dmg":       "雷元素伤害加成",
    "geo_dmg":           "岩元素伤害加成",
    "hydro_dmg":         "水元素伤害加成",
    "pyro_dmg":          "火元素伤害加成",
    "crit_rate":         "暴击率",
    "crit_dmg":          "暴击伤害",
    "healing_bonus":     "治疗加成",
}

# 所有部位的主词条分布
MAIN_STAT_DISTRIBUTION = {
    SLOT_FLOWER:  FLOWER_MAIN_STATS,
    SLOT_PLUME:   PLUME_MAIN_STATS,
    SLOT_SANDS:   SANDS_MAIN_STATS,
    SLOT_GOBLET:  GOBLET_MAIN_STATS,
    SLOT_CIRCLET: CIRCLET_MAIN_STATS,
}

# ============================================================
# 副词条定义与权重
# ============================================================

# 副词条权重（来自游戏解包数据）
# 数据来源: Genshin Impact Fandom Wiki - Artifact/Distribution
# 解包权重: 总权重 = 1000
SUBSTAT_WEIGHTS = {
    "flat_hp":           150,   # 小生命
    "flat_atk":          150,   # 小攻击
    "flat_def":          150,   # 小防御
    "hp_percent":        100,   # 大生命
    "atk_percent":       100,   # 大攻击
    "def_percent":       100,   # 大防御
    "elemental_mastery": 100,   # 元素精通
    "energy_recharge":   100,   # 元素充能
    "crit_rate":          75,   # 暴击率
    "crit_dmg":           75,   # 暴击伤害
}

TOTAL_SUBSTAT_WEIGHT = sum(SUBSTAT_WEIGHTS.values())

# 副词条分类（按概率层级）
SUBSTAT_CATEGORIES = {
    "high":   ["flat_hp", "flat_atk", "flat_def"],           # 权重150, 各15%
    "medium": ["hp_percent", "atk_percent", "def_percent",
               "elemental_mastery", "energy_recharge"],       # 权重100, 各10%
    "low":    ["crit_rate", "crit_dmg"],                      # 权重75, 各7.5%
}

# 副词条中文名
SUBSTAT_NAMES_CN = {
    "flat_hp":           "小生命",
    "flat_atk":          "小攻击",
    "flat_def":          "小防御",
    "hp_percent":        "大生命",
    "atk_percent":       "大攻击",
    "def_percent":       "大防御",
    "elemental_mastery": "元素精通",
    "energy_recharge":   "元素充能",
    "crit_rate":         "暴击率",
    "crit_dmg":          "暴击伤害",
}

# ============================================================
# 掉落相关数据
# ============================================================

# 圣遗物副本每次掉落五星圣遗物数量概率
# 20树脂: 约93%概率出1个, 约7%概率出2个
DROP_COUNT_PROB = {
    1: 0.93,
    2: 0.07,
}
EXPECTED_DROPS_PER_RUN = sum(k * v for k, v in DROP_COUNT_PROB.items())  # ≈ 1.07

# 每个副本有两个套装，每次掉落各有50%概率属于目标套装
TARGET_SET_PROB = 0.5

# 五个部位均匀分布（各20%）
SLOT_PROB = {slot: 0.2 for slot in ALL_SLOTS}

# 初始副词条数量概率（圣遗物副本）
INITIAL_SUBSTAT_COUNT_PROB = {
    3: 0.80,  # 80%概率初始3词条
    4: 0.20,  # 20%概率初始4词条
}


def get_main_stat_prob(slot: str, main_stat: str) -> float:
    """获取某部位某主词条的掉落概率"""
    dist = MAIN_STAT_DISTRIBUTION.get(slot, {})
    return dist.get(main_stat, 0.0)


def get_substat_weight(substat: str) -> int:
    """获取某副词条的原始权重"""
    return SUBSTAT_WEIGHTS.get(substat, 0)


def get_effective_substat_prob(substat: str, main_stat: str) -> float:
    """
    计算某副词条在给定主词条下的有效掉落概率。
    规则: 副词条不能与主词条相同。
    """
    if substat == main_stat:
        return 0.0
    # 排除主词条后的总权重
    excluded_weight = SUBSTAT_WEIGHTS.get(main_stat, 0)
    effective_total = TOTAL_SUBSTAT_WEIGHT - excluded_weight
    return SUBSTAT_WEIGHTS.get(substat, 0) / effective_total


def get_artifact_prob(slot: str, main_stat: str) -> float:
    """
    计算获得特定部位 + 特定主词条圣遗物的单次掉落概率。
    考虑: 部位概率 × 主词条概率
    """
    slot_p = SLOT_PROB.get(slot, 0.2)
    main_p = get_main_stat_prob(slot, main_stat)
    return slot_p * main_p


def print_data_summary():
    """打印数据摘要"""
    print("=" * 60)
    print("  原神圣遗物概率数据摘要")
    print("=" * 60)
    print(f"\n数据来源: KQM, Genshin Fandom Wiki, 游戏解包数据")
    print(f"\n【掉落基础数据】")
    print(f"  每次副本(20树脂)期望五星圣遗物数: {EXPECTED_DROPS_PER_RUN:.2f}")
    print(f"  目标套装概率: {TARGET_SET_PROB*100}%")
    print(f"  期望每次获得目标套装五星圣遗物: {EXPECTED_DROPS_PER_RUN * TARGET_SET_PROB:.3f} 个")
    print(f"  部位均匀分布: 各{SLOT_PROB[SLOT_FLOWER]*100}%")

    print(f"\n【主词条分布】")
    for slot in ALL_SLOTS:
        print(f"\n  [{SLOT_NAMES_CN[slot]}]")
        dist = MAIN_STAT_DISTRIBUTION[slot]
        for stat, prob in sorted(dist.items(), key=lambda x: -x[1]):
            name = MAIN_STAT_NAMES_CN.get(stat, stat)
            if prob >= 1.0:
                print(f"    {name}: 100% (固定)")
            else:
                print(f"    {name}: {prob*100:.2f}%")

    print(f"\n【副词条权重】(总权重={TOTAL_SUBSTAT_WEIGHT})")
    print(f"  高概率层 (权重150, 各{150/TOTAL_SUBSTAT_WEIGHT*100:.1f}%):")
    for s in SUBSTAT_CATEGORIES["high"]:
        print(f"    {SUBSTAT_NAMES_CN[s]} ({s})")
    print(f"  中概率层 (权重100, 各{100/TOTAL_SUBSTAT_WEIGHT*100:.1f}%):")
    for s in SUBSTAT_CATEGORIES["medium"]:
        print(f"    {SUBSTAT_NAMES_CN[s]} ({s})")
    print(f"  低概率层 (权重75, 各{75/TOTAL_SUBSTAT_WEIGHT*100:.1f}%):")
    for s in SUBSTAT_CATEGORIES["low"]:
        print(f"    {SUBSTAT_NAMES_CN[s]} ({s})")

    print(f"\n【初始副词条数概率】")
    for n, p in INITIAL_SUBSTAT_COUNT_PROB.items():
        print(f"  {n}词条: {p*100:.0f}%")
    print("=" * 60)


if __name__ == "__main__":
    print_data_summary()
