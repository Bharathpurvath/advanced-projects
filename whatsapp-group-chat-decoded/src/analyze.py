from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd
import regex as unicode_re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "chat.txt"
REPORTS = ROOT / "reports"

# Common WhatsApp export prefixes, with and without seconds and AM/PM.
PREFIXES = [
    re.compile(r"^(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*[apAP][mM])\s+-\s+(?P<body>.*)$"),
    re.compile(r"^(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s+-\s+(?P<body>.*)$"),
    re.compile(r"^\[(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*[apAP][mM])\]\s+(?P<body>.*)$"),
    re.compile(r"^\[(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\]\s+(?P<body>.*)$"),
]
DATE_FORMATS = [
    "%d/%m/%y %I:%M %p", "%d/%m/%Y %I:%M %p", "%m/%d/%y %I:%M %p", "%m/%d/%Y %I:%M %p",
    "%d/%m/%y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%y %H:%M:%S", "%m/%d/%Y %H:%M:%S",
    "%d/%m/%y %H:%M", "%d/%m/%Y %H:%M", "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M",
    "%d-%m-%y %I:%M %p", "%d-%m-%Y %I:%M %p", "%m-%d-%y %I:%M %p", "%m-%d-%Y %I:%M %p",
    "%d-%m-%y %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%m-%d-%y %H:%M:%S", "%m-%d-%Y %H:%M:%S",
    "%d-%m-%y %H:%M", "%d-%m-%Y %H:%M", "%m-%d-%y %H:%M", "%m-%d-%Y %H:%M",
]
STOP_WORDS = set("""a an and are as at be been but by can could did do does for from had has have he her here hers him his how i if in is it its me my of on or our ours she so that the their them then there these they this to we were what when where which who will with you your yours im ive dont didnt its its wasnt werent yes no ok okay இல்ல நா நான் நீ நீங்கள் அவன் அவள் அது ஒரு இந்த அந்த என்ன எப்படி ஏன் மட்டும் தான் கூட என்று ஆனா அப்போ இப்போ என்னா""".split())
NOISE = ("<media omitted>", "image omitted", "video omitted", "audio omitted", "sticker omitted", "this message was deleted", "you deleted this message")


def parse_datetime(date: str, time: str) -> datetime | None:
    value = f"{date} {time.strip().upper()}"
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def parse_export(path: Path) -> tuple[list[dict], int]:
    rows: list[dict] = []
    skipped = 0
    current = None
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for line in text.splitlines():
        match = next((p.match(line) for p in PREFIXES if p.match(line)), None)
        if match:
            stamp = parse_datetime(match.group("date"), match.group("time"))
            if stamp is None:
                skipped += 1
                current = None
                continue
            body = match.group("body")
            if ": " in body:
                sender, message = body.split(": ", 1)
                if sender.strip():
                    current = {"timestamp": stamp, "sender": sender.strip(), "message": message}
                    rows.append(current)
                else:
                    current = None
            else:
                # System messages have no sender and are excluded from participant metrics.
                current = None
        elif current is not None:
            current["message"] += "\n" + line
    return rows, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a WhatsApp text export locally.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--timezone", default=None, help="Optional timezone name, e.g. Asia/Kolkata")
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"Export not found: {args.input}\nExport the chat without media and pass --input PATH.")
    rows, skipped = parse_export(args.input)
    if not rows:
        raise SystemExit("No participant messages parsed. Check the export format and date order.")
    synthetic_demo = args.input.name.casefold().startswith("synthetic_demo")

    REPORTS.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
    if args.timezone:
        try:
            df["timestamp"] = df["timestamp"].dt.tz_localize(args.timezone, ambiguous="NaT", nonexistent="shift_forward")
        except Exception as exc:
            raise SystemExit(f"Could not apply timezone {args.timezone}: {exc}")
    df["date"] = df.timestamp.dt.strftime("%Y-%m-%d")
    df["hour"] = df.timestamp.dt.hour
    df["weekday"] = df.timestamp.dt.day_name()
    by_sender = df.groupby("sender").size().sort_values(ascending=False).rename("messages").reset_index()
    by_hour = df.groupby("hour").size().reindex(range(24), fill_value=0).rename("messages").rename_axis("hour").reset_index()
    by_day = df.groupby("date").size().sort_values(ascending=False).rename("messages").reset_index()
    by_sender.to_csv(REPORTS / "messages_by_sender.csv", index=False)
    by_hour.to_csv(REPORTS / "messages_by_hour.csv", index=False)
    by_day.to_csv(REPORTS / "messages_by_day.csv", index=False)

    words = Counter()
    emojis = Counter()
    eligible_messages = 0
    for message in df.message:
        low = message.casefold()
        if any(noise in low for noise in NOISE):
            continue
        eligible_messages += 1
        for em in unicode_re.findall(r"\p{Extended_Pictographic}(?:\uFE0F|\u200D\p{Extended_Pictographic})*", message):
            emojis[em] += 1
        cleaned = re.sub(r"https?://\S+|www\.\S+", " ", low)
        for token in unicode_re.findall(r"[\p{L}\p{M}]+", cleaned):
            if len(token) > 1 and token not in STOP_WORDS:
                words[token] += 1
    pd.DataFrame(words.most_common(30), columns=["word", "count"]).to_csv(REPORTS / "top_words.csv", index=False)
    pd.DataFrame(emojis.most_common(30), columns=["emoji", "count"]).to_csv(REPORTS / "top_emojis.csv", index=False)

    # Approximate hand-off: a different participant posts within 60 minutes.
    gap = df.timestamp.diff().dt.total_seconds().div(60)
    handoffs = ((df.sender != df.sender.shift()) & gap.ge(0) & gap.le(60)).sum()
    hour_peak = by_hour.loc[by_hour.messages.idxmax()] if len(by_hour) else None
    busiest_date = by_day.iloc[0] if len(by_day) else None
    top_sender = by_sender.iloc[0] if len(by_sender) else None

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(by_hour.hour, by_hour.messages, color="#176B87")
    ax.set(title="Messages by hour of day", xlabel="Hour (as shown in the export)", ylabel="Messages", xticks=range(0, 24, 2))
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(REPORTS / "messages_by_hour.png", dpi=160)
    plt.close(fig)

    day_top = by_day.head(10).sort_values("messages")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(day_top.date, day_top.messages, color="#64CCC5")
    ax.set(title="10 busiest calendar days", xlabel="Messages", ylabel="Date")
    fig.tight_layout()
    fig.savefig(REPORTS / "busiest_days.png", dpi=160)
    plt.close(fig)

    demo_note = (
        "## Demonstration data notice\n\n"
        "This report uses a **synthetic example chat** created for the project. Participant labels and messages are invented; these results do not describe a real WhatsApp group. Replace the sample with your own private export to produce personal findings, and do not publish identifiable results.\n\n"
        if synthetic_demo else ""
    )
    report = f"""# Findings: WhatsApp group chat\n\n{demo_note}## Sample\n\n- Parsed participant messages: **{len(df):,}** across **{df.sender.nunique():,}** participants.\n- Date span: **{df.timestamp.min()}** to **{df.timestamp.max()}**.\n- Lines with a timestamp but an unsupported date/time format: **{skipped:,}**.\n- Messages included in word and emoji counts: **{eligible_messages:,}**.\n\n## Activity\n\n- Most active participant: **{top_sender.sender}** ({int(top_sender.messages):,} messages).\n- Busiest hour: **{int(hour_peak.hour):02d}:00** ({int(hour_peak.messages):,} messages).\n- Busiest calendar day: **{busiest_date.date}** ({int(busiest_date.messages):,} messages).\n- Approximate participant hand-offs within 60 minutes: **{int(handoffs):,}**. This is not a count of direct replies; WhatsApp export text has no reply/thread links.\n\n## Language and emoji\n\n- Frequent words are in `top_words.csv`; emoji counts are in `top_emojis.csv`. The editable stop-word list in `src/analyze.py` is only a starter and may miss Tamil forms, transliterations, names, slang, or context-specific filler words.\n\n## Privacy and limits\n\nThis report contains aggregate activity metrics. Participant names can still identify people; anonymize before sharing. The input export is not copied to reports and the script does not transmit it.\n\n## Charts\n\n![Messages by hour](messages_by_hour.png)\n\n![Busiest days](busiest_days.png)\n"""
    (REPORTS / "findings.md").write_text(report, encoding="utf-8")
    print(f"Parsed {len(df):,} messages from {df.sender.nunique()} participants. Reports saved in {REPORTS}.")


if __name__ == "__main__":
    main()
