# V13 打印准备 / Print preparation

记录日期：2026-10-19。**用户决定暂缓打印。V13 已完成 Bambu Studio 图形界面切片，没有发送到打印机，没有实物结果。**

Printing is paused by the user. GUI slicing is complete; no V13 print task has been submitted.

## 模型锁定 / Model identity

- 当前文件：`../v13/massage-comb-v13.stl`。
- SHA-256：`738ba2182f7e2160b3a154ae202eba4e92cfba4032a6b856794e526116cbd013`。
- 90.53 × 49.22 × 15.30 mm；五齿，单一连通、封闭网格。
- V13 无对应 STEP，V12 STEP 不能替代本版。未复用已被否定的 V10 打印任务。

## 已复核工艺 / Verified GUI settings

| 项目 / Item | 设置 / Setting |
| --- | --- |
| 机型与喷嘴 / Printer and nozzle | Bambu Lab H2C，0.4 mm，单喷嘴单色 |
| 耗材 / Filament | 黑色 PLA Basic / Black PLA Basic |
| 热床板 / Plate | 增稳低温打印板 / SuperTack |
| 层高 / 首层 / Layer / first layer | 0.12 / 0.20 mm |
| 外墙 / 内墙 / Outer / inner wall | 35 / 60 mm/s |
| 首层 / 首层填充 / First layer / infill | 20 / 25 mm/s |
| 顶面 / Top surface | 30 mm/s |
| 稀疏 / 实心填充 / Sparse / solid infill | 80 / 60 mm/s |
| 支撑 / 支撑界面 / Support / interface | 45 / 30 mm/s |
| 桥接 / Bridge | 25 mm/s |
| 常规 / 外墙加速度 / Normal / outer acceleration | 2000 / 800 mm/s² |
| 壁数 / 填充 / Walls / infill | 4 / 25% Gyroid |
| 顶 / 底壳层数 / Top / bottom layers | 9 / 7（顶壳最小厚度 0.8 mm） |
| 摆放 / Orientation | 握持部平背贴床，梳齿上弯 / Flat grip back down, teeth curve upward |
| 支撑 / Support | 树状自动，仅热床；阈值 35° / Automatic tree, build plate only, 35° |
| 支撑间隙 / Support separation | 上下 Z 间隙 0.20 mm，XY 间隙 0.35 mm |
| 顶部支撑界面 / Top support interface | 3 层 / layers |
| 防翘边 / Brim | 仅外侧 5 mm，模型间隙 0.1 mm |
| 擦料塔 / Prime tower | 关闭，单喷嘴单色 / Off for the single-color, single-nozzle job |
| 切片层数 / Layers | 127 |
| GUI 估时 / Estimated duration | 2 小时 27 分钟 / 2 h 27 min |
| GUI 用料 / Estimated filament | 7.08 m / 21.46 g |

估时不是实际打印耗时。不同机型、材料、喷嘴、板型、支撑和校准选项会改变时间与用料。

## 检查经过与状态 / Checks and status

1. 从 V13 STL 新建工程；完成离线切片及静态路径检查。离线日志存在厂家 H2C 模板指令解析告警，没有为消除告警而删除或修改厂家启动指令；离线 G-code 不作为直接发送文件。
2. 在 Bambu Studio 2.8.2.61 中载入可编辑工程，发现部分默认速度与支撑覆盖了预期参数；在界面内重设，保存并重新切片。核对保存后的工程设置、支撑预览与估时，以上表格记录的是实际 GUI 配置。
3. 发送界面确认目标 H2C 正在执行其他打印任务，发送按钮禁用，所以没有提交。耗材映射曾在该设备上核对；槽位不作为跨设备通用设置。
4. 尝试检查另一台设备时，窗口操作未能取得该机实时状态；不能据此判定另一台空闲或就绪。
5. 用户随后决定先整理并发布项目，暂停打印。以后重新开始须有新的打印指示，重新核对设备空闲、热床清空、喷嘴、板型及实际耗材。

The generic settings above are documented for reproducibility. Local 3MF/G-code jobs, device aliases, serial numbers, network details and credentials are not published. The previous send attempt stopped at a disabled send button; it was not a queued job.

## 下次试打 / Next physical trial

新获得打印指示后，按实际设备重新切片，检查首层和五个上弯齿的底部支撑；发送前确认床面已清空、板型与耗材映射正确。若更换打印机，不直接使用本次 H2C G-code。

冷却取件、拆除支撑并检查圆头、齿缝、齿根与毛刺。第一件主要验证握持、头皮轻触感受、缠发和表面处理；不从模型圆润或切片成功推断人体适配或耐久性。
