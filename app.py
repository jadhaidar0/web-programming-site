"""
Web Programming — starter Flask application (Week 1).

A minimal server that renders the portfolio home page. Over the semester you
will add routes here; for now it serves a single page from the templates folder.
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """Serve the portfolio home page."""
    # The list of weekly work grows as the semester goes on.
    weekly_work = [
        # {"week": 1, "title": "Live site launched", "url": "/"},
    ]
    return render_template("index.html", weekly_work=weekly_work)


if __name__ == "__main__":
    # For local development only. In production, Render runs the app with
    # gunicorn (see the Procfile), not this block.
    app.run(debug=True)
