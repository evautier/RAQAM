function formatDictionary(data, indent = 0) {
    let formattedText = "";
    for (const [key, value] of Object.entries(data)) {
        if (typeof value === "object" && value !== null) {
            // If value is a nested object, recursively format it with indentation
            formattedText += `<p style="margin-left: ${indent}px"><strong>${key}:</strong></p>`;
            formattedText += formatDictionary(value, indent + 20); // Increase indentation
        } else {
            // Normal key-value pair
            formattedText += `<p style="margin-left: ${indent}px"><strong>${key}:</strong> ${value}</p>`;
        }
    }
    return formattedText;
}

document.addEventListener("DOMContentLoaded", function () {
    const generateButton = document.getElementById("generate-quiz");
    const numQuestionsInput = document.getElementById("num-questions");
    const numChoicesInput = document.getElementById("num-choices");
    const textAreaInput = document.getElementById("text-area");
    const questionText = document.getElementById("question-text");
    let questionIndex = 0;
    let questions = [];
    let choicesContainer = document.getElementById("choices");
    let questionCounter = document.getElementById("question-counter");
    let errorBox = document.getElementById("error-message");
    let prevButton = document.getElementById("prev");
    let nextButton = document.getElementById("next");   
    const infoBtn = document.getElementById("infoBtn");
    const infoModal = document.getElementById("infoModal");
    const closeModal = document.getElementById("closeModal");
    const infoContent = document.getElementById("infoContent");
    let quizContext = {};
     
    // Store answered questions (to keep button colors)
    let answeredQuestions = {};
    
    async function fetchQuiz() {
        const numQuestions = numQuestionsInput.value || 1;
        const numChoices = numChoicesInput.value || 2;
        const textContent = textAreaInput.value || "";
        const loader = document.getElementById("loader");
        questionText.innerHTML = "";
        choicesContainer.innerHTML = "";
        questionCounter.innerHTML = "";
        answeredQuestions = {};
        prevButton.style.display = "none";
        nextButton.style.display = "none";
        errorBox.style.display = "none";
        try {
            // Show loader & disable button        
            loader.style.visibility = "visible";
            generateButton.disabled = true;        
            const response = await fetch("/generate-quiz", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ num_questions: numQuestions, num_choices: numChoices, text_content: textContent }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                let stackTrace = errorData.stack_trace ? `<pre>${errorData.stack_trace}</pre>` : ""; // Format stack trace if exists
                errorBox.innerHTML = `
                    <p><strong>${errorData.error}</strong></p>
                    <p>${errorData.message}</p>
                    ${stackTrace}
                `;
                errorBox.style.display = "block";
                return;
            }

            const data = await response.json();
            quizContext = data.quizContext;
            if (!data.questionCards || !Array.isArray(data.questionCards)) {
                throw new Error("Invalid response format");
            }

            questions = data.questionCards;
            questionIndex = 0; // Reset index
            loadQuestion(questionIndex);
            // Show nav buttons when quiz is loaded
            prevButton.style.display = "inline-block";
            nextButton.style.display = "inline-block";
            infoBtn.style.display = "flex";

        } catch (error) {
            errorBox.innerHTML = `<p><strong>Unexpected Error</strong></p><p>${error.message}</p>`;
            errorBox.style.display = "block";
        } finally {
            // Hide loader & enable button
            loader.style.visibility = "hidden";
            generateButton.disabled = false;
        }
    }

    function updateCounter() {
        questionCounter.innerText = `${questionIndex + 1}/${questions.length}`;
    }

    function loadQuestion(index, direction = "next") {
        let currentQuestion = questions[index];

        // Apply slide-out effect
        questionText.classList.add("slide-out");
        choicesContainer.classList.add("slide-out");

        setTimeout(() => {
            // Update question and choices
            questionText.innerText = currentQuestion.questionText;
            choicesContainer.innerHTML = "";
            choicesContainer.dataset.correctIndex = currentQuestion.questionAnswerIndex;

            currentQuestion.questionChoices.forEach((choice, idx) => {
                let button = document.createElement("button");
                button.classList.add("choice-btn");
                button.innerText = choice;
                button.onclick = () => handleAnswer(button, idx, currentQuestion.questionAnswerIndex, index);
                
                // Restore previous colors if answered before
                if (answeredQuestions[index]) {
                    if (idx === answeredQuestions[index].selected) {
                        button.classList.add(answeredQuestions[index].correct ? "correct" : "wrong");
                    }
                    if (idx === currentQuestion.questionAnswerIndex) {
                        button.classList.add("correct");
                    }
                    button.disabled = true;
                }

                choicesContainer.appendChild(button);
            });

            // Apply slide-in effect
            questionText.classList.remove("slide-out");
            choicesContainer.classList.remove("slide-out");

            updateCounter();
            nextButton.disabled = !answeredQuestions[index];
            prevButton.disabled = (index == 0);

        }, 300);
    }

    function handleAnswer(selectedButton, selectedIndex, correctIndex, currentQuestionIndex) {
        let buttons = document.querySelectorAll(".choice-btn");

        let isCorrect = selectedIndex === correctIndex;
        if (isCorrect) {
            selectedButton.classList.add("correct");
        } else {
            selectedButton.classList.add("wrong");
            buttons[correctIndex].classList.add("correct");
        }

        // Disable buttons to prevent multiple clicks
        buttons.forEach(button => button.disabled = true);

        // Store answer state
        answeredQuestions[currentQuestionIndex] = {
            selected: selectedIndex,
            correct: isCorrect
        };

        // Auto move to next question after 1 second
        setTimeout(() => {
            if (questionIndex < questions.length - 1) {
                questionIndex++;
                loadQuestion(questionIndex);
            }
        }, 1000);
    }

    prevButton.addEventListener("click", function () {
        if (questionIndex > 0) {
            questionIndex--;
            loadQuestion(questionIndex, "prev");
        }
    });

    nextButton.addEventListener("click", function () {
        if (questionIndex < questions.length - 1) {
            questionIndex++;
            loadQuestion(questionIndex, "next");
        }
    });

    infoBtn.addEventListener("click", function () {
        infoContent.innerHTML = formatDictionary(quizContext);
        infoModal.style.display = "flex";
    });

    closeModal.addEventListener("click", function () {
        infoModal.style.display = "none";
    });

    // Close modal when clicking outside
    window.addEventListener("click", (e) => {
        if (e.target === infoModal) {
            infoModal.style.display = "none";
        }
    });
    
    // Load first question
    generateButton.addEventListener("click", fetchQuiz);
});
