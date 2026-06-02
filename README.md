# 原神圣遗物期望计算器

帮你算算刷一套目标圣遗物要打多少次副本、花多少体力。

## 快速开始

```bash
# 安装依赖
pip install streamlit

# 进入目录
cd genshin_artifact

# 命令行快速计算（默认：攻击沙+火伤杯+暴击头）
python simulator.py

# 自定义角色（示例：雷神）
python simulator.py --sands energy_recharge --goblet electro_dmg --circlet crit_rate

# 保存结果到文件
python simulator.py --save result.txt

# 或打开网页界面
streamlit run app.py
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

## 词条关键词

- 沙漏：`atk_percent` `hp_percent` `def_percent` `energy_recharge` `elemental_mastery`
- 杯子：`pyro_dmg` `hydro_dmg` `electro_dmg` `cryo_dmg` `anemo_dmg` `geo_dmg` `dendro_dmg` `physical_dmg`
- 头冠：`crit_rate` `crit_dmg` `hp_percent` `atk_percent` `healing_bonus`

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

## 数据来源

概率数据来自 KQM (KeqingMains) 和游戏解包数据。

## 依赖

- Python >= 3.8
- streamlit >= 1.35.0（仅网页界面需要）
