// ===== DEBUG LOGGER =====
function log(message, data = null) {
    console.log(message, data);
    const logs = document.getElementById('debug-logs');
    if (logs) {
        const entry = document.createElement('div');
        const time = new Date().toLocaleTimeString();
        let text = `[${time}] ${message}`;
        if (data) {
            try {
                if (typeof data === 'object') {
                    text += ' ' + JSON.stringify(data);
                } else {
                    text += ' ' + String(data);
                }
            } catch (e) {
                text += ' [Complex Data]';
            }
        }
        entry.textContent = text;
        entry.style.borderBottom = '1px solid #333';
        entry.style.padding = '2px 0';
        logs.appendChild(entry);
        logs.scrollTop = logs.scrollHeight;
    }
}

window.onerror = function (msg, url, lineNo, columnNo, error) {
    log(`ERROR: ${msg} @ ${lineNo}:${columnNo}`);
    return false;
};

// ===== QUIZ PAGE =====
let currentQuestionIndex = 0;
let score = 0;
let currentQuestion = null;
let questions = [];
let answered = false;
let quizStartTime = null;
let timerInterval = null;
let quizQuestionsData = [];
let currentQuizId = null;

// Initialiser le quiz
async function initQuiz() {
    log('Initializing quiz...');
    if (!quizImages || quizImages.length === 0) {
        log('ERROR: No images found!');
        return;
    }

    // Mélanger les images pour le quiz
    questions = [...quizImages].sort(() => Math.random() - 0.5);
    currentQuestionIndex = 0;
    score = 0;
    answered = false;
    quizStartTime = Date.now();
    quizQuestionsData = [];
    currentQuizId = null;

    // Démarrer une nouvelle session sur le serveur
    try {
        const response = await fetch('/api/quiz/start_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
            const data = await response.json();
            currentQuizId = data.quiz_id;
            log('Quiz session started on server. ID:', currentQuizId);
        } else {
            log('Failed to start quiz session on server');
        }
    } catch (e) {
        log('Error starting quiz session:', e);
    }

    updateStats();
    startTimer();
    loadQuestion();

    document.getElementById('quizInfo').classList.remove('hidden');
    document.getElementById('quizContent').classList.remove('hidden');
    document.getElementById('quizResults').classList.add('hidden');
    log('Quiz initialized. Total questions: ' + questions.length);
}

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    const timerDisplay = document.getElementById('timer');
    let seconds = 0;
    timerInterval = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        timerDisplay.textContent = `${mins}:${secs}`;
    }, 1000);
}

function loadQuestion() {
    if (currentQuestionIndex >= questions.length) {
        showResults();
        return;
    }

    currentQuestion = questions[currentQuestionIndex];
    answered = false;

    // Afficher l'image
    const questionImage = document.getElementById('questionImage');
    questionImage.src = `/images/${currentQuestion.filename}`;

    // Générer les réponses (1 correcte + 3 incorrectes)
    const correctAnswer = currentQuestion.class;
    const wrongAnswers = getWrongAnswers(correctAnswer);
    const answers = [correctAnswer, ...wrongAnswers].sort(() => Math.random() - 0.5);

    // Afficher les réponses
    const answersGrid = document.getElementById('answersGrid');
    answersGrid.innerHTML = '';

    answers.forEach(answer => {
        const answerBtn = document.createElement('button');
        answerBtn.className = 'answer-btn';
        answerBtn.textContent = answer;
        answerBtn.onclick = () => selectAnswer(answer, correctAnswer);
        answersGrid.appendChild(answerBtn);
    });

    // Masquer le feedback et les boutons
    document.getElementById('quizFeedback').classList.add('hidden');
    document.getElementById('nextBtn').classList.add('hidden');
    document.getElementById('restartBtn').classList.add('hidden');

    updateStats();
}

function getWrongAnswers(correctAnswer) {
    const allClasses = quizImages.map(img => img.class);
    const wrongAnswers = allClasses
        .filter(cls => cls !== correctAnswer)
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);
    return wrongAnswers;
}

function selectAnswer(selectedAnswer, correctAnswer) {
    if (answered) return;

    answered = true;
    const answerButtons = document.querySelectorAll('.answer-btn');
    const feedback = document.getElementById('quizFeedback');
    const feedbackIcon = document.getElementById('feedbackIcon');
    const feedbackText = document.getElementById('feedbackText');

    // Enregistrer les détails de la question
    const isCorrect = selectedAnswer === correctAnswer;
    const questionInfo = {
        question: currentQuestion ? currentQuestion.filename : 'unknown',
        correct_answer: correctAnswer,
        selected_answer: selectedAnswer,
        correct: isCorrect
    };

    if (!quizQuestionsData) {
        quizQuestionsData = [];
    }
    quizQuestionsData.push(questionInfo);

    // Sauvegarder en arrière-plan (non-bloquant)
    if (currentQuizId) {
        fetch('/api/quiz/update_progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quiz_id: currentQuizId, question_data: questionInfo })
        }).catch(err => log('Silently ignored progress error', err));
    }

    // Désactiver tous les boutons et appliquer les couleurs
    answerButtons.forEach(btn => {
        btn.classList.add('disabled');
        if (btn.textContent === correctAnswer) {
            btn.classList.add('correct');
        } else if (btn.textContent === selectedAnswer && selectedAnswer !== correctAnswer) {
            btn.classList.add('incorrect');
        }
    });

    if (isCorrect) score++;

    // Le feedback textuel est supprimé pour plus de rapidité (demande utilisateur)
    // Mais on garde l'incrémentation du score et les stats

    // Prochaines étapes
    if (currentQuestionIndex < questions.length - 1) {
        document.getElementById('nextBtn').classList.remove('hidden');
        // Auto-advance RAPIDE (600ms) pour une fluidité maximale
        setTimeout(() => {
            if (currentQuestionIndex < questions.length - 1) nextQuestion();
        }, 600);
    } else {
        document.getElementById('restartBtn').classList.remove('hidden');
        setTimeout(() => {
            showResults();
        }, 800);
    }

    updateStats();
}

function nextQuestion() {
    // Si déjà répondu ou première question, on avance
    currentQuestionIndex++;
    loadQuestion();
}

async function showResults() {
    log('Showing results...');
    document.getElementById('quizInfo').classList.add('hidden');
    document.getElementById('quizContent').classList.add('hidden');
    document.getElementById('quizResults').classList.remove('hidden');

    const finalScore = document.getElementById('finalScore');
    const scoreMessage = document.getElementById('scoreMessage');

    const totalResult = document.getElementById('totalQuestionsResult');
    if (totalResult) totalResult.textContent = questions.length;

    finalScore.textContent = score;
    const percentage = Math.round((score / questions.length) * 100);

    // Update circular chart
    const circle = document.getElementById('resultCircle');
    const percentageDisplay = document.getElementById('scorePercentageDisplay');
    if (circle) circle.setAttribute('stroke-dasharray', `${percentage}, 100`);
    if (percentageDisplay) percentageDisplay.textContent = `${percentage}%`;

    if (timerInterval) clearInterval(timerInterval);

    // Message selon le score
    if (percentage >= 90) {
        scoreMessage.textContent = 'Excellent ! Vous maîtrisez parfaitement les signes ASL !';
    } else if (percentage >= 70) {
        scoreMessage.textContent = 'Très bien ! Continuez à pratiquer !';
    } else if (percentage >= 50) {
        scoreMessage.textContent = 'Pas mal ! Pratiquez encore un peu !';
    } else {
        scoreMessage.textContent = 'Continuez à apprendre ! Vous vous améliorerez !';
    }

    // Calculer la durée du quiz
    const quizDuration = quizStartTime ? Math.round((Date.now() - quizStartTime) / 1000) : 0;

    // Préparer les données à envoyer
    const quizData = {
        quiz_id: currentQuizId,
        total_questions: questions.length,
        correct_answers: score,
        score_percentage: percentage,
        quiz_duration: quizDuration,
        questions_data: quizQuestionsData
    };

    log('Finalizing quiz data...', quizData);

    // Sauvegarder le résultat
    try {
        const response = await fetch('/api/quiz/save_result', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(quizData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            log(`HTTP ERROR: ${errorText}`);
            if (scoreMessage) scoreMessage.textContent += ' (Erreur de sauvegarde)';
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const result = await response.json();
        if (result.success) {
            log('SUCCESS: Quiz saved');
            if (scoreMessage) {
                const originalText = scoreMessage.textContent;
                scoreMessage.textContent = originalText + ' (Résultat enregistré ✓)';
                scoreMessage.style.color = '#28a745';
                setTimeout(() => { scoreMessage.style.color = ''; }, 3000);
            }
        }
    } catch (error) {
        log('EXCEPTION: ' + error.message);
        console.error('Erreur lors de l\'enregistrement du quiz:', error);
    }

    // Auto-refresh la page après 10 secondes (demande utilisateur)
    setTimeout(() => {
        if (!document.getElementById('quizResults').classList.contains('hidden')) {
            log('Auto-refreshing page...');
            window.location.reload();
        }
    }, 10000);
}

function restartQuiz() {
    // Recharger la page pour un nouveau départ propre
    window.location.reload();
}

function updateStats() {
    const progress = Math.round((currentQuestionIndex / questions.length) * 100);
    document.getElementById('score').textContent = score;
    document.getElementById('questionNumber').textContent = currentQuestionIndex + 1;
    document.getElementById('progressBar').style.width = `${progress}%`;
    document.getElementById('progressText').textContent = `${progress}%`;
}

// Initialiser le quiz au chargement de la page
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initQuiz);
} else {
    initQuiz();
}


