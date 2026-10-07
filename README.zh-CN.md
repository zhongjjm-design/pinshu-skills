# Pinshu Skills

Aidan（品叔）维护的14项公开试用Skill，覆盖课程采集、忠实精编、知识提炼、课程编排、学习训练、内容母体、Markdown转PDF、写作、视觉系统、信息图、商业图形、图解学习、视频公共底座和品牌片拆解。

**中文是主要操作规则，英文README是国际化入口；两者使用同一套脚本、状态合同和测试，不维护功能不同的中英文管线。**

## 下载与安装

macOS或Linux（含WSL）需先有Bash、Git、rsync、Python 3。首次安装和受管升级使用同一条命令：

```bash
curl -fsSL https://raw.githubusercontent.com/zhongjjm-design/pinshu-skills/main/install.sh | bash
```

执行远程脚本前，应先阅读仓库中的[安装脚本](install.sh)。安装完成后重启Agent客户端。

包的共享位置为 `~/.agents/skills/`。安装器自动处理Claude的加载入口；其他Agent需按各自支持的Skill发现目录读取共享包，不必复制出另一套功能源。安装不自动提供模型账号、API额度或全部外部渲染依赖。

### 先预览，不写本机

```bash
curl -fsSL https://raw.githubusercontent.com/zhongjjm-design/pinshu-skills/main/install.sh | bash -s -- --dry-run
```

预览不创建锁、安装缓存、暂存、备份或归属回执，不做完整远端下载验证。真实安装会验证来源、名单与配套完整性。

### 已有旧包或本机定制

只有匹配安装归属记录的受管包才正常升级。已有同名包但没有归属证明，或者新增、修改、删除了文件/相关权限/链接，安装器默认拒绝，不会因为“做了备份”就覆盖你的增强。

旧官方版本确实未定制、克隆及包内容能精确证明一致时，可以明确选择 `--adopt-legacy` 接管；不要给定制包盲加此参数。拒绝时先保留原包，再审阅迁移方案。

失败回滚覆盖克隆、包目录、归属回执及必需客户端链接。旧内容保存在提示的可恢复备份位置。此命令不是后台自动更新。

## 14项能力

| 分组 | Skill |
|---|---|
| 课程与知识资产 | pinshu-course-capture、pinshu-transcript、pinshu-distill、pinshu-course、pinshu-study、pinshu-content-assets、pinshu-md2pdf |
| 视觉与品牌表达 | pinshu-visual-system、pinshu-infographic、pinshu-business-graphics、pinshu-film-teardown |
| 中文商业写作 | pinshu-write |
| 视频与图解配套 | pinshu-video-core、pinshu-visual-learning |

`pinshu-md2pdf`的数字保持原样。配套包随统一安装交付，不需要在不同Agent的仓库中分别拼装。

安装后可对Agent说：

> 使用pinshu-write，把我给的选题和材料写成中文商业分析文章，先提炼判断和大纲，再起草、审稿。

> 使用pinshu-course-capture，把这门课程整理成知识资产，先推荐用途、审核方式与最终资产，确认后执行。

## 私有配置与使用边界

公开包不带个人账号画像、真人参考图、私有课程/客户材料、API钥匙或机器路径。品牌、角色、草稿目录和禁词等通过明确配置或任务输入传入；升级不覆盖独立私有配置。

图解需要已验收讲义、用户样稿批准及真实阅读证据。脚本检查不代替图形语义与Obsidian实际阅读。影视需FFmpeg、Node/HyperFrames、相应Python音频依赖、授权素材和各人自己的配音API访问；离线合成素材与服务替身自测不等于真付费配音或实际平台成片验收。

PDF默认用WeasyPrint，不自动启动本机Chrome。Chrome转换需要明确指定，Chrome专项测试也必须明确开启；不要通过 `--no-sandbox` 绕过安全保护。

当前为公开试用版。已执行的测试和仍需按本机环境检查的能力分开看待，不承诺所有平台、原生PPTX或外部付费服务均已实测。

## 使用许可

按[LICENSE](LICENSE)，允许个人与团队内部使用、复制和修改，包括内部商业工作；用这些Skill产生的文章、文档、图片、视频等可商业使用。不授对外转卖或再分发Skill本身及修改版本的权利，扩大范围需另获许可。第三方原许可证与服务条款继续适用。这是受限源码可见许可，不是MIT或OSI开源许可，详见[NOTICE](NOTICE.md)。

## 本地验证

```bash
python3 scripts/validate_release.py --quick
bash tests/test_installer.sh
```

通过、失败、跳过分别报告；跳过测试不是业务成功。
