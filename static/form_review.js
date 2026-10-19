"use strict";

const form = document.querySelector(".profile-form");
const panel = document.getElementById("reviewPanel");
const reviewList = document.getElementById("reviewList");

form.addEventListener("submit", function (event) {
  event.preventDefault();

  if (!form.reportValidity()) {
    return;
  }

  showReview(collectData());
});

document.getElementById("editBtn").addEventListener("click", function () {
  panel.classList.remove("is-open");
  form.classList.remove("is-hidden");
  form.scrollIntoView();
});

// submit() does not fire the submit event, so the listener above is not run again.
document.getElementById("confirmBtn").addEventListener("click", function () {
  form.submit();
});


function valueOf(id) {
  return document.getElementById(id).value.trim();
}

function checkedValue(name) {
  return document.querySelector('input[name="' + name + '"]:checked')?.value;
}

function selectedText(id) {
  const select = document.getElementById(id);
  if (select.value === "") {
    return "";
  }
  return select.selectedOptions[0].text;
}

function collectData() {
  const skills = [...document.querySelectorAll('input[name="skills"]:checked')]
    .map(cb => cb.nextElementSibling.textContent);

  const software = [...document.getElementById("software").selectedOptions]
    .map(opt => opt.value);

  let phone = "";
  if (valueOf("phone") !== "") {
    phone = valueOf("phone_country") + " " + valueOf("phone");
  }

  return [
    ["Student ID", valueOf("student_id")],
    ["Full name", valueOf("fullname")],
    ["USEK email", valueOf("email")],
    ["Mobile number", phone],
    ["Date of birth", valueOf("birthdate")],
    ["GitHub", valueOf("portfolio")],
    ["GIN446 website", valueOf("gin446")],
    ["Engineering major", selectedText("major")],
    ["GPA / 100", valueOf("gpa")],
    ["Credits completed", valueOf("credits")],
    ["Graduation month", valueOf("graduation_month")],
    ["Expected graduation", checkedValue("graduation")],
    ["Internship completed", checkedValue("internship_completed")],
    ["Areas of experience", skills],
    ["Programming language", valueOf("language")],
    ["Engineering software", software],
    ["Project title", valueOf("project_title")],
    ["Project area", selectedText("project_area")],
    ["Project description", valueOf("description")],
    ["Team size", valueOf("team_size")],
    ["Dashboard colour", valueOf("project_color")],
    ["Meeting date", valueOf("meeting_date")],
    ["Meeting time", valueOf("meeting_time")],
    ["Information confirmed", document.getElementById("confirmation").checked ? "Yes" : "No"],
  ];
}

function showReview(rows) {
  reviewList.innerHTML = "";

  for (const [label, value] of rows) {
    const dt = document.createElement("dt");
    dt.textContent = label;

    const dd = document.createElement("dd");

    if (Array.isArray(value)) {
      if (value.length === 0) {
        dd.textContent = "None";
      } else {
        const ul = document.createElement("ul");
        for (const item of value) {
          const li = document.createElement("li");
          li.textContent = item;
          ul.appendChild(li);
        }
        dd.appendChild(ul);
      }
    } else {
      dd.textContent = value || "Not provided";
    }

    reviewList.appendChild(dt);
    reviewList.appendChild(dd);
  }

  form.classList.add("is-hidden");
  panel.classList.add("is-open");
  panel.scrollIntoView();
}
