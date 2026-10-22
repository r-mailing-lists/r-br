# r-br

Brazil's R discussion list, in Portuguese: R-br, "a lista Brasileira oficial de discussão do programa R", started by LEG/UFPR on 15 March 2011.

The list was hosted at listas.inf.ufpr.br, which no longer answers. This archive was rebuilt in October 2026 from the monthly text files that the Internet Archive's Wayback Machine captured from the list's pipermail archive: every month from March 2011 to June 2025, 20,630 messages. June 2025 was captured on its third day, and nothing later was captured. The archive is not updated.

## Structure

- `raw/` - Monthly .mbox files, from the Wayback Machine's copies of [http://listas.inf.ufpr.br/pipermail/r-br/](https://web.archive.org/web/2025/http://listas.inf.ufpr.br/pipermail/r-br/) (each capture is listed in `tools/wayback-captures.tsv`)
- `processed/` - Structured JSON output from rmail-parser
- `meta.json` - List statistics

Addresses appear as the list's archive showed them, in Mailman's Portuguese form ("nome em dominio").

## Changes from the captured files

The scripts in `tools/` made two changes to the captured files, and nothing else.

- `to-utf8.py` writes each file as UTF-8. UFPR's files kept each message in the bytes it arrived in, so one file mixes UTF-8 messages with Latin-1 ones. A line that is valid UTF-8 is kept as it is, and any other line is read as Windows-1252.
- `fix-2149.py` dates 29 messages of May 2013 again. The list's server stamped them with dates in June 2149 while its clock ran 2^32 seconds ahead. Replies that quote three of them agree with that offset to within a minute, and they now fall between 4 and 7 May 2013 (UTC), after the messages they answer and before their replies.

## Viewer

Browse these archives at [r-mailing-lists.thecoatlessprofessor.com](https://r-mailing-lists.thecoatlessprofessor.com/lists/r-br/)
