"use strict";

let total = 0;
const cache = {};

let currentQuestion = 0;
const userAnswers = [];


async function getQuestion(index) {
  if (cache[index]) {
    return cache[index];
  }

  const response = await fetch(`/api/question/${index}`);
  if (!response.ok) {
    throw new Error("Could not load question " + (index + 1));
  }

  const question = await response.json();
  cache[index] = question;
  return question;
}

function saveAnswer(choiceIndex) {
  userAnswers[currentQuestion] = choiceIndex;
}

function goNext() {
  if (currentQuestion < total - 1) {
    currentQuestion = currentQuestion + 1;
    renderQuestion();
  }
}

function goPrevious() {
  if (currentQuestion > 0) {
    currentQuestion = currentQuestion - 1;
    renderQuestion();
  }
}

function goFirst() {
  currentQuestion = 0;
  renderQuestion();
}

function goLast() {
  currentQuestion = total - 1;
  renderQuestion();
}

function goTo(index) {
  if (index >= 0 && index < total) {
    currentQuestion = index;
    renderQuestion();
  }
}

function restartQuiz() {
  for (let i = 0; i < userAnswers.length; i++) {
    userAnswers[i] = undefined;
  }
  currentQuestion = 0;
  document.getElementById("resultsPanel").classList.remove("is-open");
  document.getElementById("quizPanel").classList.remove("is-hidden");
  renderQuestion();
  document.getElementById("quizPanel").scrollIntoView({ behavior: "smooth", block: "start" });
}

function countAnswered() {
  let answered = 0;

  for (let i = 0; i < userAnswers.length; i++) {
    if (userAnswers[i] !== undefined) {
      answered = answered + 1;
    }
  }

  return answered;
}

async function calculateScore() {
  let score = 0;

  for (let i = 0; i < total; i++) {
    const current = await getQuestion(i);
    if (userAnswers[i] === current.answer) {
      score = score + 1;
    }
  }

  return score;
}

function calculatePercentage(score) {
  return Math.round((score / total) * 100);
}

function getPerformanceMessage(percentage) {
  if (percentage >= 80) {
    return "Excellent";
  } else if (percentage >= 60) {
    return "Good";
  } else if (percentage >= 50) {
    return "Pass";
  } else {
    return "Needs improvement";
  }
}

async function buildCorrection() {
  const lines = [];

  for (let i = 0; i < total; i++) {
    const current = await getQuestion(i);
    const given = userAnswers[i];

    const userAnswerText =
      given === undefined ? "Not answered" : current.choices[given];
    const correctAnswerText = current.choices[current.answer];
    const result = given === current.answer ? "Correct" : "Incorrect";

    lines.push("Question " + (i + 1) + ": " + current.question);
    lines.push("");
    lines.push("Your answer: " + userAnswerText);
    lines.push("Correct answer: " + correctAnswerText);
    lines.push("Result: " + result);
    lines.push("Explanation: " + current.explanation);
    lines.push("");
    lines.push("---------------------------------------");
    lines.push("");
  }

  return lines.join("\n");
}

async function submitQuiz() {
  const error = document.getElementById("error");
  error.hidden = true;

  try {
    const score = await calculateScore();
    const percentage = calculatePercentage(score);
    const message = getPerformanceMessage(percentage);
    const correction = await buildCorrection();

    showResults(score, percentage, message, correction);
  } catch (err) {
    error.textContent = err.message;
    error.hidden = false;
  }
}


function answerState(index) {
  if (userAnswers[index] === undefined) {
    return "empty";
  }
  if (userAnswers[index] === cache[index].answer) {
    return "right";
  }
  return "wrong";
}

const STATE_WORDS = {
  right: "Correct",
  wrong: "Incorrect",
  empty: "Not answered",
};


async function renderQuestion() {
  const loading = document.getElementById("loading");
  const error = document.getElementById("error");
  const index = currentQuestion;

  loading.hidden = false;
  error.hidden = true;

  try {
    const current = await getQuestion(index);

    if (index !== currentQuestion) {
      return;
    }

    document.getElementById("progress").textContent =
      "Question " + (currentQuestion + 1) + " of " + total;
    document.getElementById("questionText").textContent = current.question;

    renderStepper();

    const choicesBox = document.getElementById("choices");
    choicesBox.innerHTML = "";

    for (let i = 0; i < current.choices.length; i++) {
      const id = "choice-" + i;

      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "choice";
      radio.id = id;
      radio.value = i;
      radio.checked = userAnswers[currentQuestion] === i;
      radio.addEventListener("change", function () {
        saveAnswer(i);
        renderStepper();
      });

      const text = document.createElement("span");
      text.className = "choice-text";
      text.textContent = current.choices[i];

      const label = document.createElement("label");
      label.className = "choice";
      label.htmlFor = id;
      label.appendChild(radio);
      label.appendChild(text);

      choicesBox.appendChild(label);
    }

    const atStart = currentQuestion === 0;
    const atEnd = currentQuestion === total - 1;
    document.getElementById("firstBtn").disabled = atStart;
    document.getElementById("previousBtn").disabled = atStart;
    document.getElementById("nextBtn").disabled = atEnd;
    document.getElementById("lastBtn").disabled = atEnd;
  } catch (err) {
    error.textContent = err.message;
    error.hidden = false;
  } finally {
    loading.hidden = true;
  }
}

function renderStepper() {
  const stepper = document.getElementById("stepper");

  if (stepper.children.length === 0) {
    for (let i = 0; i < total; i++) {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "step";
      dot.textContent = i + 1;
      dot.addEventListener("click", function () {
        goTo(i);
      });
      stepper.appendChild(dot);
    }
  }

  const dots = stepper.children;
  for (let i = 0; i < dots.length; i++) {
    dots[i].dataset.state = userAnswers[i] === undefined ? "empty" : "answered";
    if (i === currentQuestion) {
      dots[i].setAttribute("aria-current", "true");
    } else {
      dots[i].removeAttribute("aria-current");
    }
  }

  const answered = countAnswered();
  document.getElementById("quizPanel").style.setProperty(
    "--answered", (answered / total) * 100
  );
  document.getElementById("deckCount").textContent =
    answered + "/" + total;
  document.getElementById("answeredCount").textContent =
    answered === total
      ? "All questions answered"
      : "Filled squares are answered";
}

function showResults(score, percentage, message, correction) {
  document.getElementById("quizPanel").classList.add("is-hidden");

  const results = document.getElementById("resultsPanel");
  results.classList.add("is-open");

  document.getElementById("scoreText").textContent =
    "Score: " + score + " / " + total;
  document.getElementById("percentageText").textContent =
    "Percentage: " + percentage + "%";
  document.getElementById("performanceText").textContent = message;

  results.dataset.band = message.toLowerCase().split(" ")[0];
  results.style.setProperty("--pct", percentage);
  document.getElementById("ringValue").textContent = percentage + "%";

  renderCorrectionCards();

  document.getElementById("correction").textContent = correction;

  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderCorrectionCards() {
  const list = document.getElementById("correctionCards");
  list.innerHTML = "";

  for (let i = 0; i < total; i++) {
    const current = cache[i];
    const given = userAnswers[i];
    const state = answerState(i);

    const item = document.createElement("li");
    item.className = "fix";
    item.dataset.state = state;

    const head = document.createElement("div");
    head.className = "fix-head";

    const num = document.createElement("span");
    num.className = "fix-num";
    num.textContent = i + 1;

    const q = document.createElement("h4");
    q.className = "fix-q";
    q.textContent = current.question;

    const verdict = document.createElement("span");
    verdict.className = "fix-verdict";
    verdict.textContent = STATE_WORDS[state];

    head.appendChild(num);
    head.appendChild(q);
    head.appendChild(verdict);

    const answers = document.createElement("dl");
    answers.className = "fix-answers";
    addRow(answers, "Your answer",
      given === undefined ? "Not answered" : current.choices[given]);
    addRow(answers, "Correct answer", current.choices[current.answer]);

    const why = document.createElement("p");
    why.className = "fix-why";
    why.textContent = current.explanation;

    item.appendChild(head);
    item.appendChild(answers);
    item.appendChild(why);
    list.appendChild(item);
  }
}

function addRow(list, term, value) {
  const dt = document.createElement("dt");
  dt.textContent = term;

  const dd = document.createElement("dd");
  dd.textContent = value;

  list.appendChild(dt);
  list.appendChild(dd);
}


async function init() {
  const error = document.getElementById("error");

  try {
    const response = await fetch("/api/questions/count");
    if (!response.ok) {
      throw new Error("Could not load the quiz");
    }

    const data = await response.json();
    total = data.count;

    await renderQuestion();
  } catch (err) {
    error.textContent = err.message;
    error.hidden = false;
  }
}

init();
