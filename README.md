# 🧠 AI-Powered MCQ Platform

An AI-powered multiple-choice quiz platform that converts PDF documents and user-defined topics into interactive quizzes with instant answer feedback, AI explanations, score analytics, and history tracking.

[![GitHub Repository](https://img.shields.io/badge/GitHub-gonjinikhil--cpu%2Fai--mcq--platform-181717?style=for-the-badge&logo=github)](https://github.com/gonjinikhil-cpu/ai-mcq-platform)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi)](http://127.0.0.1:8000)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

---

## 🔗 Quick Navigation Links

- 🌐 **Live Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📝 **Create New AI Quiz**: [http://127.0.0.1:8000/#home](http://127.0.0.1:8000/#home)
- 📜 **Quiz History & Saved Results**: [http://127.0.0.1:8000/#history](http://127.0.0.1:8000/#history)
- 📖 **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 🐙 **GitHub Project Repository**: [https://github.com/gonjinikhil-cpu/ai-mcq-platform](https://github.com/gonjinikhil-cpu/ai-mcq-platform)

---

## ✨ Features

- 📄 **PDF Question Generation**: Upload lecture slides, chapters, or notes to extract content and automatically generate MCQs.
- 💡 **Topic Question Generation**: Type any topic (e.g. *Operating Systems - Paging*, *CPU Scheduling*, *Data Structures*) to create custom quizzes.
- ⚙️ **Custom Configuration**: Select question counts (**5**, **10**, **20**, **50**) and difficulty (**Easy**, **Medium**, **Hard**).
- ⚡ **Instant Explanation Feedback**: Selecting an option instantly highlights correct (**Green**) or incorrect (**Red**) answers and displays a detailed explanation card.
- 📊 **Performance Analytics**: Visual score gauges, accuracy %, difficulty breakdown, and strong vs. needs improvement topic identification.
- 🕒 **Quiz History**: SQLite database persistence to review past attempts, retake quizzes, and track progress over time.
- 🤖 **Dual AI Engine**: Supports Google Gemini API (`@google/genai`) with an offline smart generator fallback.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn, PyMuPDF (`fitz`), SQLite
- **Frontend**: Single Page Application (SPA), HTML5, Tailwind CSS, Lucide Icons, Chart.js
- **AI Service**: Google Gemini API (`google-genai`) & Smart Offline Generator

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pymupdf google-genai pydantic jinja2 requests
```

### 2. Run Application
```bash
python main.py
```
Open your browser and navigate to `http://127.0.0.1:8000`.

---

## 📁 Repository Structure

```
ai-mcq-platform/
├── main.py                     # FastAPI web server & API router
├── services/
│   ├── pdf_service.py          # PyMuPDF text extraction
│   ├── ai_service.py           # Gemini AI & Offline generator
│   └── db_service.py          # SQLite database storage
├── templates/
│   └── index.html              # Main dashboard UI
└── static/
    └── js/
        └── app.js              # Frontend interactive application logic
```
