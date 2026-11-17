import os
import re
import requests

ORCID_ID = "0000-0003-0180-3676"
API_URL = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
HEADERS = {"Accept": "application/json"}
OUTPUT_DIR = "_publications"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')[:60]

def fetch_publications():
    res = requests.get(API_URL, headers=HEADERS, timeout=15)
    res.raise_for_status()
    data = res.json()

    for group in data.get("group", []):
        summary = group.get("work-summary", [{}])[0]
        title = summary.get("title", {}).get("title", {}).get("value", "Untitled")
        
        pub_date = summary.get("publication-date") or {}
        year = (pub_date.get("year") or {}).get("value") or "2026"
        month = (pub_date.get("month") or {}).get("value") or "01"
        day = (pub_date.get("day") or {}).get("value") or "01"
        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        venue = (summary.get("journal-title") or {}).get("value") or "Conference / Journal"
        work_type = summary.get("type", "journal-article")
        category = "conferences" if "conference" in work_type else "manuscripts"

        paper_url = ""
        for ext_id in summary.get("external-ids", {}).get("external-id", []):
            if ext_id.get("external-id-type") == "doi":
                doi = ext_id.get("external-id-value")
                paper_url = f"https://doi.org/{doi}"
                break
            elif ext_id.get("external-id-url"):
                paper_url = ext_id["external-id-url"].get("value", "")

        slug = slugify(title)
        filename = f"{OUTPUT_DIR}/{date_str}-{slug}.md"

        if os.path.exists(filename):
            continue

        safe_title = title.replace('"', '\\"')
        safe_venue = venue.replace('"', '\\"')

        md_content = f"""---
title: "{safe_title}"
collection: publications
category: {category}
permalink: /publication/{date_str}-{slug}
date: {date_str}
venue: "{safe_venue}"
paperurl: "{paper_url}"
---

* **Venue:** {venue} ({year})
* **ORCID / DOI Link:** [{paper_url}]({paper_url})
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)

if __name__ == "__main__":
    fetch_publications()
