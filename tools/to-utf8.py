"""Write a pipermail text archive as UTF-8.

UFPR's monthly files hold each message in the bytes it arrived in, so one
file mixes UTF-8 messages with Latin-1 ones and is valid in neither. A line
that is valid UTF-8 is kept as it is; any other line is read as Windows-1252
(Latin-1 with the printable characters Windows puts in 0x80 to 0x9F).
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
out, recoded = [], 0
for line in open(src, "rb").read().split(b"\n"):
    try:
        line.decode("utf-8")
    except UnicodeDecodeError:
        line = line.decode("cp1252", errors="replace").encode("utf-8")
        recoded += 1
    out.append(line)
open(dst, "wb").write(b"\n".join(out))
print(f"{dst}: {recoded} lines read as Windows-1252")
