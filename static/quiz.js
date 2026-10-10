/* =====================================================================
   quiz.js — GIN446 Week 5, interactive quiz
   Jad Haidar

   The file is in three parts:

     1. The questions        the data the quiz runs on
     2. The quiz state       which question we are on, and what was answered
     3. The logic            navigation, scoring, correction
     4. The interface        the code that talks to the page (DOM + events)

   Parts 1 to 3 are the activity. Part 4 is the interface layer that reads
   and writes the page; the DOM and events are taught in a later session.
   ===================================================================== */

"use strict";


/* ---------------------------------------------------------------------
   1. The questions

   Each question is an OBJECT with four properties:

     question     the text that is asked
     choices      an array of possible answers
     answer       the INDEX into choices of the correct one (0 based)
     explanation  a short reason, shown in the correction

   Storing the index rather than the text means the correct answer can
   never drift out of step with the wording of the choice.
   --------------------------------------------------------------------- */
const questions = [
  {
    question: "Which keyword declares a block-scoped variable that can later be reassigned?",
    choices: ["var", "let", "const", "static"],
    answer: 1,
    explanation: "let declares a block-scoped variable whose value may later be reassigned. " +
                 "var is function-scoped, and const cannot be reassigned.",
  },
  {
    question: "Which JavaScript operator tests strict equality?",
    choices: ["=", "==", "===", "!="],
    answer: 2,
    explanation: "The === operator compares both value and type. == converts the types first, " +
                 "so \"5\" == 5 is true while \"5\" === 5 is false.",
  },
  {
    question: "Which property gives the number of elements in a JavaScript array?",
    choices: ["size", "count", "length", "total"],
    answer: 2,
    explanation: "The length property contains the number of elements in an array. " +
                 "It is a property, not a method, so there are no brackets after it.",
  },
  {
    question: "What does the push() method do to an array?",
    choices: [
      "Removes the last element",
      "Adds an element to the end",
      "Adds an element to the beginning",
      "Sorts the array",
    ],
    answer: 1,
    explanation: "push() adds one or more elements to the END of an array and returns the " +
                 "new length. unshift() is the one that adds to the beginning.",
  },
  {
    question: "What is the value of typeof \"GIN446\"?",
    choices: ["\"text\"", "\"string\"", "\"String\"", "\"char\""],
    answer: 1,
    explanation: "typeof returns a lower-case string naming the type. For text that string " +
                 "is \"string\".",
  },
  {
    question: "Which loop is guaranteed to run its body at least once?",
    choices: ["for", "while", "do...while", "for...of"],
    answer: 2,
    explanation: "A do...while loop tests its condition AFTER running the body, so the body " +
                 "always runs at least once. A while loop tests first and may never run.",
  },
  {
    question: "What does a function return when it has no return statement?",
    choices: ["0", "null", "undefined", "An error"],
    answer: 2,
    explanation: "A function with no return statement returns undefined. That is different " +
                 "from null, which is a value you assign on purpose to mean \"nothing\".",
  },
  {
    question: "How do you read the property city from an object named student?",
    choices: ["student->city", "student.city", "student::city", "student:city"],
    answer: 1,
    explanation: "Dot notation, student.city, reads a property. Square brackets, " +
                 "student[\"city\"], do the same and are needed when the name is in a variable.",
  },
  {
    question: "What does Math.round(4.5) return?",
    choices: ["4", "5", "4.5", "NaN"],
    answer: 1,
    explanation: "Math.round() rounds to the nearest integer and rounds a .5 upwards, " +
                 "so Math.round(4.5) is 5.",
  },
  {
    question: "Which string method joins two strings together?",
    choices: ["concat()", "join()", "merge()", "append()"],
    answer: 0,
    explanation: "concat() joins strings. join() belongs to arrays, and merge() and append() " +
                 "are not JavaScript string methods at all.",
  },
];


/* ---------------------------------------------------------------------
   2. The quiz state

   Two pieces of information describe the whole quiz at any moment.

   currentQuestion  the INDEX of the question on screen. It starts at 0
                    because array indexes start at 0, so question 1 on
                    screen is questions[0] in the code.

   userAnswers      one slot per question, holding the index of the
                    choice picked. A slot that was never answered stays
                    undefined, which is how an unanswered question is
                    told apart from one answered with choice 0.

   userAnswers is const because the ARRAY itself never changes: only the
   values inside it do, and const does not prevent that.
   --------------------------------------------------------------------- */
let currentQuestion = 0;
const userAnswers = new Array(questions.length);


/* ---------------------------------------------------------------------
   3. The logic
   --------------------------------------------------------------------- */

/**
 * Store the choice the user just picked for the question on screen.
 * Writing into the slot rather than pushing keeps each answer tied to
 * its own question, which is what lets the user move around freely.
 */
function saveAnswer(choiceIndex) {
  userAnswers[currentQuestion] = choiceIndex;
}

/** Move forward one question, stopping at the last one. */
function goNext() {
  if (currentQuestion < questions.length - 1) {
    currentQuestion = currentQuestion + 1;
    renderQuestion();
  }
}

/** Move back one question, stopping at the first one. */
function goPrevious() {
  if (currentQuestion > 0) {
    currentQuestion = currentQuestion - 1;
    renderQuestion();
  }
}

/** Jump to the first question. */
function goFirst() {
  currentQuestion = 0;
  renderQuestion();
}

/** Jump to the last question. Length minus one, because indexes start at 0. */
function goLast() {
  currentQuestion = questions.length - 1;
  renderQuestion();
}

/**
 * Jump straight to one question, used by the numbered stepper.
 * The guard keeps the index inside the array whatever it is given.
 */
function goTo(index) {
  if (index >= 0 && index < questions.length) {
    currentQuestion = index;
    renderQuestion();
  }
}

/** Empty every answer and go back to the beginning. */
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

/** How many questions have been answered so far. */
function countAnswered() {
  let answered = 0;

  for (let i = 0; i < userAnswers.length; i++) {
    if (userAnswers[i] !== undefined) {
      answered = answered + 1;
    }
  }

  return answered;
}

/**
 * One point per correct answer.
 * An unanswered slot is undefined, and undefined is never equal to a
 * number, so unanswered questions score nothing without a special case.
 */
function calculateScore() {
  let score = 0;

  for (let i = 0; i < questions.length; i++) {
    if (userAnswers[i] === questions[i].answer) {
      score = score + 1;
    }
  }

  return score;
}

/** The score as a percentage of the total, rounded to a whole number. */
function calculatePercentage(score) {
  return Math.round((score / questions.length) * 100);
}

/**
 * Turn a percentage into a verdict.
 * The tests run from the highest band down, so each one only has to
 * check its lower edge: anything that reaches this line already failed
 * every higher test.
 */
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

/**
 * Build the full correction as one string: every question, what the
 * user answered, what was correct, the verdict and the explanation.
 *
 * The lines are collected in an array and joined at the end. Joining
 * once is tidier than gluing a string together in a loop.
 */
function buildCorrection() {
  const lines = [];

  for (let i = 0; i < questions.length; i++) {
    const current = questions[i];
    const given = userAnswers[i];

    // An unanswered question has no index to look up, so it is named.
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

/** Work out the results and hand them to the interface. */
function submitQuiz() {
  const score = calculateScore();
  const percentage = calculatePercentage(score);
  const message = getPerformanceMessage(percentage);
  const correction = buildCorrection();

  showResults(score, percentage, message, correction);
}


/* ---------------------------------------------------------------------
   4. The interface

   Everything below reads from or writes to the page. The DOM and events
   are covered in a later session; the logic above never touches the
   page, and this layer never decides anything about the quiz.
   --------------------------------------------------------------------- */

/** Draw the current question, its choices, the stepper and the buttons. */
function renderQuestion() {
  const current = questions[currentQuestion];
  const panel = document.getElementById("quizPanel");

  document.getElementById("progress").textContent =
    "Question " + (currentQuestion + 1) + " of " + questions.length;
  document.getElementById("questionText").textContent = current.question;

  renderStepper();

  // Rebuild the choices from scratch each time.
  const choicesBox = document.getElementById("choices");
  choicesBox.innerHTML = "";

  for (let i = 0; i < current.choices.length; i++) {
    const id = "choice-" + i;

    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "choice";
    radio.id = id;
    radio.value = i;
    // Re-tick the saved answer, which is what makes an answer survive
    // navigating away and coming back.
    radio.checked = userAnswers[currentQuestion] === i;
    radio.addEventListener("change", function () {
      saveAnswer(i);
      renderStepper();          // the dot for this question fills in
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

  // Grey out the moves that would go past either end.
  const atStart = currentQuestion === 0;
  const atEnd = currentQuestion === questions.length - 1;
  document.getElementById("firstBtn").disabled = atStart;
  document.getElementById("previousBtn").disabled = atStart;
  document.getElementById("nextBtn").disabled = atEnd;
  document.getElementById("lastBtn").disabled = atEnd;
}

/**
 * The row of numbered dots. One per question, marked as answered or not,
 * with the current one highlighted. Clicking a dot jumps to it.
 * It is built once and then only updated, so clicking a dot does not
 * destroy the element the click came from.
 */
function renderStepper() {
  const stepper = document.getElementById("stepper");

  // Build the ten buttons the first time only. They must not be rebuilt on
  // every move, because clicking one would then destroy the very button the
  // click came from.
  if (stepper.children.length === 0) {
    for (let i = 0; i < questions.length; i++) {
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
    // aria-current tells a screen reader which one you are on; the
    // data attribute is what the stylesheet colours.
    dots[i].dataset.state = userAnswers[i] === undefined ? "empty" : "answered";
    if (i === currentQuestion) {
      dots[i].setAttribute("aria-current", "true");
    } else {
      dots[i].removeAttribute("aria-current");
    }
  }

  // The deck ring and its label. --answered is a percentage; the
  // stylesheet turns it into an angle for the conic-gradient, so the
  // drawing stays in CSS and only the number comes from here.
  const answered = countAnswered();
  document.getElementById("quizPanel").style.setProperty(
    "--answered", (answered / questions.length) * 100
  );
  document.getElementById("deckCount").textContent =
    answered + "/" + questions.length;
  // The ring already carries the count, so this line is a key for the
  // squares above it rather than a second tally.
  document.getElementById("answeredCount").textContent =
    answered === questions.length
      ? "All questions answered"
      : "Filled squares are answered";
}

/** Hide the quiz, show the results panel, fill it in. */
function showResults(score, percentage, message, correction) {
  // Toggle a class rather than writing style.display directly. An inline
  // style beats every rule in the stylesheet, so setting display here
  // would flatten the panel's own grid layout. The class lets the
  // stylesheet keep deciding HOW each panel is laid out; this only says
  // WHICH one is showing.
  document.getElementById("quizPanel").classList.add("is-hidden");

  const results = document.getElementById("resultsPanel");
  results.classList.add("is-open");

  document.getElementById("scoreText").textContent =
    "Score: " + score + " / " + questions.length;
  document.getElementById("percentageText").textContent =
    "Percentage: " + percentage + "%";
  document.getElementById("performanceText").textContent = message;

  // A band name lets the stylesheet colour the verdict and the ring.
  results.dataset.band = message.toLowerCase().split(" ")[0];
  // The ring is a conic-gradient sized by this one number.
  results.style.setProperty("--pct", percentage);
  document.getElementById("ringValue").textContent = percentage + "%";

  renderResultStrip();
  renderCorrectionCards();

  // textContent, not innerHTML: the correction is plain text and must
  // never be treated as markup.
  document.getElementById("correction").textContent = correction;

  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

/** One small square per question: correct, incorrect or unanswered. */
function renderResultStrip() {
  const strip = document.getElementById("resultStrip");
  strip.innerHTML = "";

  for (let i = 0; i < questions.length; i++) {
    const given = userAnswers[i];
    const cell = document.createElement("button");
    cell.type = "button";
    cell.className = "strip-cell";
    cell.textContent = i + 1;

    if (given === undefined) {
      cell.dataset.state = "empty";
      cell.title = "Question " + (i + 1) + ": not answered";
    } else if (given === questions[i].answer) {
      cell.dataset.state = "right";
      cell.title = "Question " + (i + 1) + ": correct";
    } else {
      cell.dataset.state = "wrong";
      cell.title = "Question " + (i + 1) + ": incorrect";
    }

    // Jump to that question's entry further down the correction.
    cell.addEventListener("click", function () {
      document.getElementById("fix-" + i).scrollIntoView({
        behavior: "smooth", block: "center"
      });
    });

    strip.appendChild(cell);
  }
}

/**
 * The correction as a list of cards.
 *
 * buildCorrection() still produces the plain-text version, and it is
 * still shown, tucked inside the "Plain text version" panel underneath.
 * This is the same information drawn properly: the interface layer is
 * allowed to present the data however it likes.
 */
function renderCorrectionCards() {
  const list = document.getElementById("correctionCards");
  list.innerHTML = "";

  for (let i = 0; i < questions.length; i++) {
    const current = questions[i];
    const given = userAnswers[i];
    const isRight = given === current.answer;

    const item = document.createElement("li");
    item.className = "fix";
    item.id = "fix-" + i;
    item.dataset.state = given === undefined ? "empty" : isRight ? "right" : "wrong";

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
    verdict.textContent =
      given === undefined ? "Not answered" : isRight ? "Correct" : "Incorrect";

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

/** Add one label-and-value pair to a correction card's description list. */
function addRow(list, term, value) {
  const dt = document.createElement("dt");
  dt.textContent = term;

  const dd = document.createElement("dd");
  dd.textContent = value;

  list.appendChild(dt);
  list.appendChild(dd);
}


/* Draw the first question as soon as the script runs. The <script> tag
   sits at the end of the page, so the elements above already exist. */
renderQuestion();
