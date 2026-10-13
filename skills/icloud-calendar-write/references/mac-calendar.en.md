# Mac Calendar Interface

The native approach accesses synchronized iCloud data through the Mac Calendar application. Prefer tools in the current environment that explicitly support Apple Calendar. Otherwise, use `osascript` and Calendar.app's AppleScript interface, whose bundle ID is `com.apple.iCal`.

## Check the local scripting dictionary first

Read `/System/Applications/Calendar.app/Contents/Resources/iCal.sdef` and use its local definitions as authoritative. The verified interface currently includes:

- `calendar`: `name`, `calendarIdentifier`, `writable`, and `events`.
- `event`: `uid`, `summary`, `description`, `start date`, `end date`, `allday event`, `status`, `recurrence`, `excluded dates`, and `display alarms`.
- `display alarm`: `trigger interval` (minutes; negative values mean in advance) and `trigger date` (absolute time).

The dictionary does not expose the account source, so a calendar's name alone cannot establish that it belongs to iCloud. Verify this in the Calendar interface when necessary. It also lacks complete availability/recurring-instance expansion and an event time zone property; do not pretend these capabilities are supported.

## Reading and writing events

Locate calendars by `calendarIdentifier` and events by `uid`. The native `confirmed` status does not mean a project's follow-up work is complete.

Create an event using `make new event at end of events of targetCalendar with properties`, setting `summary`, `description`, `start date`, `end date`, and `allday event` where needed. Do not add attendees. Read before updating and preserve fields outside the requested change.

Explicitly resolve timed events to the same absolute instant before converting them to an AppleScript `date`. Do not use locale-dependent expressions such as `date "11/03/2026"`, or assume that the host time zone matches the user's. If a specific display time zone is required but the current interface does not support it, use an available EventKit tool or verify it in the interface.

For all-day events, set the start and end boundaries according to local date semantics, then read back and check the date range displayed in the calendar. Do not treat midnight in the host time zone as a trigger time in another time zone. The parent skill separately calculates the agent's actual read time.

Include events crossing the query window's boundaries when checking for conflicts: `start < window_end` and `end > window_start`. Query only the scope authorized by the user. For recurring schedules, verify actual instances with a reliable EventKit tool or the Calendar interface. If coverage is incomplete, offer candidates without claiming that a lack of conflicts has been verified. This skill creates one-time events by default and does not automatically split recurring series.

Create a calendar alert using `make new display alarm at end of display alarms of targetEvent with properties {trigger interval:-15}` for an alert 15 minutes in advance. Reuse matching alerts rather than adding duplicates. Do not use `mail alarm` as a substitute for the parent skill's email after a successful read.

Pass all user text through `on run argv` or reliable serialization; never concatenate it into shell or AppleScript source. Set a finite timeout. Do not output unrelated calendar data or secrets. After writing, read back the UID, dates, notes, and alerts.

## Permissions and partial failures

If macOS automation permission is denied, report the actual error, point the user to the relevant setting under System Settings → Privacy & Security → Automation, and wait for the user to resolve it. Do not modify privacy databases, bypass device verification, or request the Apple account password.

Writing the event, alerts, and local configuration is not atomic. After a timeout, first investigate which parts already exist, then repair within the original authorization. Do not treat an uncertain result as a failure and immediately create another event. A successful read-back proves only that the local save succeeded. Do not claim cross-device synchronization or notification delivery until verified on the other devices.
