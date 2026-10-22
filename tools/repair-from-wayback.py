"""Put back the text of messages that R-br's Mailman 3 archive holds damaged.

usage: repair-from-wayback.py RAW_DIR WAYBACK_RAW_DIR

When UFPR moved the list to Mailman 3 in 2025, the import wrote some older
messages' letters as replacement characters or as two letters for one. The
list's Mailman 2 archive, as the Wayback Machine kept it (the first commit
of this repository), has those messages intact. A message whose text here is
damaged gets the text of the same message (by Message-ID) there, when that
text is not damaged; its headers stay as they are.
"""
import glob
import os
import re
import sys

SEPARATOR = re.compile(r"(?m)^(?=From \S+(?: (?:em|at) \S+)?  \w{3} \w{3} [ \d]\d \d\d:\d\d:\d\d \d{4}$)")
DAMAGE = re.compile("\ufffd|\u00c3[\u0080-\u00bf]")


def messages(path):
    return [p for p in SEPARATOR.split(open(path, encoding="utf-8").read()) if p.strip()]


def split(message):
    head, _, body = message.partition("\n\n")
    found = re.search(r"(?m)^Message-ID: (.*)$", head)
    return head, body, " ".join(found.group(1).split()) if found else None


def main(raw_dir, wayback_dir):
    clean = {}
    for path in glob.glob(os.path.join(wayback_dir, "*.mbox")):
        for message in messages(path):
            _, body, mid = split(message)
            if mid and not DAMAGE.search(body):
                clean[mid] = body
    repaired = still = 0
    for path in sorted(glob.glob(os.path.join(raw_dir, "*.mbox"))):
        out, changed = [], False
        for message in messages(path):
            head, body, mid = split(message)
            if DAMAGE.search(body):
                if mid in clean:
                    message = head + "\n\n" + clean[mid]
                    repaired += 1
                    changed = True
                else:
                    still += 1
            out.append(message)
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write("".join(out))
    print(f"{repaired} messages repaired, {still} damaged in both copies")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
