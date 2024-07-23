#!/usr/bin/env python3

"""
Help audit, remove, and update musician infoboxes.

Usage: python3 check_associated_acts.py

https://en.wikipedia.org/wiki/Category:Pages_using_infobox_musical_artist_with_associated_acts

Article cases:
- Musician with associated acts as
  - Other musicians (remove)
  - Bands (can be updated to current_member_of or past_member_of)
- Bands with associated acts as
  - Musicians (can be updated to current_members or past_member_of, check if
    those exist)
  - Bands (can be updated to spinoff_of or spinoffs)
"""

import random
import re
import webbrowser

from bs4 import BeautifulSoup as bs
import mwparserfromhell
import requests


def get_info_box(url):
    """
    Pull Infobox information

    :param str url: whole URL for Wikipedia page to get infobox from
    :return: string of just infobox

    Examples
    ========
    >>> BASE= "https://en.wikipedia.org/w/index.php/?title="
    >>> page = "The_Beatles"
    >>> SUFFIX = "&action=raw&ctype=text"
    >>> get_infobox(BASE + page + SUFFIX)
    """
    r = requests.get(url, timeout=10)
    wc = mwparserfromhell.parse(r.content)

    for t in wc.filter_templates():
        if t.name.matches("Infobox musical artist"):
            return t

    print("No infobox found")
    return ""


def construct_wiki_url(page_title, source=True):
    """
    Create Wikipedia URL using page title

    This is to help create a valid URL to open a Wikipedia page using the web
    browser. It takes the title's page.
    """
    # Setup to extract the raw Wikitext
    wiki_base = "https://en.wikipedia.org/w/index.php?title="
    wiki_src_end = "&action=raw&ctype=text"
    wiki_edit_end = "&veaction=editsource"

    if source:
        return f"{wiki_base}{str(page_title)}{wiki_src_end}"

    return f"{wiki_base}{str(page_title)}{wiki_edit_end}"


def get_wiki_markup(page):
    """
    Get Wiki markup

    Given a Wikipedia URL, request Wiki page and return its Wiki markup code.
    """
    page_response = requests.get(page, timeout=10)
    return mwparserfromhell.parse(page_response.content)


def get_param_wikilinks(template_obj, param):
    """
    Return Wikilinks from template parameter
    """
    print(f"Getting the {param}= values:")
    try:
        wiki_links = (
            template_obj
            .get(f"{param}")
            .value
            .filter_wikilinks()
        )
    except ValueError:
        wiki_links = "None"

    return wiki_links


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

# Just use one page for example at random
search = construct_wiki_url(random.choice(music_pages))
print(f"Searching for {search}")

# Request and pull Wiki markup code
wikicode = get_wiki_markup(search)

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

# print("Printing top node.")
# print(wikicode.get_sections(include_lead=True))

for template in wikicode.filter_templates():

    # Just focus on the musical artitist infobox
    if template.name.matches("Infobox musical artist"):
        ac = get_param_wikilinks(template, "associated_acts")
        print(ac)

        # Loop through links in associated_acts for page
        for link in ac:

            title = link.title
            print(title)
            search = construct_wiki_url(title)
            webbrowser.open(search)

            # Get information about what kind of article it is, e.g., band or
            # individual
            inner_wikicode = get_wiki_markup(search)

            # Loop through values of each page
            for template in inner_wikicode.filter_templates():
                if template.name.matches("Infobox musical artist"):

                    print(get_param_wikilinks(template, "current_member_of"))
                    print(get_param_wikilinks(template, "past_member_of"))
                    print(get_param_wikilinks(template, "spinoff_of"))
                    print(get_param_wikilinks(template, "spinoffs"))

            input("Enter any key to continue...")
