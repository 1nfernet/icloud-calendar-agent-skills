# Mac 日历接口

原生路线通过 Mac“日历”应用访问已同步的 iCloud 数据。优先使用当前环境明确支持 Apple 日历的工具；否则使用 osascript 和 Calendar.app 的 AppleScript 接口，bundle ID 为 com.apple.iCal。

## 先核对本机字典

读取 /System/Applications/Calendar.app/Contents/Resources/iCal.sdef，以本机定义为准。当前已核对的接口包括：

- calendar：name、calendarIdentifier、writable、events。
- event：uid、summary、description、start date、end date、allday event、status、recurrence、excluded dates、display alarms。
- display alarm：trigger interval（分钟，负数提前）及 trigger date（绝对时间）。

字典不暴露账户来源，不能仅靠日历名称断定属于 iCloud；必要时通过日历界面核实。没有完整忙闲/周期实例展开或事件时区属性，不能假装支持这些能力。

## 读写事件

日历用 calendarIdentifier 定位，事件用 uid 定位。原生 confirmed 状态不代表项目待办工作已完成。

创建使用 make new event at end of events of targetCalendar with properties，设置 summary、description、start date、end date 和必要的 allday event。不添加参加者。更新前读取，保留未涉及的字段。

明确解析时间型事件为同一绝对时刻，再转换为 AppleScript date。不要使用依赖地区格式的 date "11/03/2026"，也不要假定宿主时区等于用户时区。需要特定显示时区而当前接口不支持时，使用可用的 EventKit 工具或界面核实。

全天事件按本机日期语义设置起止边界并读回检查日历显示的日期范围，不将宿主时区的午夜当作另一时区的触发时刻。父技能负责另外计算实际 agent 读取时刻。

检查冲突时包含跨窗口边界的事件：start < 窗口结束 且 end > 窗口开始。只检索用户允许范围。涉及周期安排时用可靠的 EventKit 工具或日历界面核实实际实例；覆盖不完整时给出候选，不宣称已验证无冲突。本技能默认单次事件，不自动拆分周期系列。

日历提示使用 make new display alarm at end of display alarms of targetEvent with properties {trigger interval:-15} 表示提前 15 分钟。相同提醒复用，不重复累加。不用 mail alarm 代替父技能的读取成功邮件。

所有用户文本通过 on run argv 或可靠序列化传入，不能拼接进 shell/AppleScript 源码。设置有限超时；不输出无关日历数据或秘密。写入后读回 UID、日期、备注和提醒。

## 权限与部分失败

macOS 自动化权限被拒绝时报告实际错误，告知系统设置 → 隐私与安全 → 自动化的相关位置，等待用户处理；不修改隐私数据库或绕过设备验证，不索取 Apple 账户密码。

事件、提醒和本机配置写入不是原子操作。超时后先查证已存在的部分，再在原授权内修复；不能把不确定结果当成失败后直接新建。读回成功只证明本机保存成功，未核实其他设备前不声称完成跨设备同步或通知送达。
