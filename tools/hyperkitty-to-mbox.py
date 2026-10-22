"""Write a month exported from R-br's Mailman 3 archive as a pipermail-style mbox.

usage: hyperkitty-to-mbox.py EXPORT.mbox.gz OUT.mbox

HyperKitty exports each message as it arrived, with every sender's address
in full. The archive's own pages show none of them, and for its first
fourteen years the list's archive wrote them as Mailman's Portuguese text
archive does, "nome em dominio". This keeps that form: the sender, and every
address in a subject or in the text, is written "nome em dominio".

Each message keeps the headers a pipermail text archive keeps (From, Date,
Subject, Message-ID, In-Reply-To, References) and its text, in UTF-8. A
text attachment follows the text after Mailman's "next part" line; any other
attachment is named there, as Mailman's archive names one it took out. The
HTML copy most mail programs send beside the text is left out.

In May 2013 the list's server stamped 29 messages with dates in June 2149
while its clock ran 2**32 seconds ahead (a 32-bit clock that wrapped).
Replies quoting three of them agree with that offset to within a minute, so a
date past 2100 is moved back by it, which puts those 29 between 4 and 7 May
2013, after the messages they answer and before their replies.

A record with no sender, no subject and no text carries nothing to show, and
is left out. One the archive imported broken has the word "None" for its
sender and its subject, and counts as having neither.
"""
import email
import email.policy
import gzip
import html
import mailbox
import os
import re
import sys
import tempfile
from datetime import timedelta, timezone
from email.header import Header
from email.utils import format_datetime, getaddresses, parsedate_to_datetime

CLOCK_WRAP = timedelta(seconds=2**32)
ADDRESS = re.compile(r"(?<![\w.+-])([\w.+-]+)@([\w-]+(?:\.[\w-]+)+)")
NEXT_PART = "-------------- next part --------------"


def obscure(text):
    return ADDRESS.sub(r"\1 em \2", text)


def encoded(value):
    """A header value, as RFC 2047 encoded words when it is not ASCII."""
    if value.isascii():
        return value
    return Header(value, "utf-8").encode(maxlinelen=998)


def html_to_text(markup):
    markup = re.sub(r"(?is)<(script|style).*?</\1>", "", markup)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</tr>", "\n", markup)
    return html.unescape(re.sub(r"<[^>]+>", "", markup))


def part_text(part):
    try:
        return part.get_content()
    except (LookupError, UnicodeError, AssertionError):
        payload = part.get_payload(decode=True) or b""
        return payload.decode("utf-8", errors="replace")


def body_of(msg):
    """The message's text, then its attachments in Mailman's form."""
    text, extras, html_body = None, [], None
    parts = [p for p in msg.walk() if not p.is_multipart()] or [msg]
    for part in parts:
        ctype = part.get_content_type()
        attached = part.get_content_disposition() == "attachment"
        if ctype == "text/plain" and not attached and text is None:
            text = part_text(part)
        elif ctype == "text/html":
            if html_body is None:
                html_body = part_text(part)
        elif ctype.startswith("text/"):
            extras.append(f"{NEXT_PART}\n{part_text(part).rstrip()}\n")
        else:
            size = len(part.get_payload(decode=True) or b"")
            extras.append(
                f"{NEXT_PART}\nA non-text attachment was scrubbed...\n"
                f"Name: {part.get_filename() or 'not available'}\n"
                f"Type: {ctype}\nSize: {size} bytes\n"
            )
    if text is None:
        text = html_to_text(html_body) if html_body is not None else ""
    body = "\n".join([text.rstrip() + "\n"] + extras)
    body = obscure(body.replace("\r\n", "\n").replace("\r", "\n"))
    return re.sub(r"(?m)^(>*From )", r">\1", body)


def sender(msg):
    pairs = getaddresses([str(msg.get("From", ""))])
    name, addr = pairs[0] if pairs else ("", "")
    local, _, domain = addr.partition("@")
    who = f"{local} em {domain}" if domain else (local or "unknown")
    return who, obscure(name)


def empty(msg):
    blank = ("", "None")
    return (str(msg.get("From", "")).strip() in blank and str(msg.get("Subject", "")).strip() in blank
            and not body_of(msg).strip())


def convert(msg):
    who, name = sender(msg)
    try:
        when = parsedate_to_datetime(str(msg["Date"]))
    except (TypeError, ValueError, IndexError):
        when = None
    stamp = when.astimezone(timezone.utc) if when and when.tzinfo else when
    if stamp and stamp.year > 2100:
        stamp -= CLOCK_WRAP
    sep_date = (stamp.strftime("%a %b ") + f"{stamp.day:2d}" + stamp.strftime(" %H:%M:%S %Y")
                if stamp else "Thu Jan  1 00:00:00 1970")
    lines = [f"From {who}  {sep_date}", f"From: {who} ({encoded(name)})" if name else f"From: {who}"]
    if msg.get("Date"):
        lines.append(f"Date: {msg['Date']}" if stamp is None else f"Date: {format_datetime(stamp)}")
    lines.append(f"Subject: {encoded(obscure(str(msg.get('Subject', ''))))}")
    for key in ("In-Reply-To", "References", "Message-ID"):
        if msg.get(key):
            lines.append(f"{key}: {' '.join(str(msg[key]).split())}")
    return "\n".join(lines) + "\n\n" + body_of(msg) + "\n"


def main(src, dst):
    raw = gzip.open(src).read() if src.endswith(".gz") else open(src, "rb").read()
    with tempfile.NamedTemporaryFile(suffix=".mbox", delete=False) as tmp:
        tmp.write(raw)
    try:
        box = mailbox.mbox(tmp.name, factory=lambda f: email.message_from_binary_file(f, policy=email.policy.default))
        out = [convert(msg) for msg in box if not empty(msg)]
    finally:
        os.unlink(tmp.name)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("".join(out))
    print(f"{dst}: {len(out)} messages")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
