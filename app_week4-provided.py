"""
Web Programming — Flask application (Week 4).

Download this file from e-learning and REPLACE all the contents of your existing
app.py with it. Then run your app as usual.

WHAT THIS FILE DOES (the "black box" for this week)
---------------------------------------------------
It adds the "Engineering Student Profile" form. You do NOT need to understand this
code yet — server-side form handling is taught in a later session. For now:

  GET  /submit-profile   -> shows your form   (you build templates/profile_form.html)
  POST /submit-profile   -> reads the submitted data and shows your profile page
                            (renders templates/profile.html, which extends your
                             base.html so it appears in YOUR design / CSS)

HOW THE DATA REACHES THE PROFILE PAGE
-------------------------------------
When the form is submitted, this route reads every field the form sends and hands
it to profile.html. Three variables are available inside profile.html:

  data      -> a dictionary of all single-value fields, keyed by the field `name`,
               e.g. data['fullname'], data['student_id'], data['email'],
               data['major'], data['gpa'], data['project_title'], ...
  skills    -> a LIST of the ticked "skills" checkboxes
  software  -> a LIST of the selected "software" options (from the multiple <select>)

Note: `skills` and `software` can hold several values, so they are read as lists.
Every other field is a single value inside `data`.

Example inside profile.html (which extends your base.html):

  <h1>{{ data['fullname'] }}</h1>
  <p>{{ data['major'] }}</p>
  <p>Skills: {{ skills | join(', ') }}</p>
  <p>Software: {{ software | join(', ') }}</p>
"""

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    """Serve the portfolio home page."""
    weekly_work = [
        {"week": 2, "title": "History of the Internet", "url": "/internet-history"},
        {"week": 2, "title": "History of the Web", "url": "/web-history"},
        {"week": 2, "title": "History of the Internet (AI)", "url": "/internet-history-ai"},
        {"week": 2, "title": "History of the Web (AI)", "url": "/web-history-ai"},
        {"week": 4, "title": "Engineering Student Profile", "url": "/submit-profile"},
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


@app.route("/submit-profile", methods=["GET", "POST"])
def submit_profile():
    """
    GET  -> show the profile form (you build templates/profile_form.html).
    POST -> read the submitted fields and show the profile page
            (templates/profile.html, which extends your base.html).
    """
    if request.method == "POST":
        data = request.form.to_dict()                   # all single-value fields
        skills = request.form.getlist("skills")         # checkboxes -> list
        software = request.form.getlist("software")     # multiple <select> -> list
        return render_template(
            "profile.html", data=data, skills=skills, software=software
        )

    # First visit (GET): just show the empty form.
    return render_template("profile-form.html")


if __name__ == "__main__":
    app.run(debug=True)