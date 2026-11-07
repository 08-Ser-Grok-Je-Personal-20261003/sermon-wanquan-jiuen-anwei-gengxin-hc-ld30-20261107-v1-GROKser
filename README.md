# 基督以完全的救恩安慰并更新他的教会 · 林前11:17–34 · 海德堡要理问答主日30
# Christ Comforts and Renews His Church by a Finished Salvation · 1 Cor 11:17–34 · Heidelberg Catechism LD 30

## 线上链接 / Live links

- GitHub Pages: https://08-ser-grok-je-personal-20261003.github.io/sermon-wanquan-jiuen-anwei-gengxin-hc-ld30-20261107-v1-GROKser/
- Surge: https://wanquan-jiuen-anwei-gengxin-hc-ld30-20261107-v1-grokser.surge.sh
- Repository: https://github.com/08-Ser-Grok-Je-Personal-20261003/sermon-wanquan-jiuen-anwei-gengxin-hc-ld30-20261107-v1-GROKser

讲题：基督以完全的救恩安慰并更新他的教会。要点：① 仰望一次献上的基督　② 省察来到桌前的自己　③ 尊重基督所爱的身体。
诗歌只列编号：韵诗第8篇3–5节 · 韵诗第28篇1、4、5节 · 圣诗第52首 · 圣诗第62首（圣餐）· 诗篇23篇。

静态多页网站（HTML / CSS / 原生 JS，无外部库）。版本 v1.1：修正羊皮纸与亮色主题的文字对比度，并加上可逐步查看的三步主线。Surge 由协调员在自己的电脑发布；本仓库不放 CNAME。网址不变。

## 结构 / Structure

| 文件 | 内容 |
|---|---|
| `index.html` | 总入口、一句话总结、三点默想、站点地图、三条线上链接 |
| `sermon.html` | 完整讲章、背景、四个闭环、16道讨论题、逐节大意、信条原文 |
| `table.html` | 问80的历史与弥撒对照、省察、纪律、相关信条 |
| `creeds-read.html` | 三大信经阅读与背诵 |
| `forms-read.html`, `hc.html`, `belgic.html`, `dort.html` | 三项联合信条全文 |
| `compare.html` | 三信经与三信条比较 |
| `memorize.html` | 闪卡、填空、测验、打印摘要 |
| `resources.html` | 出处 |
| `corpus/` | 信经与信条 JSON |
| `build.py` | 由 `src/` 与 `corpus/` 生成页面 |
| `verify_verbatim.py` | 逐字校验与漏引扫描 |

## 如何重新生成

```bash
python3 build.py
python3 verify_verbatim.py
python3 tools/check_links.py
python3 tools/qa.py /tmp/shots-ld30 --shots
python3 tools/contrast_audit.py /tmp/contrast-ld30
```

引文指令如 `{{HC 80}}`、`{{BC 35}}`、`{{DORT 5 14}}` 只从 `corpus/` 取文。圣经讲解标为“大意”。主日29只在需要交代上一主日时作为背景出现。

## 保留与限制

- 地图与流程图都标明为示意图。不把罗马豪宅平面图当作林前11章的现场。
- 问80的版本次序较清楚；具体发行日与“唯一动机”不作过度断言。
- 天主教官方自述与改革宗判断分栏，不把对方说成“每次重新杀死耶稣”。
- 疾病不能从本段倒推成每个人的隐罪。
- 圣诗与韵诗只列编号，不转录歌词。
- 闪卡进度只存在访问者浏览器的 localStorage。
