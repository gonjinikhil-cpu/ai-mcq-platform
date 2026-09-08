# 🧠 AI-Powered MCQ Platform

An AI-powered multiple-choice quiz platform that converts PDF documents and user-defined topics into interactive quizzes with instant answer feedback, AI explanations, score analytics, and history tracking.

[![GitHub Repository](https://img.shields.io/badge/GitHub-gonjinikhil--cpu%2Fai--mcq--platform-181717?style=for-the-badge&logo=github)](https://github.com/gonjinikhil-cpu/ai-mcq-platform)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi)](https://github.com/gonjinikhil-cpu/ai-mcq-platform)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

---

## 🌐 How to Run & Access the Application

Because `127.0.0.1` (localhost) runs locally on a specific machine, here are the **2 ways** to run and view the website on any laptop:

### Method 1: Run Locally on Any Laptop (Recommended for Local Use)
1. **Clone the repository**:
   ```bash
   git clone https://github.com/gonjinikhil-cpu/ai-mcq-platform.git
   cd ai-mcq-platform
   ```
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the Web App**:
   ```bash
   python main.py
   ```
4. Open your browser to **`http://127.0.0.1:8000`**.

---

### Method 2: Host Online Live for FREE (Accessible From Any Device/Laptop)
To get a permanent public link (e.g. `https://ai-mcq-platform.onrender.com`) that anyone can open anywhere:

1. Sign up/Log in at **[Render.com](https://render.com)** (Free).
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository: **`gonjinikhil-cpu/ai-mcq-platform`**.
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy Web Service**! You now get a live public website URL!

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

## 📁 Repository Structure

```
ai-mcq-platform/
├── main.py                     # FastAPI web server & API router
├── Procfile                    # Cloud deployment command
├── requirements.txt            # Python package dependencies
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
