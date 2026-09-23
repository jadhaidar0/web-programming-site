"""
Web Programming — Flask application.
Serves the portfolio home page and the Week 2 history pages.
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """Serve the portfolio home page."""
    weekly_work = [
        {"week": 1, "title": "Live site launched", "url": "/"},
        {"week": 2, "title": "History of the Internet", "url": "/internet-history"},
        {"week": 2, "title": "History of the Web", "url": "/web-history"},
    ]
    return render_template("index.html", weekly_work=weekly_work)


@app.route("/internet-history")
def internet_history():
    return render_template("internet-history.html")


@app.route("/web-history")
def web_history():
    return render_template("web-history.html")


if __name__ == "__main__":
    app.run(debug=True)