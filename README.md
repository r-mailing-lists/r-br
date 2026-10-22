# r-br

Brazil's R discussion list, in Portuguese: R-br, "a lista Brasileira oficial de discussão do programa R", started by LEG/UFPR on 15 March 2011. In 2025 UFPR moved it to Mailman 3, where it keeps [its archive](https://listas.inf.ufpr.br/hyperkitty/list/r-br@listas.inf.ufpr.br/) and [its page](https://listas.inf.ufpr.br/postorius/lists/r-br.listas.inf.ufpr.br/).

Automated mbox archive. Updated daily via GitHub Actions from the list's Mailman 3 archive.

## Structure

- `raw/` - Monthly .mbox files, made from the Mailman 3 archive's monthly exports by `tools/update.sh`
- `processed/` - Structured JSON output from rmail-parser
- `meta.json` - List statistics

## How the files are made

`tools/hyperkitty-to-mbox.py` writes each exported month the way the list's Mailman 2 archive wrote its text files: the headers that archive kept (From, Date, Subject, Message-ID, In-Reply-To, References), the text in UTF-8, any attachment named after Mailman's "next part" line, and every address in the form that archive used, "nome em dominio". The Mailman 3 archive shows no addresses on its pages. Its export holds them in full, and they are not copied here.

The history was repaired once, in October 2026:

- 29 messages of May 2013 carry dates in June 2149, stamped while the list's server clock ran 2^32 seconds ahead. The converter moves any date past 2100 back by that much, which puts them between 4 and 7 May 2013; replies that quote three of them agree to within a minute.
- The move to Mailman 3 damaged the text of some older messages, writing letters as replacement characters or as two letters for one. `tools/repair-from-wayback.py` put back the text of 524 of them from the list's Mailman 2 archive as the Wayback Machine kept it, which is this repository's first commit.
- `raw/from-wayback.mbox` holds three messages, from 2013 and 2015, that the Mailman 3 archive lost, from the same copy.

Fetching a month of that history again (`tools/update.sh 2013-05`) would bring the damage back; run the repair again after it.

## Viewer

Browse these archives at [r-mailing-lists.thecoatlessprofessor.com](https://r-mailing-lists.thecoatlessprofessor.com/lists/r-br/)
