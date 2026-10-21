# WAR3 训练营 · 兽族冲榜数据实验室

线上地址：<https://lucifer.ren/war3-lab/>（GitHub Pages，main 分支自动发布）

与博客《让魔兽再次伟大》同源：地图点位来自 Liquipedia Preview（`~/github/blog/tools/war3-preview-data.json`），野怪等级来自 battle.net 官方族页，营地经验按 1.27/TFT 口径计算。

## 本地预览

```bash
cd ~/github/war3-lab
./start.command          # 或: python3 -m http.server 8931
# 打开 http://127.0.0.1:8931/
```

纯静态站（index.html + data.js + assets/），无构建步骤、无依赖。

## 发布

```bash
git add -A && git commit -m "update" && git push
```

push 到 main 即自动上线（GitHub Pages），一般一分钟内生效。

## 改数据

- 营地/建筑/出生点坐标：源数据在博客仓库 `tools/war3-preview-data.json`，重新生成 `data.js`（生成脚本见会话记录，或手改 data.js）
- 路线/速查表/文案：直接编辑 `data.js` 与 `index.html`
- 底图：`assets/preview-<图>.jpg`（与博客 `tools/war3-base/` 同名同源）
