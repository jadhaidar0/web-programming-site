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

# Main menu. Each entry is a dict:
#
#   label     what the menu shows
#   endpoint  where the entry itself goes
#   children  optional list of {endpoint, label} shown in a small submenu
#
# The two history topics have children, so the menu stays at five items
# instead of listing the hand-made and AI versions separately. Clicking
# the parent still works on its own: it goes to the hand-made version.
MENU = [
    {"endpoint": "home", "label": "Home"},
    {
        "endpoint": "internet_history",
        "label": "Internet",
        "children": [
            {"endpoint": "internet_history", "label": "Written by hand"},
            {"endpoint": "internet_history_ai", "label": "Generated with AI"},
        ],
    },
    {
        "endpoint": "web_history",
        "label": "Web",
        "children": [
            {"endpoint": "web_history", "label": "Written by hand"},
            {"endpoint": "web_history_ai", "label": "Generated with AI"},
        ],
    },
    {"endpoint": "weekly", "label": "Journal"},
    {"endpoint": "research", "label": "Research"},
    {"endpoint": "quiz", "label": "Quiz"},
    {"endpoint": "submit_profile", "label": "Profile"},
]


def menu_is_active(item, endpoint):
    """True when a menu entry, or any of its children, is the current page.

    The parent "Internet" should look selected on both the hand-made and
    the AI page, otherwise the menu loses your place as soon as you
    switch version from inside the submenu.
    """
    if item["endpoint"] == endpoint:
        return True
    return any(child["endpoint"] == endpoint for child in item.get("children", []))

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


# The course journal. One entry per week, newest last.
#
#   built    what was added to the site that week
#   learned  the ideas behind it, in plain words
#   links    pages to look at, as (endpoint, label)
WEEKS = [
    {
        "week": 1,
        "title": "Getting a Flask site live",
        "tint": "soft",
        "summary": "Set the project up from the course template and put it on a real "
                   "server instead of leaving it on my laptop.",
        "built": [
            "A Flask app with routes for the home page and one template per page.",
            "The folder layout Flask expects: templates/ for pages, static/ for CSS and images.",
            "The site deployed and reachable on its own address.",
        ],
        "learned": [
            "A route is a URL joined to a Python function. Flask runs the function "
            "and sends back whatever it returns.",
            "render_template() looks inside templates/ and fills the page in before sending it.",
            "url_for() builds addresses from the route's name instead of me typing the path. "
            "If a route changes later, every link follows it.",
        ],
        "links": [("home", "Home page")],
    },
    {
        "week": 2,
        "title": "History of the Internet and the Web",
        "tint": "mint",
        "summary": "Four long pages on the same two topics, each one written twice: "
                   "once by hand from my own research, once with AI, so the two can "
                   "be compared.",
        "built": [
            "Two hand-written timelines, one for the Internet and one for the Web.",
            "Two AI-generated versions of the same topics.",
            "A sourced reference list on every page, with the primary sources marked.",
        ],
        "learned": [
            "Semantic HTML is about meaning, not looks. header, nav, main, section, "
            "article and time each say what a piece of content is.",
            "A page should have one h1 and no skipped heading levels, because that "
            "outline is how a screen reader navigates.",
            "An ordered list is the honest element for a timeline, since the order "
            "carries meaning.",
            "Checking sources properly is slower than writing. Several links looked "
            "fine and turned out to be dead or to no longer support the claim.",
        ],
        "links": [
            ("internet_history", "History of the Internet"),
            ("web_history", "History of the Web"),
        ],
    },
    {
        "week": 3,
        "title": "One layout, one stylesheet",
        "tint": "sun",
        "summary": "The four pages had grown their own copies of the same header, "
                   "footer and CSS. This week was about saying each of those things "
                   "once and having every page inherit it.",
        "built": [
            "base.html, holding the page shell, the menu and the footer, with Jinja "
            "blocks for the parts that change.",
            "history.html, a second layer between base.html and the four history "
            "pages, so everything those four share is written once.",
            "One style.css for the whole site, with the colours, fonts and spacing "
            "declared as design tokens on :root.",
            "A full redesign on top of that: the white shell, the side rail, the "
            "bento tile grid and the centre-spine timeline.",
        ],
        "learned": [
            "Template inheritance: {% extends %} names the parent, {% block %} marks "
            "a hole in it, and a child page fills the holes. The shared parts exist "
            "in one file.",
            "Design tokens are custom properties declared once on :root. Because "
            ":root is the html element, every var() further down inherits it, so "
            "changing one line restyles the whole site.",
            "The cascade is not a bug to fight. Later rules and more specific "
            "selectors win, and that is what lets a page add to the site styles "
            "without editing them.",
            "CSS Grid places things without moving them in the HTML. The timeline "
            "alternates left and right using nth-child and column spans, so the "
            "reading order stays correct.",
            "Contrast has to be measured, not guessed. Several colours I liked "
            "failed WCAG AA and had to be darkened.",
        ],
        "links": [
            ("internet_history", "See the shared layout in use"),
            ("web_history_ai", "The same layout, different content"),
        ],
    },
    {
        "week": 4,
        "title": "Forms and the data behind them",
        "tint": "pink",
        "summary": "An Engineering Student Profile form, built by hand, that posts "
                   "to the server and comes back as a finished profile page.",
        "built": [
            "profile-form.html: five sections, 34 controls, twelve different input "
            "types, a datalist, a multiple select and a select with optgroups.",
            "Validation done by the browser alone, with required, pattern, min, max, "
            "step and maxlength. No JavaScript.",
            "form_style.css, a second stylesheet loaded only by the form page "
            "through the {% block head %} slot.",
        ],
        "learned": [
            "The name attribute is what the server sees. The label is for the person, "
            "the name is for the code, and they are not the same thing.",
            "A checkbox group and a multiple select can send the same name more than "
            "once, so the server reads those as a list and everything else as a "
            "single value.",
            "GET puts the data in the URL, POST puts it in the request body. Anything "
            "long or personal should be POST.",
            "Every control needs a label tied to its id, or clicking the text does "
            "nothing and a screen reader announces an unnamed box.",
            ":user-invalid waits until someone has actually used a field, while "
            ":invalid fires immediately and paints an untouched form red.",
            "A second stylesheet loaded after the first can extend one page without "
            "touching any other. That is the cascade being useful on purpose.",
        ],
        "links": [("submit_profile", "The profile form")],
    },
    {
        "week": 5,
        "title": "The first JavaScript on the site",
        "tint": "soft",
        "summary": "An interactive quiz. Until this week every page was finished by the "
                   "time it reached the browser. This one keeps changing after it arrives.",
        "built": [
            "A ten question quiz with First, Previous, Next and Last navigation.",
            "Answers that survive moving around, so a question can be revisited and changed.",
            "Scoring, a percentage, a verdict, and a full correction for every question.",
            "quiz.css, a third stylesheet loaded only by that page.",
        ],
        "learned": [
            "An object groups related values under names. Each question is one object "
            "holding its text, its choices, the index of the correct one, and an explanation.",
            "Storing the correct answer as an INDEX rather than as text means the two can "
            "never disagree if the wording of a choice changes.",
            "An array slot that was never filled is undefined, and undefined is never equal "
            "to a number. Unanswered questions therefore score nothing with no special case.",
            "const on an array stops the variable being pointed somewhere else, not the "
            "contents being changed. userAnswers is const and still gets written into.",
            "Separating the logic from the page is what makes it testable: the functions that "
            "calculate the score never touch the DOM, and the DOM code never decides anything.",
        ],
        "links": [("quiz", "The quiz")],
    },
]


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
    return {
        "menu": MENU,
        "menu_is_active": menu_is_active,
        "history_pages": HISTORY_PAGES,
        "related_pages": related_pages,
        "weeks": WEEKS,
    }


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
    return render_template("index.html")


@app.route("/weekly")
def weekly():
    """The course journal: what was built each week, and what it taught."""
    return render_template("weekly.html")


# Week 5: the JavaScript quiz. The page is served as-is; everything the
# quiz does happens in the browser, in static/quiz.js.
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/research")
def research():
    """Reference notes: the syntax this site is built from, each one with
    a working demonstration."""
    return render_template("research.html")


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

        # The mobile number is collected as TWO controls: a country picker
        # and the number itself. profile.html prints data['phone'] on its
        # own, so the two halves are joined back into one value here.
        # pop() also takes phone_country out of data, so it is not left
        # lying around as a stray field.
        code = data.pop("phone_country", "").strip()
        number = data.get("phone", "").strip()
        data["phone"] = f"{code} {number}".strip() if number else ""

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
