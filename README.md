# 3D 打印项目集 / 3D Printing Projects

从设计、建模到打印和实物反馈，持续收集我们的 3D 打印作品。后续新项目统一加入这个仓库，每个作品保留独立目录和说明。

A growing collection of our 3D printing projects: CAD models, design illustrations, print settings and real-world feedback.

## 项目一览 / Projects

| 项目 / Project | 当前版本 | 实物进展 |
| --- | --- | --- |
| [hello · MacBook 竖放支架](macbook-vertical-stand/) | Design 1.0 / V14 | 打印完成，用户初步使用反馈良好 |
| [Fishbone · 鱼骨收线器](fishbone-cable-organizer/) | V06 | 打印完成；使用方便，保留现有尺寸 |
| [羽毛球笔筒 / Shuttlecock pen holder](shuttlecock-pen-holder/) | V08 | 双色切片完成，已提交首件试打，待实物验收 |

### hello · 竖放支架

![支架 CAD 展示渲染，非实拍](macbook-vertical-stand/v14/showcase-v14.png)

开放 hello 前挡架、蜂窝后框和一体底座。图为 CAD 展示渲染，实际打印使用黑色 PLA。用户已确认打印完成及初步使用良好；强度和长期稳定性尚未系统验证。

[项目介绍](macbook-vertical-stand/) · [STEP](macbook-vertical-stand/v14/stand-v14.step) · [STL](macbook-vertical-stand/v14/stand-v14.stl) · [打印记录](macbook-vertical-stand/docs/first-print-2026-09-16.md)

### Fishbone · 鱼骨收线器

![鱼骨 V06 设计渲染](fishbone-cable-organizer/assets/design-v06.png)

两对浅弧骨节、双端卡槽和现有挂钩适用的悬挂孔。用户反馈“比想象中大一些，挺方便的”，明确保留 V06 尺寸，不做紧凑版。上图为 CAD 设计渲染，非实拍，实际打印使用黑色 PLA；挂钩适配和不同线缆容量仍待验证。

[项目介绍与设计图](fishbone-cable-organizer/) · [STEP](fishbone-cable-organizer/models/v06/fishbone-v06.step) · [STL](fishbone-cable-organizer/models/v06/fishbone-v06.stl) · [打印记录](fishbone-cable-organizer/docs/PRINTING.md)

### 羽毛球笔筒 / Shuttlecock pen holder

![羽毛球笔筒 V08 CAD 渲染，非实拍](shuttlecock-pen-holder/assets/showcase-v08.png)

16 片宽圆羽毛、镂空连接环与圆润球托，白色主体配黑色环带。高 90 mm，最大外径约 83.4 mm。V08 加强羽梗和羽尖；H2C 双色切片预计约 4 小时、69 g。已提交试打，实物结果待验收。

A 16-feather shuttlecock-inspired holder with a white body and black band. CAD and slicing checks are complete; the first physical trial is pending acceptance.

[中英文介绍与模拟效果图](shuttlecock-pen-holder/) · [双色 STEP](shuttlecock-pen-holder/v08/shuttlecock-v08-two-color.step) · [单色 STL](shuttlecock-pen-holder/v08/shuttlecock-v08-single.stl) · [打印参数与记录](shuttlecock-pen-holder/v08/PRINT-PREPARATION.md)

## 整理方式 / Organization

每个作品独立保存：中英文介绍、CAD 源码、STEP/STL、设计图和实拍、打印参数、版本演进及试用反馈。后续项目放入新的作品目录，并在本页添加图片和入口。具体生成和检查命令见各项目 README。

Each project keeps its own documentation and build instructions. Renders, AI illustrations, slicer estimates and physical observations are labeled separately. A successful print is not a comprehensive strength or durability certification.

## 迁移说明 / Migration

两项旧独立仓库已迁入此处；此仓库是后续更新入口。两个旧独立仓库已按用户确认删除，原仓库链接不再使用。此次复制各仓库 main 的已跟踪文件，没有将原来的提交历史合并进本仓库。来源提交与文件完整性核对见 [迁移记录](MIGRATION.md)。本机 3MF、G-code、设备凭据不纳入迁移。

This repository is the ongoing home for future projects. The two original repositories have been deleted after migration; this collection is the single ongoing repository.

## 开源许可 / License

本仓库原创代码、CAD 模型和展示素材采用 [MIT License](LICENSE)，允许使用、修改和再分发（包括商业用途），请保留版权和许可声明。第三方软件、商标及其权利不包含在本授权中。

Original code, CAD models and presentation assets are available under the MIT License. Third-party dependencies and trademarks retain their respective terms and rights. Designs are provided without warranty; verify fit and suitability before use.
