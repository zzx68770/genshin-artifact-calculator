"""
原神圣遗物数据爬虫
===================
从多个在线源爬取圣遗物掉落概率数据。
当网页不可访问（反爬保护）时，回退到预设的解包数据。

数据源:
  1. KeqingMains (KQM) - https://keqingmains.com/misc/artifacts/
  2. Genshin Fandom Wiki - https://genshin-impact.fandom.com/wiki/Artifact/Distribution
  3. 预设解包数据 (artifact_data.py)
"""

import re
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Optional, Tuple
from html.parser import HTMLParser

# ============================================================
# 数据源 URL
# ============================================================
KQM_URL = "https://keqingmains.com/misc/artifacts/"
FANDOM_WIKI_URL = "https://genshin-impact.fandom.com/wiki/Artifact/Distribution"
BILIBILI_WIKI_URL = "https://wiki.biligame.com/ys/圣遗物"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class SimpleHTMLTableParser(HTMLParser):
    """简单的 HTML 表格解析器，用于提取概率数据"""

    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.in_th = False
        self.current_row = []
        self.tables = []
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag in ("table",):
            self.in_table = True
            self.tables.append([])
        elif tag in ("tr",):
            self.in_tr = True
            self.current_row = []
        elif tag in ("td", "th"):
            if tag == "td":
                self.in_td = True
            else:
                self.in_th = True
            self.current_text = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.current_row.append(self.current_text.strip())
            self.in_td = False
            self.in_th = False
        elif tag in ("tr",):
            if self.in_table and self.current_row:
                # 找到最后一个活跃的表格
                for t in reversed(self.tables):
                    if isinstance(t, list):
                        t.append(self.current_row)
                        break
            self.in_tr = False
        elif tag in ("table",):
            self.in_table = False

    def handle_data(self, data):
        if self.in_td or self.in_th:
            self.current_text += data


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """尝试获取网页内容"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="ignore")
    except Exception as e:
        print(f"  [爬虫] 无法访问 {url}: {e}")
        return None


def extract_percentages(text: str) -> Dict[str, float]:
    """从文本中提取百分比数值"""
    results = {}
    # 匹配 "xxx: 26.68%" 或 "xxx 26.68%" 格式
    pattern = r'([\u4e00-\u9fff\w%+\s]+?)[:：\s]+(\d+\.?\d*)\s*%'
    matches = re.findall(pattern, text)
    for name, value in matches:
        name = name.strip().lower().replace(" ", "_")
        try:
            results[name] = float(value) / 100.0
        except ValueError:
            pass
    return results


def parse_kqm_tables(html: str) -> Optional[Dict]:
    """解析 KQM 页面中的圣遗物概率表格"""
    parser = SimpleHTMLTableParser()
    parser.feed(html)

    if not parser.tables:
        return None

    result = {}
    for table in parser.tables:
        for row in table:
            if len(row) >= 2:
                key = row[0].strip()
                for cell in row[1:]:
                    pct_match = re.search(r'(\d+\.?\d*)\s*%', cell)
                    if pct_match:
                        result[key] = float(pct_match.group(1)) / 100.0
    return result if result else None


def crawl_artifact_data() -> Tuple[Dict, str]:
    """
    主爬虫函数。
    返回: (数据字典, 数据源标识)
    """
    print("[爬虫] 开始获取圣遗物概率数据...")

    # 尝试多个数据源
    sources = [
        ("KeqingMains (KQM)", KQM_URL, parse_kqm_tables),
        ("Bilibili Wiki", BILIBILI_WIKI_URL, parse_kqm_tables),
    ]

    for name, url, parser_fn in sources:
        print(f"[爬虫] 尝试: {name} ({url})")
        html = fetch_url(url)
        if html:
            data = parser_fn(html)
            if data:
                print(f"[爬虫] ✓ 成功从 {name} 获取数据")
                return data, name
            else:
                print(f"[爬虫] ✗ {name} 返回了内容但无法解析所需数据")

    # 回退到预设数据
    print("[爬虫] 所有在线源不可用，回退到预设解包数据")
    from artifact_data import (
        MAIN_STAT_DISTRIBUTION,
        SUBSTAT_WEIGHTS,
        DROP_COUNT_PROB,
        EXPECTED_DROPS_PER_RUN,
        TARGET_SET_PROB,
        SLOT_PROB,
        INITIAL_SUBSTAT_COUNT_PROB,
    )

    data = {
        "main_stat_distribution": MAIN_STAT_DISTRIBUTION,
        "substat_weights": SUBSTAT_WEIGHTS,
        "drop_count_prob": DROP_COUNT_PROB,
        "expected_drops_per_run": EXPECTED_DROPS_PER_RUN,
        "target_set_prob": TARGET_SET_PROB,
        "slot_prob": SLOT_PROB,
        "initial_substat_count_prob": INITIAL_SUBSTAT_COUNT_PROB,
    }
    return data, "预设解包数据 (datamined game files)"


def export_data_json(data: Dict, filepath: str = "artifact_data.json"):
    """将爬取的数据导出为JSON文件"""
    # 序列化处理
    serializable = {}
    for key, value in data.items():
        if isinstance(value, dict):
            # 确保所有键都是字符串
            serializable[key] = {
                str(k): (dict(v) if isinstance(v, dict) else v)
                for k, v in value.items()
            }
        else:
            serializable[key] = value

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"[爬虫] 数据已导出到 {filepath}")


if __name__ == "__main__":
    data, source = crawl_artifact_data()
    print(f"\n数据源: {source}")
    export_data_json(data)
