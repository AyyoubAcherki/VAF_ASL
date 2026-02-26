// ===== ANALYTICS PAGE =====
let typeChart = null;
let classChart = null;
let dailyChart = null;
let confidenceChart = null;

// Variables pour les graphiques de quiz
let scoresChart = null;
let distributionChart = null;
let errorsChart = null;
let quizDailyChart = null;

// Charger les données au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    // Vérifier si un onglet spécifique est demandé via l'URL
    const urlParams = new URLSearchParams(window.location.search);
    const requestedTab = urlParams.get('tab');

    if (requestedTab === 'quiz') {
        switchAnalyticsTab('quiz');
    } else {
        loadAnalytics();
        // Charger les données de quiz si l'onglet quiz est actif
        const quizTab = document.getElementById('quizTab');
        if (quizTab && quizTab.style.display !== 'none') {
            loadQuizAnalysis();
        }
    }
});

// Fonction pour basculer entre les onglets
function switchAnalyticsTab(tab) {
    // Masquer tous les contenus
    document.querySelectorAll('.analytics-tab-content').forEach(content => {
        content.style.display = 'none';
    });

    // Masquer tous les boutons
    document.querySelectorAll('.analytics-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Afficher l'onglet sélectionné
    if (tab === 'predictions') {
        document.getElementById('predictionsTab').style.display = 'block';
        document.querySelectorAll('.analytics-tab-btn')[0].classList.add('active');
    } else if (tab === 'quiz') {
        document.getElementById('quizTab').style.display = 'block';
        document.querySelectorAll('.analytics-tab-btn')[1].classList.add('active');
        // Charger les données de quiz si pas encore chargées
        loadQuizAnalysis();
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics/stats');
        const data = await response.json();

        if (response.ok) {
            updateStats(data);
            updateCharts(data);
            updateTable(data);
        } else {
            console.error('Erreur lors du chargement des données:', data.error);
            alert('Erreur lors du chargement des données: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors du chargement des données');
    }
}

function updateStats(data) {
    let totalPredictions = 0;
    let totalConfidence = 0;
    let predictionTypes = {};
    let uniqueClasses = new Set();

    if (!data.stats || data.stats.length === 0) {
        document.getElementById('totalPredictions').textContent = '0';
        document.getElementById('avgConfidence').textContent = '0%';
        document.getElementById('predictionTypes').textContent = '0';
        document.getElementById('uniqueClasses').textContent = '0';
        return;
    }

    data.stats.forEach(stat => {
        totalPredictions += stat.total_predictions;
        totalConfidence += (stat.avg_confidence || 0) * stat.total_predictions;
        predictionTypes[stat.prediction_type] = stat.total_predictions;
    });

    if (data.classes && Array.isArray(data.classes)) {
        data.classes.forEach(cls => {
            if (cls.predicted_class) uniqueClasses.add(cls.predicted_class);
        });
    }

    const avgConfidence = totalPredictions > 0 ? (totalConfidence / totalPredictions) * 100 : 0;

    // Mettre à jour l'affichage
    document.getElementById('totalPredictions').textContent = totalPredictions;
    document.getElementById('avgConfidence').textContent = avgConfidence.toFixed(1) + '%';
    document.getElementById('predictionTypes').textContent = Object.keys(predictionTypes).length;
    document.getElementById('uniqueClasses').textContent = uniqueClasses.size;
}

function updateCharts(data) {
    // Graphique par type
    const typeCtx = document.getElementById('typeChart').getContext('2d');
    if (typeChart) {
        typeChart.destroy();
    }

    const typeLabels = data.stats.map(s => s.prediction_type);
    const typeData = data.stats.map(s => s.total_predictions);

    typeChart = new Chart(typeCtx, {
        type: 'doughnut',
        data: {
            labels: typeLabels,
            datasets: [{
                data: typeData,
                backgroundColor: [
                    '#004E89',
                    '#FF6B35',
                    '#1A659E'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });

    // Graphique par classe (top 10)
    const classCtx = document.getElementById('classChart').getContext('2d');
    if (classChart) {
        classChart.destroy();
    }

    const topClasses = data.classes.slice(0, 10);
    const classLabels = topClasses.map(c => c.predicted_class);
    const classData = topClasses.map(c => c.count);

    classChart = new Chart(classCtx, {
        type: 'bar',
        data: {
            labels: classLabels,
            datasets: [{
                label: 'Nombre de prédictions',
                data: classData,
                backgroundColor: '#FF6B35'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Graphique par jour
    const dailyCtx = document.getElementById('dailyChart').getContext('2d');
    if (dailyChart) {
        dailyChart.destroy();
    }

    const dailyLabels = data.daily.map(d => new Date(d.date).toLocaleDateString('fr-FR'));
    const dailyData = data.daily.map(d => d.count);

    dailyChart = new Chart(dailyCtx, {
        type: 'line',
        data: {
            labels: dailyLabels.reverse(),
            datasets: [{
                label: 'Prédictions par jour',
                data: dailyData.reverse(),
                borderColor: '#004E89',
                backgroundColor: 'rgba(0, 78, 137, 0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Graphique de confiance par type
    const confidenceCtx = document.getElementById('confidenceChart').getContext('2d');
    if (confidenceChart) {
        confidenceChart.destroy();
    }

    const confidenceLabels = data.stats.map(s => s.prediction_type);
    const confidenceData = data.stats.map(s => s.avg_confidence * 100);

    confidenceChart = new Chart(confidenceCtx, {
        type: 'bar',
        data: {
            labels: confidenceLabels,
            datasets: [{
                label: 'Confiance moyenne (%)',
                data: confidenceData,
                backgroundColor: '#1A659E'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

async function updateTable(data) {
    // Charger les données détaillées pour le tableau
    try {
        const response = await fetch('/api/powerbi/export');
        const exportData = await response.json();

        if (response.ok && exportData.data) {
            const tableBody = document.getElementById('predictionsTableBody');
            tableBody.innerHTML = '';

            // Afficher les 50 dernières prédictions
            const recentPredictions = exportData.data.slice(0, 50);

            recentPredictions.forEach(prediction => {
                const row = document.createElement('tr');
                const date = new Date(prediction.created_at).toLocaleString('fr-FR');
                row.innerHTML = `
                    <td>${date}</td>
                    <td>${prediction.prediction_type}</td>
                    <td>${prediction.predicted_class}</td>
                    <td>${(prediction.confidence * 100).toFixed(2)}%</td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Erreur lors du chargement du tableau:', error);
    }
}

// ===== QUIZ ANALYSIS FUNCTIONS =====

async function loadQuizAnalysis() {
    try {
        const loadingMsg = document.getElementById('recentResultsBody');
        if (loadingMsg) {
            loadingMsg.innerHTML = '<tr><td colspan="5" style="text-align: center;">Chargement...</td></tr>';
        }

        const response = await fetch('/api/quiz/analysis');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            console.error('Erreur API:', data.error);
            return;
        }

        updateQuizStats(data);
        updateQuizCharts(data);
        updateQuizRecentResults(data);
        updateQuizPredictions(data);
    } catch (error) {
        console.error('Erreur:', error);
        const tbody = document.getElementById('recentResultsBody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Erreur lors du chargement des données</td></tr>';
        }
    }
}

function updateQuizStats(data) {
    const stats = data.stats;

    const totalQuizzesEl = document.getElementById('totalQuizzes');
    const avgScoreEl = document.getElementById('avgScore');
    const bestScoreEl = document.getElementById('bestScore');
    const avgDurationEl = document.getElementById('avgDuration');

    if (totalQuizzesEl) totalQuizzesEl.textContent = stats.total_quizzes || 0;
    if (avgScoreEl) avgScoreEl.textContent = stats.avg_score ? stats.avg_score.toFixed(1) + '%' : '-';
    if (bestScoreEl) bestScoreEl.textContent = stats.best_score ? stats.best_score.toFixed(1) + '%' : '-';

    if (avgDurationEl) {
        if (stats.avg_duration) {
            const minutes = Math.floor(stats.avg_duration / 60);
            const seconds = Math.round(stats.avg_duration % 60);
            avgDurationEl.textContent = minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
        } else {
            avgDurationEl.textContent = '-';
        }
    }
}

function updateQuizCharts(data) {
    // Graphique d'évolution des scores
    const scoresCtx = document.getElementById('scoresChart');
    if (scoresCtx) {
        if (scoresChart) scoresChart.destroy();

        const recentScores = (data.recent && data.recent.length > 0) ? data.recent.slice(0, 10).reverse() : [];

        if (recentScores.length > 0) {
            const scoreLabels = recentScores.map((r, i) => `Quiz ${i + 1}`);
            const scoreData = recentScores.map(r => parseFloat(r.score_percentage));

            scoresChart = new Chart(scoresCtx, {
                type: 'line',
                data: {
                    labels: scoreLabels,
                    datasets: [{
                        label: 'Score (%)',
                        data: scoreData,
                        borderColor: '#004E89',
                        backgroundColor: 'rgba(0, 78, 137, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }

    // Graphique de distribution
    const distributionCtx = document.getElementById('distributionChart');
    if (distributionCtx) {
        if (distributionChart) distributionChart.destroy();

        if (data.score_distribution && data.score_distribution.length > 0) {
            const distLabels = data.score_distribution.map(d => d.score_range);
            const distData = data.score_distribution.map(d => d.count);

            distributionChart = new Chart(distributionCtx, {
                type: 'doughnut',
                data: {
                    labels: distLabels,
                    datasets: [{
                        data: distData,
                        backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true
                }
            });
        }
    }

    // Graphique des erreurs
    const errorsCtx = document.getElementById('errorsChart');
    if (errorsCtx) {
        if (errorsChart) errorsChart.destroy();

        if (data.top_errors && data.top_errors.length > 0) {
            const errorLabels = data.top_errors.map(e => e.sign);
            const errorData = data.top_errors.map(e => e.count);

            errorsChart = new Chart(errorsCtx, {
                type: 'bar',
                data: {
                    labels: errorLabels,
                    datasets: [{
                        label: 'Nombre d\'erreurs',
                        data: errorData,
                        backgroundColor: '#FF6B35'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    // Graphique quiz par jour
    const quizDailyCtx = document.getElementById('quizDailyChart');
    if (quizDailyCtx) {
        if (quizDailyChart) quizDailyChart.destroy();

        if (data.daily && data.daily.length > 0) {
            const dailyLabels = data.daily.map(d => new Date(d.date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' }));
            const dailyCount = data.daily.map(d => d.count);
            const dailyAvgScore = data.daily.map(d => parseFloat(d.avg_score));

            quizDailyChart = new Chart(quizDailyCtx, {
                type: 'bar',
                data: {
                    labels: dailyLabels.reverse(),
                    datasets: [
                        {
                            label: 'Nombre de quiz',
                            data: dailyCount.reverse(),
                            backgroundColor: '#1A659E',
                            yAxisID: 'y'
                        },
                        {
                            label: 'Score moyen (%)',
                            data: dailyAvgScore.reverse(),
                            type: 'line',
                            borderColor: '#FF6B35',
                            backgroundColor: 'rgba(255, 107, 53, 0.1)',
                            yAxisID: 'y1',
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                }
            });
        }
    }
}

function updateQuizRecentResults(data) {
    const tbody = document.getElementById('recentResultsBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (data.recent && data.recent.length > 0) {
        data.recent.forEach(result => {
            const row = document.createElement('tr');
            const date = new Date(result.created_at).toLocaleString('fr-FR');
            const duration = formatQuizDuration(result.quiz_duration);

            row.innerHTML = `
                <td>${date}</td>
                <td><strong>${parseFloat(result.score_percentage).toFixed(1)}%</strong></td>
                <td>${result.correct_answers}/${result.total_questions}</td>
                <td>${result.total_questions}</td>
                <td>${duration}</td>
            `;
            tbody.appendChild(row);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucun résultat de quiz encore</td></tr>';
    }
}

function updateQuizPredictions(data) {
    const tbody = document.getElementById('predictionBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (data.prediction_accuracy && data.prediction_accuracy.length > 0) {
        data.prediction_accuracy.forEach(pred => {
            const row = document.createElement('tr');
            const accuracy = pred.accuracy;
            const accuracyColor = accuracy >= 80 ? '#28a745' : accuracy >= 60 ? '#ffc107' : '#dc3545';

            row.innerHTML = `
                <td><strong>${pred.sign}</strong></td>
                <td>${pred.total}</td>
                <td>${pred.correct}</td>
                <td><strong style="color: ${accuracyColor}">${accuracy}%</strong></td>
                <td>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${accuracy}%; background-color: ${accuracyColor};"></div>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucune donnée de prédiction disponible</td></tr>';
    }
}

function formatQuizDuration(seconds) {
    if (!seconds) return '-';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return minutes > 0 ? `${minutes}m ${secs}s` : `${secs}s`;
}

