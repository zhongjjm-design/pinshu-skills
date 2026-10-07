# Pinshu Skills 统一候选

这是 Aidan（品叔）维护的 14 项 Skill 公开候选，覆盖课程采集、忠实精编、知识提炼、课程编排、学习训练、内容母体、Markdown 转 PDF、写作、视觉系统、信息图、商业图解、图解学习、视频公共底座和品牌片拆解。

当前状态是候选，不是正式发布。仓库不授予一般再分发许可；第三方依赖保留各自许可证。正式发布、授权、冻结和独立审查另行完成。

## 安装和升级

统一入口仍是同一个安装脚本。首次安装和受管升级都走同一条路径：

```bash
bash install.sh --dry-run
```

真实安装时使用仓库发布的 `install.sh`。安装器只替换仍匹配所有权记录的受管包；同名目录只要存在本地修改、未标记私有内容、未知软链、权限变化或缺少所有权记录，就先拒绝，不会覆盖本机活动 Skill。

`pinshu-md2pdf` 的数字 slug 保持原样，不会被 slug 解析丢失。`pinshu-write`、`pinshu-video-core` 和 `pinshu-visual-learning` 均已进入 14 项名单。

## 私有配置边界

公开候选不包含个人 HOME 路径、账号画像、真人参考图、私有课程材料、客户素材、API key、真实学习记录或来源快照。需要品牌、账号、草稿目录、视觉参考或写作禁用词时，必须通过用户显式配置或本次任务输入传入。

`pinshu-visual-learning` 和 `pinshu-video-core` 已纳入候选。课程图解仍需清单显式启用、讲义语义通过和真实阅读证据；视频自测使用离线替身，不会把 fake API、HyperFrames 替身或缺依赖跳过说成真付费配音/真平台渲染成功。

## 本地验证

候选静态与脚本验证：

```bash
python3 scripts/validate_release.py --quick
```

安装器完整回归：

```bash
bash tests/test_installer.sh
```

PDF、视觉、影视等功能测试会按本机依赖决定通过或跳过；跳过不是业务成功。
