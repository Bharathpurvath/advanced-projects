# Your WhatsApp group chat, decoded

Analyze a WhatsApp **text-only** group export locally: activity by sender, hour and day; common words; emoji counts; and approximate conversational hand-offs. The raw export stays on your computer and is excluded from Git.

## Input

On your phone, open the group chat, choose **Export chat → Without media**, and place the `.txt` file at `data/chat.txt`. Do not share the export publicly: it can contain names, phone numbers, and private messages. This tool processes the file locally and writes only aggregate tables and charts.

The parser supports common Android lines such as `31/12/23, 9:41 pm - Name: message` and common iOS lines such as `[31/12/23, 21:41:02] Name: message`. It handles multiline messages by attaching continuation lines to the preceding message. Unrecognized timestamp formats are skipped and counted; check the warning in the report.

## Run

```powershell
python -m pip install -r requirements.txt
python src/analyze.py --input data/chat.txt
```

Optional: `--timezone Asia/Kolkata` assigns a timezone to timestamps that have none. Use the timezone where the chat activity occurred. The script does not upload or transmit data.

## Outputs

- `reports/messages_by_sender.csv`
- `reports/messages_by_hour.csv`
- `reports/messages_by_day.csv`
- `reports/top_words.csv`
- `reports/top_emojis.csv`
- `reports/findings.md` and charts

## Public demonstration

`data/synthetic_demo_chat.txt` is a small, entirely fictional example used to demonstrate the parser and reports. The published findings and charts are generated from that synthetic sample; they say nothing about a real group. Your own chat export is private input: analyze it locally and review/anonymize outputs before sharing.

## Method notes

- Group exports do not expose actual reply/thread links. “Conversational hand-off” is only an approximation: a message by a different sender within 60 minutes of the previous message. It is not a reply count.
- The busiest day is a calendar date, using the export's local timestamps. Hour-of-day summaries use the hour shown in the export.
- Word counts normalize case and strip URLs/punctuation. The stop-word list is a small editable starter list for English and common Tamil transliterations; review it before interpreting results. Tamil script words are preserved and counted as tokens.
- Deleted-message placeholders, system notices, and attachment placeholders are left out of word-frequency analysis but remain part of total message counts when they have a sender and timestamp.
- Names in aggregate tables may identify participants. Review and anonymize these files before sharing or publishing.

## Git hygiene

Keep `data/chat.txt` and any identifying output private. `.gitignore` excludes the input file and generated reports by default. If publishing, share only reviewed, anonymized aggregates and explain the sample and its limitations.
