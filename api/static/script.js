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
    let prevButton = document.getElementById("prev");
    let nextButton = document.getElementById("next");   
     
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
        try {
            // Show loader & disable button        
            loader.classList.remove("hidden");
            generateButton.disabled = true;        
            const response = await fetch("/generate-quiz", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ num_questions: numQuestions, num_choices: numChoices, text_content: textContent }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Error from server:", errorData);
                alert(`Error: ${errorData.error || "Unknown error"}`);
                return;
            }

            const data = await response.json();
            if (!data.questionCards || !Array.isArray(data.questionCards)) {
                throw new Error("Invalid response format");
            }

            questions = data.questionCards;
            questionIndex = 0; // Reset index
            loadQuestion(questionIndex);
            // Show nav buttons when quiz is loaded
            prevButton.style.display = "inline-block";
            nextButton.style.display = "inline-block";

        } catch (error) {
            console.error("Fetch error:", error);
            alert("Failed to fetch questions. Please try again.");

        } finally {
            // Hide loader & enable button
            loader.classList.add("hidden");
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

    // Load first question
    generateButton.addEventListener("click", fetchQuiz);
});
