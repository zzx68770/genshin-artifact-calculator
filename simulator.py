"""
原神圣遗物期望计算器 — 理论概率计算
=====================================
基于实际游戏概率数据，通过概率公式计算刷出一套目标圣遗物所需的期望次数。

用法（命令行）:
  python simulator.py                           # 默认目标
  python simulator.py --sands atk_percent --goblet pyro_dmg --circlet crit_rate
  python simulator.py --save 结果.txt           # 保存输出

主要被 app.py 作为模块调用:
  from simulator import TargetBuild, theoretical_expected_runs
"""

import math
import sys
import os
import argparse
from typing import Dict
from dataclasses import dataclass
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from artifact_data import (
    SLOT_FLOWER, SLOT_PLUME, SLOT_SANDS, SLOT_GOBLET, SLOT_CIRCLET,
    ALL_SLOTS, SLOT_NAMES_CN, MAIN_STAT_NAMES_CN,
    MAIN_STAT_DISTRIBUTION,
    EXPECTED_DROPS_PER_RUN, TARGET_SET_PROB, SLOT_PROB,
    get_main_stat_prob,
)

# ============================================================
# 目标配置
# ============================================================

@dataclass
class TargetBuild:
    """一套目标圣遗物配置"""
    sands_main: str     # 沙漏主词条
    goblet_main: str    # 杯子主词条
    circlet_main: str   # 头主词条

    def __str__(self):
        parts = [
            f"花: 生命值 (固定)",
            f"羽毛: 攻击力 (固定)",
            f"沙漏: {MAIN_STAT_NAMES_CN.get(self.sands_main, self.sands_main)}",
            f"杯子: {MAIN_STAT_NAMES_CN.get(self.goblet_main, self.goblet_main)}",
            f"头: {MAIN_STAT_NAMES_CN.get(self.circlet_main, self.circlet_main)}",
        ]
        return "\n".join(parts)


# ============================================================
# 理论计算
# ============================================================

def theoretical_expected_runs(target: TargetBuild) -> Dict:
    """
    理论计算：基于概率公式计算期望次数。

    核心思路：
    - 每次副本期望掉落 EXPECTED_DROPS_PER_RUN 个五星，其中 TARGET_SET_PROB 概率是目标套装
    - 对于每个部位：P(得到) = 部位概率 × 主词条概率
    - 使用收集券问题公式 (coupon collector with unequal probabilities)
      计算集齐五件不同部位的期望次数。

    返回:
      piece_probabilities: 每个部位单次掉落的综合概率
      expected_per_run: 每次副本期望获得该部位的个数
      single_expected_runs: 单独刷每个部位的期望次数
      total_expected_runs: 集齐全部五件的期望次数
      total_expected_resin: 期望体力消耗
      hardest_piece: 瓶颈部位 key
      hardest_piece_name: 瓶颈部位中文名
    """
    piece_probs = {}

    # 花 — 固定生命值
    p_flower = SLOT_PROB[SLOT_FLOWER] * get_main_stat_prob(SLOT_FLOWER, "flat_hp")
    piece_probs[SLOT_FLOWER] = p_flower

    # 羽毛 — 固定攻击力
    p_plume = SLOT_PROB[SLOT_PLUME] * get_main_stat_prob(SLOT_PLUME, "flat_atk")
    piece_probs[SLOT_PLUME] = p_plume

    # 沙漏
    p_sands = SLOT_PROB[SLOT_SANDS] * get_main_stat_prob(SLOT_SANDS, target.sands_main)
    piece_probs[SLOT_SANDS] = p_sands

    # 杯子 — 通常是瓶颈
    p_goblet = SLOT_PROB[SLOT_GOBLET] * get_main_stat_prob(SLOT_GOBLET, target.goblet_main)
    piece_probs[SLOT_GOBLET] = p_goblet

    # 头
    p_circlet = SLOT_PROB[SLOT_CIRCLET] * get_main_stat_prob(SLOT_CIRCLET, target.circlet_main)
    piece_probs[SLOT_CIRCLET] = p_circlet

    # 每次副本期望获得的有效圣遗物数
    effective_per_run = EXPECTED_DROPS_PER_RUN * TARGET_SET_PROB

    # 每次副本期望获得的每个部位数量
    expected_per_run = {
        slot: effective_per_run * p for slot, p in piece_probs.items()
    }

    # 单独期望：刷出一个特定部位需要的副本次数
    single_expected_runs = {
        slot: 1.0 / p if p > 0 else float('inf')
        for slot, p in expected_per_run.items()
    }

    # 使用收集券公式计算集齐全部五件的期望次数
    # E[T] = Σ(-1)^{r+1} Σ_{组合大小r} 1 / Σ λ_i
    # 其中 λ_i 是每件 i 的获取率（每次副本）
    lambdas = {slot: expected_per_run[slot] for slot in ALL_SLOTS}

    total = 0.0
    n_pieces = 5
    for r in range(1, n_pieces + 1):
        sign = 1 if r % 2 == 1 else -1
        for combo in combinations(ALL_SLOTS, r):
            sum_lambda = sum(lambdas[s] for s in combo)
            if sum_lambda > 0:
                total += sign / sum_lambda

    # 找瓶颈
    hardest_key = max(single_expected_runs, key=single_expected_runs.get)

    return {
        "piece_probabilities": piece_probs,
        "expected_per_run": expected_per_run,
        "single_expected_runs": single_expected_runs,
        "total_expected_runs": total,
        "total_expected_resin": total * 20,
        "hardest_piece": hardest_key,
        "hardest_piece_name": SLOT_NAMES_CN.get(hardest_key, "?"),
    }


# ============================================================
# 结果展示
# ============================================================

def print_theoretical_results(results: Dict):
    """打印理论计算结果（命令行使用）"""
    print(f"\n{'='*60}")
    print(f"  📐 理论概率计算")
    print(f"{'='*60}")

    print(f"\n  每次副本(20树脂):")
    print(f"    期望掉落五星圣遗物: {EXPECTED_DROPS_PER_RUN:.2f} 个")
    print(f"    期望目标套装: {EXPECTED_DROPS_PER_RUN * TARGET_SET_PROB:.2f} 个")

    print(f"\n  单部位期望 (仅考虑该部位):")
    for slot in ALL_SLOTS:
        p = results["piece_probabilities"][slot]
        er = results["single_expected_runs"][slot]
        name = SLOT_NAMES_CN[slot]
        bar = "█" * min(50, int(er / 10))
        print(f"    {name}: {er:>8.0f} 次副本 ({er*20:>8.0f} 体力)  {bar}")

    print(f"\n  ⭑ 收集全套圣遗物的期望:")
    total = results["total_expected_runs"]
    resin = results["total_expected_resin"]
    days = resin / 180
    print(f"    期望副本次数: {total:,.0f} 次")
    print(f"    期望体力消耗: {resin:,.0f} 树脂")
    print(f"    期望天数(仅自回体): {days:.1f} 天")
    print(f"    最难部位: {results['hardest_piece_name']}")

    # 瓶颈分析
    hardest = results["hardest_piece"]
    if hardest in (SLOT_GOBLET, SLOT_CIRCLET):
        dist = MAIN_STAT_DISTRIBUTION[hardest]
        target_stat = {
            SLOT_GOBLET: lambda t: t.goblet_main,
            SLOT_CIRCLET: lambda t: t.circlet_main,
        }
        print(f"\n  💡 瓶颈分析:")
        print(f"    杯子用散件（不计套装），难度会大幅下降。")

    print(f"\n  注：由于杯子概率极低（元素杯各仅5%），")
    print(f"  实际游戏中使用 4 件套 + 散件杯子是常见策略。")


# ============================================================
# CLI 入口（也可被 main.py 调用）
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="原神圣遗物期望计算器（理论计算）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python simulator.py
  python simulator.py --sands atk_percent --goblet pyro_dmg --circlet crit_rate
  python simulator.py --save 结果.txt
        """
    )
    parser.add_argument("--sands", type=str, default="atk_percent",
                        help="沙漏主词条 (默认: atk_percent)")
    parser.add_argument("--goblet", type=str, default="pyro_dmg",
                        help="杯子主词条 (默认: pyro_dmg)")
    parser.add_argument("--circlet", type=str, default="crit_rate",
                        help="头主词条 (默认: crit_rate)")
    parser.add_argument("--save", type=str, default=None,
                        help="将输出保存到指定文件")

    args = parser.parse_args()

    target = TargetBuild(
        sands_main=args.sands,
        goblet_main=args.goblet,
        circlet_main=args.circlet,
    )

    print("=" * 60)
    print("  原神圣遗物期望计算器")
    print("=" * 60)
    print(f"\n目标配置:")
    print(f"  沙漏: {MAIN_STAT_NAMES_CN.get(args.sands, args.sands)}")
    print(f"  杯子: {MAIN_STAT_NAMES_CN.get(args.goblet, args.goblet)}")
    print(f"  头冠: {MAIN_STAT_NAMES_CN.get(args.circlet, args.circlet)}")

    results = theoretical_expected_runs(target)
    print_theoretical_results(results)

    if args.save:
        # 重定向输出到文件
        with open(args.save, "w", encoding="utf-8") as f:
            f.write(f"目标: {target}\n")
            f.write(f"\n理论期望: {results['total_expected_runs']:,.0f} 次副本\n")
            f.write(f"期望体力: {results['total_expected_resin']:,.0f} 树脂\n")
            f.write(f"期望天数: {results['total_expected_resin']/180:.1f} 天\n")
            f.write(f"瓶颈部位: {results['hardest_piece_name']}\n")
        print(f"\n[结果已保存到: {args.save}]")


if __name__ == "__main__":
    main()
