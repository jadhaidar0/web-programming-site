"""
Web Programming — Flask application.
Serves the portfolio home page and the Week 2 history pages (hand-made and AI).
"""

import html
import os
import re
from urllib.parse import urlparse

from flask import Flask, render_template, request, url_for

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Site data, defined once and shared by every template
# ---------------------------------------------------------------------------

# Main menu: (endpoint, label). Used by the header and the footer.
MENU = [
    ("home", "Home"),
    ("internet_history", "Internet"),
    ("web_history", "Web"),
    ("internet_history_ai", "Internet (AI)"),
    ("web_history_ai", "Web (AI)"),
    ("submit_profile", "Profile"),
]

# The four history pages. Titles and descriptions live here so the pages,
# the home page cards and the related-page links all use the same text.
#
#   short   the two-word label printed large on the home page tile
#   image   the cover picture in static/img/, with the alt text that
#           describes it for screen readers and when images fail to load
#   tint    which colour the tile is painted (see the .tile--* rules in CSS)
HISTORY_PAGES = {
    "internet_history": {
        "title": "History of the Internet",
        "short": "The Internet",
        "description": "A verified, sourced timeline of the history of the Internet, "
                       "from packet switching to IPv6 reaching the majority in 2026.",
        "topic": "internet",
        "author": "hand",
        "tint": "soft",
        "image": "img/internet-cover.webp",
        "alt": "Paper-craft illustration: a globe laced with network lines, "
               "linked to four early computer terminals.",
    },
    "web_history": {
        "title": "History of the World Wide Web",
        "short": "The Web",
        "description": "A verified, sourced timeline of the history of the World Wide Web, "
                       "from ENQUIRE at CERN to the encrypted web of 2026.",
        "topic": "web",
        "author": "hand",
        "tint": "mint",
        "image": "img/web-cover.webp",
        "alt": "Paper-craft illustration: stacked browser windows joined by "
               "golden hyperlink threads.",
    },
    "internet_history_ai": {
        "title": "History of the Internet (AI-generated)",
        "short": "Internet, by AI",
        "description": "An AI-generated timeline of the history of the Internet, "
                       "built from verified research for GIN446.",
        "topic": "internet",
        "author": "ai",
        "tint": "sun",
        "image": "img/internet-ai-cover.webp",
        "alt": "Paper-craft illustration: undersea fibre-optic cables rising to "
               "a coastline, with a satellite and server racks.",
    },
    "web_history_ai": {
        "title": "History of the World Wide Web (AI-generated)",
        "short": "Web, by AI",
        "description": "An AI-generated timeline of the history of the World Wide Web, "
                       "built from verified research for GIN446.",
        "topic": "web",
        "author": "ai",
        "tint": "pink",
        "image": "img/web-ai-cover.webp",
        "alt": "Paper-craft illustration: a web page pulled apart into floating "
               "layers, threaded together with gold ribbons.",
    },
}


def related_pages(endpoint):
    """For a history page: its counterpart (same topic, other author) and the
    other topic by the same author."""
    page = HISTORY_PAGES[endpoint]
    counterpart = other_topic = None
    for other, info in HISTORY_PAGES.items():
        if other == endpoint:
            continue
        if info["topic"] == page["topic"]:
            counterpart = other
        elif info["author"] == page["author"]:
            other_topic = other
    return counterpart, other_topic


@app.context_processor
def asset_version():
    """Add a ?v= stamp to static files, taken from the file's own timestamp.

    Browsers and CDNs cache /static/style.css for a long time, so a redeploy
    would otherwise still serve the old file. Changing the file changes the
    stamp, which makes it a new address that nothing has cached yet.
    """

    def static_url(filename):
        try:
            stamp = int(os.path.getmtime(os.path.join(app.static_folder, filename)))
        except OSError:
            stamp = 0
        return url_for("static", filename=filename, v=stamp)

    return {"static_url": static_url}


@app.context_processor
def site_data():
    return {"menu": MENU, "history_pages": HISTORY_PAGES, "related_pages": related_pages}


# ---------------------------------------------------------------------------
# Template filters
# ---------------------------------------------------------------------------

@app.template_filter("slug")
def slug(text):
    """'"Flag Day": NCP to TCP/IP' -> 'flag-day-ncp-to-tcp-ip'"""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@app.template_filter("domain")
def domain(url):
    """'https://www.rfc-editor.org/rfc/rfc791.html' -> 'rfc-editor.org'"""
    host = urlparse(url).netloc
    return host[4:] if host.startswith("www.") else host


RULER_START, RULER_END = 1960, 2026
EVENT_PATTERN = re.compile(
    r'<li class="event[^"]*" id="([^"]+)" data-year="(\d{4})".*?'
    r'<h4 class="event-title">(.*?)</h4>', re.S)


@app.template_filter("ruler_ticks")
def ruler_ticks(timeline_html):
    """Read the rendered timeline and return one tick per entry for the
    time ruler: its anchor, year, title and position along the axis."""
    ticks, per_year = [], {}
    for anchor, year, title in EVENT_PATTERN.findall(str(timeline_html)):
        year = int(year)
        stack = per_year.get(year, 0)
        per_year[year] = stack + 1
        ticks.append({
            "anchor": anchor,
            "year": year,
            "title": html.unescape(title),
            "left": round((year - RULER_START) / (RULER_END - RULER_START) * 100, 2),
            "stack": stack,
        })
    return ticks


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Serve the portfolio home page."""
    # Each entry names a Flask endpoint; the template builds the link with url_for().
    weekly_work = [
        {"week": 1, "title": "Live site launched", "endpoint": "home"},
        {"week": 2, "title": "History of the Internet", "endpoint": "internet_history"},
        {"week": 2, "title": "History of the Web", "endpoint": "web_history"},
        {"week": 2, "title": "History of the Internet (AI)", "endpoint": "internet_history_ai"},
        {"week": 2, "title": "History of the Web (AI)", "endpoint": "web_history_ai"},
        {"week": 4, "title": "Engineering Student Profile form", "endpoint": "submit_profile"},
    ]
    return render_template("index.html", weekly_work=weekly_work)


@app.route("/internet-history")
def internet_history():
    return render_template("internet-history.html")


@app.route("/web-history")
def web_history():
    return render_template("web-history.html")


@app.route("/internet-history-ai")
def internet_history_ai():
    return render_template("internet-history-ai.html")


@app.route("/web-history-ai")
def web_history_ai():
    return render_template("web-history-ai.html")


# --- Week 4: the Engineering Student Profile form -------------------------
# This route is the instructor's app_week4.py, unchanged. Server-side form
# handling is taught later; for now it is a black box with one job:
#
#   GET  /submit-profile  -> show the empty form   (templates/profile-form.html)
#   POST /submit-profile  -> read what was sent and show templates/profile.html
#
# request.form is the submitted data. .to_dict() keeps ONE value per field,
# which is right for text boxes, radios and single selects. Checkboxes and a
# <select multiple> can send the same name several times, so those two are
# read with .getlist() instead, which returns every value as a list.
@app.route("/submit-profile", methods=["GET", "POST"])
def submit_profile():
    if request.method == "POST":
        data = request.form.to_dict()                   # all single-value fields
        skills = request.form.getlist("skills")         # checkboxes -> list
        software = request.form.getlist("software")     # multiple <select> -> list
        return render_template(
            "profile.html", data=data, skills=skills, software=software
        )

    # First visit (GET): just show the empty form.
    return render_template("profile-form.html")


@app.errorhandler(404)
def page_not_found(error):
    """Flask calls this whenever no route matches the address requested.

    Returning a tuple of (html, status) keeps the 404 status code, which
    matters: a "not found" page that answers 200 tells search engines the
    page exists.
    """
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
