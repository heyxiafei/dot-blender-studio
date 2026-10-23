# 安装与使用

此 ZIP 是 model-product-assets 的 v5 更新包，不是 Blender 插件，也不包含 Blender、原广告/音乐或案例模型。解压后保留完整 model-product-assets 文件夹及 SKILL.md、references、scripts 的相对布局。同名旧 Skill 更新前先备份并避免双份冲突；交付包不等于已在用户设备安装。

对外项目名为 dot Blender Studio，中文为“产品建模与动画制作 Skill”；为兼容旧版，内部目录与调用名仍是 model-product-assets，不要仅因仓库改名而改动它。以下本地目录于 2026-10-23 核对官方文档，不泛化到其他宿主或云端：

- Codex 本地项目级：将整个文件夹放入项目的 .agents/skills/model-product-assets/；个人级为 ~/.agents/skills/model-product-assets/。不要同时装两份同名副本。可用 /skills 查看或以 $model-product-assets 调用；未出现时重启。旧版文档中的 ~/.codex/skills 不是这里统一推荐的新安装路径。[官方说明](https://learn.chatgpt.com/docs/build-skills)
- Claude Code 本地项目级：.claude/skills/model-product-assets/；个人级：~/.claude/skills/model-product-assets/。用 /model-product-assets 调用。此目录说明不覆盖 Cowork/云会话；本项目尚未在 Claude Code 实际做端到端试用。[官方说明](https://code.claude.com/docs/en/skills)
- 其他 Agent：只有在其当前官方文档明确支持 SKILL.md 及相对支持文件时再按其规则导入。没有核实的目录不猜写；能读取 Markdown 不等于具备 Blender 执行能力。

本包是手动本地 Skill，不是已上架插件，也不会自动安装或云端注册。真实项目仓库为 [heyxiafei/dot-blender-studio](https://github.com/heyxiafei/dot-blender-studio)；可从仓库 Code → Download ZIP 获取已上传的主分支源码，不假定存在 GitHub Release。自有 Skill、脚本与文档采用 MIT，范围见 [许可与第三方资源说明](license-and-third-party.md)。模型资源将按独立版本清单提供，未发布前无下载承诺。

## 能做什么，不能承诺什么

- 引导用途/风格，将没有想法的需求收敛成小 Demo。这是设计好的流程并做过代表性情景检查，不是大量用户成功率保证。
- 制作可编辑产品模型、配色/品牌变体，按约定导出与检查。iPhone 8/8 Plus 的具体模型与 GLB 流程已实测；家具、原创类别等是支持的流程范围，不表示已经预制了全部资产。
- 用真实模型制作原创产品/MG 动画或指定片段学习重建。iPhone 4 的 317 帧精确时序项目已实测并被用户接受，有细节差异。
- 分段预览、保护已验收内容、修复再渲染、做技术和独立视觉 QA。自动脚本不替代人的视觉判断。
- 交付可编辑工程、约定导出/成片、来源与复现/检查记录。文件格式、变体、音轨和比较版按本次任务约定，不默认全部附带。

不保证一键生成、像素 1:1、制造精度、所有商品/配色已完成、任何机器性能或素材可商用。不自动上传、安装、代发，也不赋予只有聊天能力的环境 Blender 执行能力。

## 调用例句

下列 $ 写法针对 Codex；Claude Code 换为 /model-product-assets。其他宿主按自己的官方调用方式。

- “用 $model-product-assets 帮我选一个适合我账号的 6 秒小 Demo，先给三种风格。”
- “用 $model-product-assets 做一款原创原木边几，只要 BLEND、GLB 和检查记录，不做视频。”
- “用 $model-product-assets 用现有产品模型做 10 秒无声展示片，先完整低清预览。”
- “用 $model-product-assets 复刻我指定参考中的这个镜头，先核来源和真实边界，做约 5 秒小样；不要自动发平台。”
- “保留我已验收的那段，延展到第一次人物出现之前，保持原始节奏；先确认准确范围。”

## 实际依赖

建模/动画需现有可运行 Blender；检查脚本需 Python 3；视频 QA 与编码另需 ffmpeg/ffprobe。新的三个辅助脚本只用 Python 标准库（check_video 会调用 ffmpeg/ffprobe）。具体模型或重建工程可能另需 Pillow、字体等，依项目说明，不从案例隐式安装。缺工具报告缺口并按授权处理。历史 Blender 4.3.2 案例不是全部版本兼容承诺。

## 脚本用法

以下数值只是已测案例，必须换成本次实际约定值。脚本只读媒体输入并写指定报告/计划/清单，不上传、不安装、不发布。

以下命令从 model-product-assets 目录执行。若当前在仓库根目录，先执行：

    cd model-product-assets

媒体输入和报告路径也相对此工作目录解析；请改成自己的实际路径。

    python scripts/check_video.py demo.mp4 --frames 317 --width 848 --height 1044 --fps 2997/125 --audio present --report qa/video.json

FPS 接受整数、精确小数或分数；脚本严格比较探测到的平均有理数 FPS，不将 24、2997/125 和 24000/1001 当同一值。它不逐帧证明 CFR 或读取全部 PTS，也不证明音频内容正确；对 VFR/同步要求另做时间戳与音频检查。检查失败返回非零并写 FAIL 报告，参数非法则不开始检查。

    python scripts/frame_plan.py --fps 2997/125 --start 24 --end-exclusive 341 --cuts 55 104 135 --preserve 144:264 --output qa/frame-plan.json

输入是已经核实的 CFR 假设，不是脚本替你发现剪切。源帧零基，输出一基，结束 exclusive；source-zero-pts 默认为 0，需要时用 --source-zero-pts 指定真实源帧 0 的 PTS。保护区只标记不修改任何媒体，也不验证旧段哈希。VFR 不用此公式冒充真实时间。既有输出必须是同类报告才允许更新；仍应自行保存需要保留的旧版本。

    python scripts/package_manifest.py delivery --output delivery/manifest.json
    python scripts/package_manifest.py delivery --verify delivery/manifest.json

清单检查包含全部普通文件，拒绝符号链接，验证会抓出增加/缺失/改动项。它不自动清除私人内容或检查版权；输出不能冒指既有非清单资产。报告都使用指定位置，分发前审阅内容与打包成员。

v5 做了结构、脚本语法、本地链接、实际案例视频、帧范围与脚本负例检查，以及独立情景审查。详细验证随完整阅读版提供；没有声称在新用户机器完成从安装到整片渲染的端到端试用。相关案例见 [iPhone 8](iphone8-case.md) 与 [iPhone 4](iphone4-case.md)。
