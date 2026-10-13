# iCloud Calendar Agent Skills

[简体中文](README.md) | [English](README.en.md)

Two connected Codex skills for recording personal events in iCloud Calendar on a Mac, registering project follow-ups, and restoring context on a chosen date. The public package contains no preconfigured accounts, real email addresses, or runtime records.

## Included skills

| Skill | Purpose |
| --- | --- |
| [icloud-calendar-write](skills/icloud-calendar-write/SKILL.en.md) | Create or update personal calendar events, set alerts, reuse a calendar binding, avoid duplicate writes, and verify saved results |
| [apple-calendar-followup](skills/apple-calendar-followup/SKILL.en.md) | Register follow-ups, read them at 00:00 in each item's timezone, retry at its specified fallback time after failure, and email the user after a successful read |

The follow-up skill loads the writing skill for calendar changes. It manages trusted state, scheduling, and email itself. Both share a local calendar configuration; the writing skill also works independently.

## Requirements

- macOS with the target iCloud calendar synchronized to the Mac Calendar app.
- A Codex environment with local tools and the necessary system calendar/automation permissions.
- A working Gmail connection for follow-up emails. First use verifies the sender and asks the user to specify their recipient address.
- An automation tool that can trigger at the required absolute times. Installing these skills does not install connectors or a scheduler, or create scheduled tasks.
- Python 3.9+ with system IANA timezone data for the time resolver. No third-party Python packages are required.

Local automation needs the computer and relevant applications to be available. Calendar interfaces have limitations around recurring-event expansion and timezone display. The skills require those capabilities to be verified and do not guarantee exact wake-ups while the computer is offline or asleep.

## Installation

Download or clone this repository, then run from its root:

```sh
mkdir -p ~/.agents/skills
cp -R skills/icloud-calendar-write skills/apple-calendar-followup ~/.agents/skills/
```

The follow-up skill depends on the writing skill, so install both under the same parent skill directory. Preserve any local changes before replacing an existing skill with the same name. See the [official OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills) for discovery locations and loading behavior.

After installation, you can invoke:

```text
$icloud-calendar-write
Schedule a personal work block in my iCloud calendar,
using the times, timezone, and alert settings supplied in this request.
```

```text
$apple-calendar-followup
Register "check feedback" for an example project on 2030-05-10,
Asia/Shanghai. Read at 00:00; if that fails, retry at 09:30 that day.
After a successful read, email the address from my initial configuration.
```

These examples illustrate the input format. Actual writes require the user's request, a real item, and the necessary configuration.

## First-time setup and reuse

The public [default-config.json](skills/apple-calendar-followup/assets/default-config.json) selects only the Mac iCloud and Gmail channels. It contains no sender address, recipient address, or calendar ID.

On first actual use, the skills verify the target iCloud calendar and current Gmail identity, obtain the user's recipient address, and save the local configuration. Later requests reuse those bindings. Project access permissions, per-item timezones, fallback times, and website-login authorizations remain separate.

The default runtime directory is CODEX_HOME/apple-calendar-followup, or ~/.codex/apple-calendar-followup when CODEX_HOME is unset:

```text
config.json        Confirmed calendar and email bindings
state/             Private item state, authorization references, schedules, and send results
```

These files contain private user data and must not be committed. Changing a default calendar or email affects new items only. Existing items keep their binding snapshots unless the user explicitly requests migration.

## Login and privacy

Prefer existing authorized connections or valid sessions. If saved Chrome credentials are needed, confirm the target website, account, stages, and permitted login counts before setting up the item. An installed chrome-saved-login skill is an optional integration. Without it, follow the bundled [login rules](skills/apple-calendar-followup/references/saved-login.en.md); the user may also log in manually.

The skills do not read or export passwords. Installation does not authorize new calendar writes, website logins, or emails to other people. Successful reading and completed work are separate states. Reading and email delivery also have separate states; uncertain send results are verified before another send to avoid duplicate notifications.

## Validation

```sh
python3 scripts/validate_bundle.py
python3 -m unittest discover -s tests -v
```

Tests cover UTC date boundaries, daylight-saving changes, nonexistent or ambiguous local times, timezone/offset mismatches, and invalid fallback times. Package validation checks skill structure, language counterparts, relative links, public defaults, and common privacy/credential leak patterns.

Calendar writes, account logins, scheduled wake-ups, and email delivery must be verified in the actual environment. These tests do not operate real accounts or send emails.

## License

[MIT](LICENSE)
