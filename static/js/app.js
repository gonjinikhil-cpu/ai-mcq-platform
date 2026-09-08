/**
 * AI-Powered MCQ Platform - Frontend Controller
 */

class MCQApp {
    constructor() {
        this.mode = 'pdf'; // 'pdf' or 'topic'
        this.selectedFile = null;
        this.count = 10;
        this.difficulty = 'Medium';
        this.apiKey = localStorage.getItem('gemini_api_key') || '';

        // Active Quiz State
        this.currentQuiz = null;
        this.currentQuestionIdx = 0;
        this.userAnswers = {}; // { q_id: option_idx }
        this.quizStartTime = 0;
        this.timerInterval = null;

        this.init();
    }

    init() {
        if (this.apiKey) {
            document.getElementById('gemini-api-key-input').value = this.apiKey;
        }

        // Setup Drag & Drop
        const dropzone = document.getElementById('dropzone');
        if (dropzone) {
            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropzone.classList.add('border-blue-500', 'bg-blue-500/10');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropzone.classList.remove('border-blue-500', 'bg-blue-500/10');
                });
            });

            dropzone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0 && files[0].type === 'application/pdf') {
                    this.setFile(files[0]);
                }
            });
        }
    }

    setMode(mode) {
        this.mode = mode;
        const pdfTab = document.getElementById('tab-pdf');
        const topicTab = document.getElementById('tab-topic');
        const pdfSec = document.getElementById('section-pdf-input');
        const topicSec = document.getElementById('section-topic-input');

        if (mode === 'pdf') {
            pdfTab.className = 'py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 bg-blue-600 text-white shadow-md';
            topicTab.className = 'py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 text-slate-400 hover:text-white';
            pdfSec.classList.remove('hidden');
            topicSec.classList.add('hidden');
        } else {
            topicTab.className = 'py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 bg-blue-600 text-white shadow-md';
            pdfTab.className = 'py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 text-slate-400 hover:text-white';
            topicSec.classList.remove('hidden');
            pdfSec.classList.add('hidden');
        }
    }

    handleFileSelect(e) {
        if (e.target.files.length > 0) {
            this.setFile(e.target.files[0]);
        }
    }

    setFile(file) {
        this.selectedFile = file;
        const label = document.getElementById('file-label');
        if (label) {
            label.innerHTML = `Selected: <span class="text-blue-400 font-bold">${file.name}</span> (${(file.size / (1024*1024)).toFixed(2)} MB)`;
        }
    }

    setQuickTopic(topicName) {
        this.setMode('topic');
        document.getElementById('topic-input').value = topicName;
    }

    setCount(num) {
        this.count = num;
        document.querySelectorAll('.btn-count').forEach(btn => {
            if (parseInt(btn.getAttribute('data-count')) === num) {
                btn.className = 'btn-count py-2 text-sm font-bold rounded-lg border border-blue-500 bg-blue-600 text-white shadow-md';
            } else {
                btn.className = 'btn-count py-2 text-sm font-bold rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:border-blue-500 hover:text-white';
            }
        });
    }

    setDifficulty(diff) {
        this.difficulty = diff;
        document.querySelectorAll('.btn-diff').forEach(btn => {
            const attr = btn.getAttribute('data-diff');
            if (attr === diff) {
                const colorMap = {
                    'Easy': 'border-emerald-500 bg-emerald-500/10 text-emerald-400',
                    'Medium': 'border-amber-500 bg-amber-500/10 text-amber-400',
                    'Hard': 'border-rose-500 bg-rose-500/10 text-rose-400'
                };
                btn.className = `btn-diff py-2 text-sm font-bold rounded-lg border ${colorMap[diff]}`;
            } else {
                btn.className = 'btn-diff py-2 text-sm font-bold rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500';
            }
        });
    }

    toggleSettingsModal() {
        const modal = document.getElementById('settings-modal');
        modal.classList.toggle('hidden');
    }

    saveApiKey() {
        const key = document.getElementById('gemini-api-key-input').value.trim();
        this.apiKey = key;
        localStorage.setItem('gemini_api_key', key);
        this.toggleSettingsModal();
        alert('Settings saved successfully!');
    }

    showPage(pageId) {
        ['home', 'quiz', 'results', 'history'].forEach(p => {
            const el = document.getElementById(`page-${p}`);
            if (el) {
                if (p === pageId) el.classList.remove('hidden');
                else el.classList.add('hidden');
            }
        });

        if (pageId === 'history') {
            this.loadHistory();
        }
    }

    async generateQuiz() {
        const spinner = document.getElementById('loading-spinner');
        const btnGen = document.getElementById('btn-generate');

        if (this.mode === 'pdf' && !this.selectedFile) {
            alert('Please select or drop a PDF file first!');
            return;
        }

        if (this.mode === 'topic' && !document.getElementById('topic-input').value.trim()) {
            alert('Please enter a topic name!');
            return;
        }

        spinner.classList.remove('hidden');
        btnGen.disabled = true;
        btnGen.classList.add('opacity-50');

        try {
            const formData = new FormData();
            formData.append('count', this.count);
            formData.append('difficulty', this.difficulty);
            if (this.apiKey) formData.append('api_key', this.apiKey);

            let endpoint = '';
            if (this.mode === 'pdf') {
                endpoint = '/api/generate-pdf';
                formData.append('file', this.selectedFile);
            } else {
                endpoint = '/api/generate-topic';
                formData.append('topic', document.getElementById('topic-input').value.trim());
            }

            const res = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to generate quiz');
            }

            const data = await res.json();
            this.startQuiz(data);

        } catch (err) {
            alert('Error: ' + err.message);
        } finally {
            spinner.classList.add('hidden');
            btnGen.disabled = false;
            btnGen.classList.remove('opacity-50');
        }
    }

    startQuiz(quizData) {
        this.currentQuiz = quizData;
        this.currentQuestionIdx = 0;
        this.userAnswers = {};
        this.quizStartTime = Date.now();

        document.getElementById('quiz-title-badge').innerText = quizData.title;
        this.startTimer();
        this.renderQuestion();
        this.showPage('quiz');
    }

    startTimer() {
        if (this.timerInterval) clearInterval(this.timerInterval);
        const timerEl = document.getElementById('timer-display');

        this.timerInterval = setInterval(() => {
            const elapsedSeconds = Math.floor((Date.now() - this.quizStartTime) / 1000);
            const mins = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
            const secs = String(elapsedSeconds % 60).padStart(2, '0');
            timerEl.innerText = `${mins}:${secs}`;
        }, 1000);
    }

    renderQuestion() {
        const q = this.currentQuiz.questions[this.currentQuestionIdx];
        const total = this.currentQuiz.questions.length;

        // Counter & Progress
        document.getElementById('quiz-question-counter').innerText = `Question ${this.currentQuestionIdx + 1} / ${total}`;
        const pct = ((this.currentQuestionIdx + 1) / total) * 100;
        document.getElementById('quiz-progress-bar').style.width = `${pct}%`;

        // Tags & Text
        document.getElementById('q-subtopic-tag').innerText = `Subtopic: ${q.subtopic || 'General'}`;
        const pageEl = document.getElementById('q-source-page');
        if (q.source_page) {
            pageEl.innerText = `PDF Page ${q.source_page}`;
            pageEl.classList.remove('hidden');
        } else {
            pageEl.classList.add('hidden');
        }
        document.getElementById('q-text').innerText = q.question;

        // Options Rendering
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        const selectedIdx = this.userAnswers[q.id];
        const hasAnswered = selectedIdx !== undefined;

        q.options.forEach((optText, idx) => {
            const btn = document.createElement('button');
            btn.className = 'w-full text-left p-4 rounded-xl border transition-all duration-200 flex items-start gap-3.5 relative group font-medium text-sm md:text-base';
            
            // Base style
            if (!hasAnswered) {
                btn.className += ' border-slate-700 bg-slate-800/80 hover:border-blue-500 hover:bg-blue-500/10 text-slate-200 cursor-pointer';
            } else {
                if (idx === q.correct_option) {
                    btn.className += ' border-emerald-500 bg-emerald-500/20 text-emerald-200 font-bold shadow-lg shadow-emerald-500/10';
                } else if (idx === selectedIdx) {
                    btn.className += ' border-rose-500 bg-rose-500/20 text-rose-200 font-bold';
                } else {
                    btn.className += ' border-slate-800 bg-slate-900/40 text-slate-500 opacity-60';
                }
            }

            const prefixLetter = String.fromCharCode(65 + idx); // A, B, C, D
            btn.innerHTML = `
                <span class="flex-shrink-0 w-7 h-7 rounded-lg bg-slate-900 border border-slate-700 text-xs font-bold flex items-center justify-center ${hasAnswered && idx === q.correct_option ? 'border-emerald-400 text-emerald-400 bg-emerald-950' : ''}">
                    ${prefixLetter}
                </span>
                <span class="flex-1 mt-0.5">${optText}</span>
            `;

            btn.onclick = () => this.selectOption(q.id, idx);
            optionsContainer.appendChild(btn);
        });

        // Explanation Box
        const expBox = document.getElementById('explanation-box');
        if (hasAnswered) {
            expBox.classList.remove('hidden');
            const isCorrect = (selectedIdx === q.correct_option);
            const badge = document.getElementById('explanation-badge');
            
            if (isCorrect) {
                expBox.className = 'p-5 rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-emerald-200 animate-fade-in space-y-2';
                badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5';
                badge.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4"></i> Correct Answer!`;
            } else {
                expBox.className = 'p-5 rounded-xl border border-rose-500/40 bg-rose-500/10 text-rose-200 animate-fade-in space-y-2';
                badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1.5';
                badge.innerHTML = `<i data-lucide="x-circle" class="w-4 h-4"></i> Incorrect Choice`;
            }
            
            document.getElementById('explanation-text').innerText = q.explanation;
            lucide.createIcons();
        } else {
            expBox.classList.add('hidden');
        }

        // Prev / Next button state
        document.getElementById('btn-prev-q').disabled = (this.currentQuestionIdx === 0);
        const btnNext = document.getElementById('btn-next-q');
        if (this.currentQuestionIdx === total - 1) {
            btnNext.innerHTML = `<span>Submit Quiz</span> <i data-lucide="check-square" class="w-4 h-4"></i>`;
            btnNext.className = 'px-6 py-2.5 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-lg shadow-emerald-600/30 transition flex items-center gap-2';
        } else {
            btnNext.innerHTML = `<span>Next Question</span> <i data-lucide="arrow-right" class="w-4 h-4"></i>`;
            btnNext.className = 'px-6 py-2.5 text-sm font-bold text-white bg-blue-600 hover:bg-blue-500 rounded-lg shadow-lg shadow-blue-600/30 transition flex items-center gap-2';
        }
        lucide.createIcons();
    }

    selectOption(qId, optionIdx) {
        this.userAnswers[qId] = optionIdx;
        this.renderQuestion();
    }

    prevQuestion() {
        if (this.currentQuestionIdx > 0) {
            this.currentQuestionIdx--;
            this.renderQuestion();
        }
    }

    nextQuestion() {
        const total = this.currentQuiz.questions.length;
        if (this.currentQuestionIdx < total - 1) {
            this.currentQuestionIdx++;
            this.renderQuestion();
        } else {
            this.submitQuiz();
        }
    }

    async submitQuiz() {
        clearInterval(this.timerInterval);
        const timeSpent = Math.floor((Date.now() - this.quizStartTime) / 1000);

        try {
            const res = await fetch('/api/submit-attempt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    quiz_id: this.currentQuiz.quiz_id,
                    user_answers: this.userAnswers,
                    time_spent_seconds: timeSpent,
                    questions: this.currentQuiz.questions
                })
            });

            if (!res.ok) throw new Error('Failed to submit quiz results');
            const data = await res.json();
            this.renderResults(data.analysis, timeSpent);
            this.showPage('results');
        } catch (err) {
            alert('Submission error: ' + err.message);
        }
    }

    renderResults(analysis, timeSpentSeconds) {
        document.getElementById('results-title').innerText = this.currentQuiz.title;
        
        const mins = Math.floor(timeSpentSeconds / 60);
        const secs = timeSpentSeconds % 60;
        document.getElementById('results-time-spent').innerText = `Time Spent: ${mins}m ${secs}s`;

        document.getElementById('res-score-num').innerText = `${analysis.score} / ${analysis.total}`;
        document.getElementById('res-accuracy-pct').innerText = `${analysis.accuracy_pct}%`;

        // Render Strong Areas
        const strongUl = document.getElementById('list-strong-areas');
        strongUl.innerHTML = analysis.strong_areas.map(item => 
            `<li class="flex items-center gap-2 bg-emerald-500/10 px-3 py-2 rounded-lg border border-emerald-500/20 text-emerald-300">
                <span>• ${item}</span>
            </li>`
        ).join('');

        // Render Needs Improvement
        const weakUl = document.getElementById('list-needs-improvement');
        weakUl.innerHTML = analysis.needs_improvement.map(item => 
            `<li class="flex items-center gap-2 bg-rose-500/10 px-3 py-2 rounded-lg border border-rose-500/20 text-rose-300">
                <span>• ${item}</span>
            </li>`
        ).join('');

        // Render Detailed Review List
        const reviewList = document.getElementById('questions-review-list');
        reviewList.innerHTML = analysis.question_results.map((item, idx) => {
            const isCorrect = item.is_correct;
            const userLetter = item.selected_option !== undefined ? String.fromCharCode(65 + item.selected_option) : 'None';
            const correctLetter = String.fromCharCode(65 + item.correct_option);

            return `
                <div class="p-4 rounded-xl border ${isCorrect ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-rose-500/30 bg-rose-500/5'} space-y-2">
                    <div class="flex items-start justify-between gap-3">
                        <h4 class="font-bold text-slate-100 text-sm md:text-base">${idx + 1}. ${item.question}</h4>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${isCorrect ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}">
                            ${isCorrect ? 'Correct' : 'Incorrect'}
                        </span>
                    </div>

                    <div class="text-xs space-y-1 text-slate-300">
                        <p>Your Answer: <span class="${isCorrect ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}">${userLetter} - ${item.selected_option !== undefined ? item.options[item.selected_option] : 'Not Answered'}</span></p>
                        ${!isCorrect ? `<p>Correct Answer: <span class="text-emerald-400 font-bold">${correctLetter} - ${item.options[item.correct_option]}</span></p>` : ''}
                    </div>

                    <p class="text-xs text-slate-400 bg-slate-900/60 p-3 rounded-lg border border-slate-800 leading-relaxed">
                        <strong class="text-slate-300">Explanation:</strong> ${item.explanation}
                    </p>
                </div>
            `;
        }).join('');

        lucide.createIcons();
    }

    async loadHistory() {
        try {
            const res = await fetch('/api/history');
            const data = await res.json();

            const tbody = document.getElementById('history-table-body');
            if (data.history.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-slate-500">No past quiz attempts found. Start a quiz now!</td></tr>`;
                return;
            }

            tbody.innerHTML = data.history.map(item => {
                const dateStr = new Date(item.created_at * 1000).toLocaleDateString(undefined, {
                    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                });
                return `
                    <tr class="hover:bg-slate-800/40 transition">
                        <td class="p-4 font-semibold text-slate-200">${item.title}</td>
                        <td class="p-4 uppercase text-xs font-bold text-blue-400">${item.source_type}</td>
                        <td class="p-4"><span class="px-2 py-0.5 text-xs rounded bg-slate-800 border border-slate-700">${item.difficulty}</span></td>
                        <td class="p-4 font-bold text-blue-300">${item.score} / ${item.total_questions}</td>
                        <td class="p-4 font-bold ${item.accuracy_pct >= 75 ? 'text-emerald-400' : 'text-amber-400'}">${item.accuracy_pct}%</td>
                        <td class="p-4 text-xs text-slate-400">${dateStr}</td>
                    </tr>
                `;
            }).join('');
        } catch (err) {
            console.error('Error loading history:', err);
        }
    }
}

// Instantiate global app
window.app = new MCQApp();
