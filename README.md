# 原神圣遗物期望计算器

帮你算算刷一套目标圣遗物要打多少次副本、花多少体力。

## 安装

```bash
# 克隆仓库
git clone https://github.com/zzx68770/genshin-artifact-calculator.git
cd genshin-artifact-calculator

# 安装依赖（只需要 streamlit）
pip install streamlit
```

## 使用方式

### 方式一：命令行（最快）

```bash
# 默认配置（攻击沙 + 火伤杯 + 暴击头）
python simulator.py

# 自定义目标（示例：雷神）
python simulator.py --sands energy_recharge --goblet electro_dmg --circlet crit_rate

# 保存结果到文件
python simulator.py --save result.txt
```

### 方式二：网页界面

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，在左侧选择目标主词条，点击计算即可。

### 方式三：双击启动（仅 Windows）

双击 `启动计算器.vbs`，会弹出一个独立的应用窗口（无浏览器标签页）。用完关掉窗口，后台服务自动停止，全程无弹窗。

> 首次使用前需要先执行 `pip install streamlit`

## 项目结构

```
genshin-artifact-calculator/
├── simulator.py         ← 命令行计算入口
├── app.py               ← 网页界面（Streamlit）
├── artifact_data.py     ← 圣遗物概率数据
├── crawler.py           ← 数据爬取模块
├── main.py              ← 完整流程入口（爬取+模拟）
├── launcher.pyw         ← Windows 启动器（无窗口后台运行）
├── 启动计算器.vbs       ← Windows 双击入口
└── requirements.txt     ← 依赖列表
```

## 各角色常用配置

| 角色 | 沙漏 | 杯子 | 头冠 |
|------|------|------|------|
| 雷神 | `energy_recharge` | `electro_dmg` | `crit_rate` |
| 胡桃 | `hp_percent` | `pyro_dmg` | `crit_dmg` |
| 绫华 | `atk_percent` | `cryo_dmg` | `crit_dmg` |
| 那维莱特 | `hp_percent` | `hydro_dmg` | `crit_dmg` |
| 万叶 | `elemental_mastery` | `anemo_dmg` | `crit_rate` |
| 千织 | `def_percent` | `geo_dmg` | `crit_dmg` |
| 夜兰 | `hp_percent` | `hydro_dmg` | `crit_rate` |

## 词条关键词

- **沙漏**：`atk_percent` `hp_percent` `def_percent` `energy_recharge` `elemental_mastery`
- **杯子**：`pyro_dmg` `hydro_dmg` `electro_dmg` `cryo_dmg` `anemo_dmg` `geo_dmg` `dendro_dmg` `physical_dmg`
- **头冠**：`crit_rate` `crit_dmg` `hp_percent` `atk_percent` `healing_bonus`

## 示例输出

```
目标配置:
  沙漏: 元素充能效率
  杯子: 雷元素伤害加成
  头冠: 暴击率

期望副本次数: 240 次
期望体力消耗: 4,798 树脂
期望天数(仅自回体): 26.7 天
最难部位: 空之杯

💡 瓶颈分析: 杯子用散件（不计套装），难度会大幅下降。
```

## 原理

基于"收集券问题"（Coupon Collector's Problem）的概率公式，计算集齐 5 个不同部位（花、羽、沙、杯、头）且主词条都对所需的期望次数。杯子通常是最大瓶颈——元素伤害杯子只有 5% 概率。

## 数据来源

概率数据来自 KQM (KeqingMains) 和游戏解包数据。

## 依赖

- Python >= 3.8
- streamlit >= 1.35.0（仅网页界面需要）
