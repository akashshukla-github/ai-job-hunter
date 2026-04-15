import requests
from bs4 import BeautifulSoup


BASE_URL = "https://internshala.com"
DATA_SCIENCE_URL = (
    f"{BASE_URL}/internships/data-science-internship/"
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
}
TIMEOUT = 15


def fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def _clean_text(node):
    if not node:
        return ""
    return node.get_text(" ", strip=True)


def _build_link(href):
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return f"{BASE_URL}{href}"


def _extract_locations(card):
    selectors = [
        ".row-1-item.locations a",
        ".locations a",
        ".location_link",
        ".locations span",
    ]

    locations = []
    seen = set()

    for selector in selectors:
        for node in card.select(selector):
            value = _clean_text(node)
            if value and value not in seen:
                seen.add(value)
                locations.append(value)

    return ", ".join(locations)


def _extract_skills(card):
    selectors = [
        ".round_tabs_container .round_tabs",
        ".round_tabs",
        ".skills span",
        ".skill_names span",
    ]

    skills = []
    seen = set()

    for selector in selectors:
        for node in card.select(selector):
            value = _clean_text(node)
            if value and value not in seen:
                seen.add(value)
                skills.append(value)

    return skills


def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(".individual_internship, .individual_internship_visibility")
    jobs = []

    for card in cards:
        try:
            title_node = (
                card.select_one("h3.job-internship-name")
                or card.select_one("a.job-title-href")
            )
            company_node = (
                card.select_one("p.company-name")
                or card.select_one(".company-name")
            )
            link_node = card.select_one("a.job-title-href")

            title = _clean_text(title_node)
            company = _clean_text(company_node)
            location = _extract_locations(card)
            skills = _extract_skills(card)
            link = _build_link(link_node.get("href") if link_node else "")

            if not title or not company or not link:
                continue

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "skills": skills,
                    "link": link,
                    "source": "internshala",
                }
            )
        except Exception:
            continue

    return jobs


def get_jobs():
    html = fetch_page(DATA_SCIENCE_URL)
    return parse_jobs(html)


if __name__ == "__main__":
    try:
        jobs = get_jobs()
        for index, job in enumerate(jobs[:5], start=1):
            print(f"{index}. {job['title']}")
            print(f"   Company : {job['company']}")
            print(f"   Location: {job['location'] or 'N/A'}")
            print(f"   Skills  : {', '.join(job['skills']) if job['skills'] else 'N/A'}")
            print(f"   Link    : {job['link']}")
            print(f"   Source  : {job['source']}")
            print()
    except requests.RequestException as error:
        print(f"Failed to fetch Internshala jobs: {error}")
