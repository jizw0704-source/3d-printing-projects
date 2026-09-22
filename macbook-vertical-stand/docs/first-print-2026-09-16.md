# Design 1.0：设计回顾与首次完整打印

记录日期：2026-09-16。此文为会话和打印软件观测的进展快照，不是实时打印监控。

## 当前结论

- 设计基线：hello 竖放支架 · 1.0 设计定稿，对应原 V14。
- 已完成几何检查、STEP 导入和完整支架切片；任务已提交，用户随后确认完整打印已完成，并反馈“感觉用起来挺不错的”。
- 打印完成和初步使用良好来自用户反馈。尚未取得实物照片、尺寸测量、贴垫细节、承重、防倾倒或温升测试数据，不能标记为系统性实物验收通过。
- 用户选择黑色 PLA，直接打印完整支架；30 mm 小试槽本次未打印。

## 设计决策回顾

1. 底座宽度由讨论中的 70 mm 收窄到 45 mm，长度确定为 150 mm，厚度 6 mm。
2. 后挡架展开向两侧延伸，经过加宽和圆角边界裁切，最终控制在底座顶部投影内；后框实际宽约 144.14 mm。
3. 前侧采用开放连笔 hello，后侧为圆角蜂窝，两侧根部与底座连为一体；提高曲面离散精度，并增加局部连接条和支撑筋。
4. 裸槽 22.5 mm，预留双侧各 3 mm 软垫，名义净距 16.5 mm。15.5 mm 裸机厚度是适配假设，胶层、软垫压缩与打印误差需实测。
5. 后侧接触边和底部连接条局部倒圆。hello 整圈圆角尝试未通过导出检查，最终未采用；接触电脑的区域仍需软垫保护。
6. 当前工作树只保留 V14 基线，展示名称改为 Design 1.0。旧设计保留在 Git 历史，`v14/` 路径和 `v14-stable` 历史标签保持兼容。
7. 已有中英文 README 和真实模型生成的鼠尾草绿展示渲染。展示色与本次实际黑色 PLA 区分记录。

## 几何检查与证据边界

主体有效单实体、STL 闭合且体积为正；STEP 回读相对体积误差约 1.9 × 10⁻¹⁰。主体包围尺寸约 150.002 × 45.001 × 39.544 mm，实体体积约 55.5965 cm³。

`v14/validation.json` 是建模时的历史几何检查记录，其中“未切片”描述反映生成时状态；本次打印进展以此文为准。未为更新进展重跑建模或改写历史检查数据。

几何检查与切片成功不等于强度验收。45 mm 窄底座仍需重点检查侧推、线缆牵拉和实际重心条件下的稳定性；现有估算不是有限元分析或实物测试。

## 实际切片与发送记录

| 项目 | 本次记录 |
| --- | --- |
| 输入模型 | `v14/stand-v14.step`，直接导入 STEP |
| STEP 转换 | 线偏转 0.003 mm；角偏转 0.50°；29,298 三角面；不拆分复合实体 |
| 软件 / 设备 | Bambu Studio / Bambu Lab P1S，0.4 mm 标准喷嘴 |
| 打印板 | 纹理 PEI；底座平放 |
| 耗材 | PLA Basic，发送窗口核对为 A4 黑色 PLA |
| 工艺预设显示 | `0.20mm Standard @BBL X1C`，打印机选择为 P1S；下列参数为本次调整后的值 |
| 层高 | 0.20 mm |
| 墙与实心层 | 4 层墙；顶部 5 层 / 1 mm；底部 5 层 |
| 填充 | 25%，网格 |
| 支撑 | 树状（自动）；阈值 30°；“仅在打印板生成”关闭 |
| 切片估计 | 2 小时 24 分钟；198 层；56.22 g / 18.55 m |
| 耗材构成 | 模型 47.08 g；支撑 9.14 g |
| 发送选项 | 自动热床调平开启；延时摄影开启 |
| 任务名 | `stand-print-check` |
| 启动证据 | 发送完成后设备页显示同名任务，0/198 层并开始预热；随后用户确认已开始打印 |

预计时间与耗材来自切片结果，不是实测。喷嘴与热床的最终打印温度未单独记录，不将预热阶段温度当作打印设定温度。

## 超范围报错的原因与修复

重新导入后项目内有两个对象：打印板上的黑色支架，以及盘外的旧副本。保存项目并检查 3MF 后，旧副本平移约为 X=-4444.49、Y=-7904.20、Z=19772.00 mm，导致“位于打印板边界或超出高度限制”报错。对板内对象居中或排布无法解决另一个对象的异常。

在对象列表的“盘外”分组中移除旧副本后，报错消失，切片与提交成功。修复后的项目仅有一个可打印主体；保留黑色材料和既定打印参数，未缩放或修改 CAD 几何。

本地保留 `v14/stand-print-check.3mf` 供继续打印排查。本次 GitHub 同步仅上传文档，不将设备相关的本地打印工程作为通用发布文件。

## 打印完成与后续验证

- [x] 用户确认首次完整打印完成。
- [x] 记录初步使用反馈：“感觉用起来挺不错的”。

以下细项仍待补充，不从总体好评推断各项已通过：

- [ ] 确认完成时间、实际用料与打印异常，拍摄正面、背面、底面照片。
- [ ] 冷却取件并去除支撑，检查翘边、分层、根部裂纹、蜂窝与 hello 细节。
- [ ] 测量裸槽宽和底座平整度；记录软垫含胶厚度、贴垫后间隙。
- [ ] 用受保护的替代载荷验证承重、残余变形、侧推和线缆牵拉稳定性。
- [ ] 完成以上检查后，再做有人看护的 MacBook 试装；运行温升验证另行记录。
- [ ] 按实测决定是否调整底座宽度、固定方式、局部结构或打印参数；保留 Design 1.0 基线。

## English summary

Design 1.0 (formerly V14) is the retained design baseline for a 150 × 45 mm MacBook stand with open hello lettering and a honeycomb rear frame. The first full print was sliced from STEP and submitted to a P1S using black PLA in A4, a 0.4 mm nozzle, 0.20 mm layers, four walls, 25% grid infill and automatic tree supports. Estimates: 2 h 24 min, 56.22 g, 198 layers.

An out-of-bounds error was caused by a second, misplaced object approximately 19.8 m above the plate. Removing that off-plate duplicate resolved the error without changing the CAD geometry. The user subsequently confirmed that the full print was complete and reported a positive initial experience. This is user-reported evidence, not a measured acceptance test. Photos, measured padded fit, load, tipping, thermal and long-term stability checks remain pending. The fit gauge was skipped by user choice for this attempt.
