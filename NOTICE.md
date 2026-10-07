# Attribution and dependency notice / 归属与依赖说明

Original Pinshu Skills capability ownership: **Aidan (Pinshu / 品叔)**. The repository's original material uses the restricted internal-use license in [LICENSE](LICENSE), not MIT. Implementation assistance by AI agents does not create an additional original owner. Existing third-party copyright and license notices remain applicable and must be retained.

原创能力归属为Aidan（品叔）。本仓原创材料允许个人、团队内部使用和修改，包括内部商业工作；文章、文档、图片和视频等产出可商业使用。不授予对外转卖或再分发Skill本身及修改版的权利；扩大使用范围需另获许可。平台自身授予的必要查看/fork权利和第三方独立许可不受此说明限制。完整条款以LICENSE为准。这不是MIT或OSI开源许可。

## External runtime dependencies

Skills can invoke external tools and services; the original workflow license does not relicense them. Installing these Skills does not by itself install every external dependency or grant model/API access. Each installer supplies their own lawful access and any required API keys; no publisher credentials are distributed.

Dependency declarations and installation checks are in the relevant Skill and its doctor/self-test. Video dependencies include FFmpeg, HyperFrames, BaoCut, NumPy, SoundFile, Pillow, librosa, and optionally Demucs. PDF and visual tools can depend on WeasyPrint, markdown2, fonts and rendering programs. They remain subject to their respective upstream licenses and provider terms. FFmpeg licensing depends on the particular build and enabled components. Do not infer redistribution permission for downloaded tools, fonts or media from this repository's license.

This notice is not a claim that every dependency is bundled, installed, verified on every OS, or available without payment. Tests using synthetic inputs or service substitutes must be reported as such, not as real paid synthesis or public production evidence.

No private identity masters, publisher API keys, raw course recordings, customer materials, or machine-specific configuration are licensed or distributed by this repository merely because a workflow can reference them. Users must supply authorized inputs explicitly.
