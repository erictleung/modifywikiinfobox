#!/usr/bin/env python3

"""
Help audit, remove, and update musician infoboxes.

https://en.wikipedia.org/wiki/Category:Pages_using_infobox_musical_artist_with_associated_acts
"""

import re
import requests

import mwparserfromhell
from bs4 import BeautifulSoup as bs


def get_info_box(url):
    """
    Pull Infobox information
    """
    response = requests.get(search, timeout=10)
    wikicode = mwparserfromhell.parse(response.content)



# pylint: disable=line-too-long
response = requests.get(
        url="https://en.wikipedia.org/wiki/Category:Pages_using_infobox_musical_artist_with_associated_acts",  # noqa: E501
        timeout=10,
)
soup = bs(response.content, "html.parser")

# Extract only links from the "Pages in category" and not unnecessary Wiki
# links
all_pages = soup.find("div", class_="mw-category-group").find_all("a")

# Extract text that can be inserted into a Wikipedia URL to get the page
music_pages = []
p = re.compile(r"^\/wiki\/([A-Za-z_()%0-9]*)")
for link in all_pages:
    if p.match(link.get("href")) is not None:
        href = link.get("href")
        music_pages.append(p.match(href).group(1))

print(f"Parsed {len(music_pages)} pages.")

# Setup to extract the raw Wikitext
WIKI_BASE = "https://en.wikipedia.org/w/index.php?title="
WIKI_END = "&action=raw&ctype=text"

# Just use one page for example
search = WIKI_BASE + music_pages[0] + WIKI_END
print(f"Searching for {search}")

response = requests.get(search, timeout=10)
wikicode = mwparserfromhell.parse(response.content)

# Pseudocode:
# Loop through initial pages
# Extract associated_acts value
# Extract Wikilinks and find their pages
# Go and extract past members and former members from Infobox
# Open up page
# Print out copy-paste information for new values of:
# - current_member_of=
# - past_member_of=
# - spinoff_of=
# - spinoffs=
# Pause to make manual changes
print("Printing top node.")
print(wikicode.get_sections(include_lead=True))

for template in wikicode.filter_templates():
    if template.name.matches("Infobox musical artist"):
        print("Getting the associated_acts= values:")
        print(template.get("associated_acts").value.filter_wikilinks())
        ac = template.get("associated_acts").value.filter_wikilinks()
        for link in ac:
            title = link.title
            print(title)
