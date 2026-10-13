# iCloud Calendar Agent Skills

[简体中文](README.md) | [English](README.en.md)

两个可联动的 Codex 技能，用于在 Mac 的 iCloud 日历中记录个人日程、标记项目待办，并在指定日期恢复跟进。公开版本不包含任何预先绑定的账户、真实邮箱或运行记录。

## 包含的技能

| 技能 | 用途 |
| --- | --- |
| [icloud-calendar-write](skills/icloud-calendar-write/SKILL.md) | 创建和更新个人日历事件，设置提醒，复用日历绑定，避免重复写入并读回核验 |
| [apple-calendar-followup](skills/apple-calendar-followup/SKILL.md) | 登记待办，按每项时区在指定日期 00:00 读取，失败时在精确时间重试，成功后发送邮件提醒 |

跟进技能加载写入技能处理日历写入；它自己负责可信状态、调度和邮件。两者共用本机日历配置。写入技能可单独使用。

## 运行前提

- macOS，且目标 iCloud 日历已同步到 Mac“日历”应用。
- 可使用本机工具的 Codex 环境，以及系统允许的日历/自动化权限。
- 跟进邮件需要可用的 Gmail 连接；首次使用核验发件身份，并由使用者指定自己的收件邮箱。
- 自动读取需要环境提供能按指定绝对时间触发的自动化工具。安装技能不会安装连接器或调度器，也不会自行创建定时任务。
- 时间换算脚本需要 Python 3.9+ 和系统 IANA 时区数据，无第三方 Python 包依赖。

本机自动化需要电脑及相关应用可用。日历接口的周期实例展开、事件时区显示等能力有限，技能会要求核实实际支持情况，不能保证离线或休眠时精确唤醒。

## 安装

下载或克隆本仓库，在仓库根目录执行：

```sh
mkdir -p ~/.agents/skills
cp -R skills/icloud-calendar-write skills/apple-calendar-followup ~/.agents/skills/
```

跟进技能依赖写入技能，两者应放在同一技能父目录下。已有同名技能时先保留需要的本地改动。具体发现位置及加载行为参见 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。

安装后可调用：

```text
$icloud-calendar-write
在我的 iCloud 日历中安排一个个人工作时段，时间、时区和提醒按本次说明设置。
```

```text
$apple-calendar-followup
为示例项目登记“检查反馈”：2030-05-10，Asia/Shanghai，
00:00 读取；失败后当天 09:30 重试；成功后发到我首次配置的邮箱。
```

示例只说明输入格式，实际写入前需要使用者明确要求，并提供真实事项和所需配置。

## 首次配置与后续复用

公开默认文件 [default-config.json](skills/apple-calendar-followup/assets/default-config.json) 只指定 Mac iCloud 与 Gmail 通道，不含发件邮箱、收件邮箱或日历 ID。

首次实际使用时，技能核实目标 iCloud 日历和当前 Gmail 身份，取得使用者指定的收件地址，再保存本机配置。以后直接复用；项目资料权限、事项时区、备用时间及网站登录授权分别记录。

默认运行目录为 CODEX_HOME/apple-calendar-followup；未设置 CODEX_HOME 时为 ~/.codex/apple-calendar-followup：

```text
config.json        已确认的日历和邮件绑定
state/             私人的待办状态、授权引用、调度和发送结果
```

这些文件属于使用者的私人数据，不能提交到仓库。修改默认日历或邮箱仅影响新事项；迁移旧事项须明确要求，旧事项默认使用各自的绑定快照。

## 登录与隐私

优先使用已有授权连接或有效会话。需要使用 Chrome 保存凭据时，在设置待办前确认目标网站、账户、阶段及次数。可选集成使用者已安装的 chrome-saved-login；没有该技能时，遵循仓库内的 [登录规则](skills/apple-calendar-followup/references/saved-login.md)，使用者也可以自行登录。

技能不读取或导出密码。安装不会授权新的日历写入、网站登录或给其他人发信。成功读取与工作完成分开记录；读取与邮件状态也分开，发送结果不明时先核验，避免重复提醒。

## 验证

```sh
python3 scripts/validate_bundle.py
python3 -m unittest discover -s tests -v
```

测试覆盖跨日 UTC 换算、夏令时变化、不存在/重复的本地时间、时区与偏移不匹配及非法重试时间。包校验检查技能结构、语言对应文件、相对链接、默认配置和常见隐私/凭据泄漏模式。

日历写入、账户登录、自动化唤起和邮件送达需要在实际环境验证；这里的测试不会操作真实账户或发送邮件。

## License

[MIT](LICENSE)
