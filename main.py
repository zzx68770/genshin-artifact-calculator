"""
原神圣遗物数据爬取 & 掉落模拟
==============================
主入口文件，整合爬虫和模拟器功能。

用法:
  python main.py                    # 爬取数据 + 完整模拟
  python main.py --crawl-only       # 仅爬取数据
  python main.py --simulate-only    # 仅模拟(使用预设数据)
  python main.py --build 雷神 --runs 100000  # 自定义目标 + 高精度
"""

import sys
import os

# 确保能导入同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler import crawl_artifact_data, export_data_json
from artifact_data import print_data_summary
from simulator import main as simulator_main


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="原神圣遗物数据爬取与掉落模拟",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                              # 完整流程
  python main.py --crawl-only                 # 仅爬取数据
  python main.py --simulate-only --build 胡桃  # 仅模拟
        """
    )
    parser.add_argument("--crawl-only", action="store_true", help="仅执行爬取")
    parser.add_argument("--simulate-only", action="store_true", help="仅执行模拟")
    parser.add_argument("--output-json", type=str, default=None,
                        help="爬取数据导出JSON路径")

    args, remaining = parser.parse_known_args()

    if args.simulate_only:
        # 直接进入模拟器
        sys.argv = [sys.argv[0]] + remaining
        simulator_main()
        return

    if args.crawl_only:
        print("=" * 60)
        print("  原神圣遗物数据爬取")
        print("=" * 60)
        data, source = crawl_artifact_data()
        print(f"\n数据来源: {source}")

        if args.output_json:
            export_data_json(data, args.output_json)
        else:
            # 打印摘要
            print_data_summary()
        return

    # 完整流程: 爬取 + 模拟
    print("=" * 60)
    print("  原神圣遗物数据爬取 & 掉落模拟")
    print("=" * 60)

    print("\n[阶段 1/2] 爬取数据...")
    data, source = crawl_artifact_data()
    print(f"数据来源: {source}")

    print("\n[阶段 2/2] 进行数值模拟...")
    sys.argv = [sys.argv[0]] + remaining
    simulator_main(data=data)       # ← 把爬到的数据传给模拟器


if __name__ == "__main__":
    main()
