"""Repair the 29 messages of r-br's 2013-May archive that UFPR's mail server
stamped with dates in June 2149 while its clock was wrong.

Three replies quote the real time of a message in that block (Brazil, -0300):
  2149-06-10 08:00:05Z  quoted as  3 May 2013 22:31
  2149-06-13 21:28:10Z  quoted as  7 May 2013 11:59
  2149-06-13 21:42:43Z  quoted as  7 May 2013 12:13
One constant offset fits all three to within a minute: 2**32 seconds, the
wrap of a 32-bit clock. It moves the whole block to 4 to 7 May 2013, after
the messages it replies to and before its replies.
The Date header and the mbox separator line of each such message are moved
back by that offset; nothing else in the file changes.
"""
import re
import sys
from datetime import datetime, timedelta, timezone

OFFSET = timedelta(seconds=2**32)
SERVER = timezone(timedelta(hours=-3))
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
DAYS = "Mon Tue Wed Thu Fri Sat Sun".split()

date = re.compile(rb"^Date: \w{3}, (\d{1,2}) Jun 2149 (\d\d:\d\d:\d\d) -0000$")

def asctime(dt):
    return f"{DAYS[dt.weekday()]} {MONTHS[dt.month - 1]} {dt.day:2d} {dt:%H:%M:%S} {dt.year}"

def rfc2822(dt):
    return f"{DAYS[dt.weekday()]}, {dt.day} {MONTHS[dt.month - 1]} {dt.year} {dt:%H:%M:%S} +0000"

path = sys.argv[1]
lines = open(path, "rb").read().split(b"\n")
fixed_sep = fixed_date = 0
for i, line in enumerate(lines):
    m = date.match(line)
    if m:
        t = datetime.strptime(f"2149-06-{int(m[1]):02d} {m[2].decode()}", "%Y-%m-%d %H:%M:%S")
        lines[i] = b"Date: " + rfc2822(t - OFFSET).encode()
        fixed_date += 1
        continue
    if line.startswith(b"From ") and line.endswith(b" 2149"):
        parts = line.rsplit(b" ", 5)
        t = datetime.strptime(b" ".join(parts[-4:]).decode(), "%b %d %H:%M:%S %Y")
        utc = (t + timedelta(hours=3)) - OFFSET
        local = utc.replace(tzinfo=timezone.utc).astimezone(SERVER)
        head = line[: len(line) - len(b" ".join(parts[-5:]))]
        lines[i] = head + asctime(local).encode()
        fixed_sep += 1
open(path, "wb").write(b"\n".join(lines))
print(f"{path}: {fixed_date} Date headers and {fixed_sep} separator lines moved back by {OFFSET}")
