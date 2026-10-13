#!/usr/bin/env python3
"""Resolve per-item midnight and fallback times without external side effects."""

import argparse
import json
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


UTC = timezone.utc


def parse_offset(value):
    match = re.fullmatch(r"([+-])([0-9]{2}):([0-9]{2})", value)
    if not match:
        raise ValueError("UTC offset must be +HH:MM or -HH:MM")
    hours, minutes = int(match[2]), int(match[3])
    if hours > 23 or minutes > 59:
        raise ValueError("UTC offset is out of range")
    delta = timedelta(hours=hours, minutes=minutes)
    return delta if match[1] == "+" else -delta


def localize(naive, zone, chosen_offset=None):
    candidates = {}
    for fold in (0, 1):
        local = naive.replace(tzinfo=zone, fold=fold)
        absolute = local.astimezone(UTC)
        restored = absolute.astimezone(zone)
        if restored.replace(tzinfo=None) == naive:
            candidates[absolute] = restored
    values = list(candidates.values())
    if not values:
        raise ValueError(f"Nonexistent local time: {naive.isoformat()} in {zone.key}")
    if chosen_offset is not None:
        values = [item for item in values if item.utcoffset() == chosen_offset]
        if not values:
            raise ValueError("Supplied UTC offset does not match the named timezone at this time")
    if len(values) > 1:
        raise ValueError(f"Ambiguous local time: {naive.isoformat()}; specify an explicit UTC offset")
    return values[0]


def resolve(read_date, zone_name, retry_value, midnight_offset=None):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", read_date):
        raise ValueError("Read date must be YYYY-MM-DD")
    if zone_name != "UTC" and "/" not in zone_name:
        raise ValueError("Use a full IANA timezone such as Europe/Paris, not an abbreviation")
    day = date.fromisoformat(read_date)
    zone = ZoneInfo(zone_name)
    first = localize(
        datetime.combine(day, time.min),
        zone,
        parse_offset(midnight_offset) if midnight_offset is not None else None,
    )
    if not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}"
        r"(?::[0-9]{2})?(?:[+-][0-9]{2}:[0-9]{2})?",
        retry_value,
    ):
        raise ValueError("Retry must be YYYY-MM-DDTHH:MM[:SS][+HH:MM or -HH:MM]")
    parsed = datetime.fromisoformat(retry_value)
    retry = localize(parsed.replace(tzinfo=None), zone, parsed.utcoffset())
    if retry.astimezone(UTC) <= first.astimezone(UTC):
        raise ValueError("Retry must be later than the item's first local midnight")
    return {
        "read_date": day.isoformat(),
        "timezone": zone.key,
        "first_read_at": first.isoformat(timespec="seconds"),
        "retry_at": retry.isoformat(timespec="seconds"),
        "first_read_utc": first.astimezone(UTC).isoformat(timespec="seconds"),
        "retry_utc": retry.astimezone(UTC).isoformat(timespec="seconds"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Read date YYYY-MM-DD")
    parser.add_argument("--timezone", required=True, help="IANA timezone")
    parser.add_argument("--retry", required=True, help="Full local fallback datetime")
    parser.add_argument("--midnight-offset", help="Explicit offset if local midnight repeats")
    args = parser.parse_args(argv)
    try:
        result = resolve(args.date, args.timezone, args.retry, args.midnight_offset)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
