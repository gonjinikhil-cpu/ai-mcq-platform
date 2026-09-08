import uuid
import time
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import Optional, Dict, Any, List

from services.pdf_service import PDFService
from services.ai_service import AIService
from services.db_service import DBService

app = FastAPI(title="AI-Powered MCQ Platform")

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static and templates
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    DBService.init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/generate-pdf")
async def generate_pdf_quiz(
    file: UploadFile = File(...),
    count: int = Form(5),
    difficulty: str = Form("Medium"),
    api_key: Optional[str] = Form(None)
):
    try:
        contents = await file.read()
        extracted = PDFService.extract_text_from_bytes(contents)
        
        if not extracted["full_text"]:
            raise HTTPException(status_code=400, detail="Could not extract text from the provided PDF file.")

        quiz_data = AIService.generate_mcqs(
            source_type="pdf",
            content=extracted["full_text"],
            count=count,
            difficulty=difficulty,
            api_key=api_key
        )
        
        quiz_id = str(uuid.uuid4())
        title = f"PDF: {file.filename[:30]}"
        
        DBService.save_quiz(
            quiz_id=quiz_id,
            title=title,
            source_type="pdf",
            difficulty=difficulty,
            count=len(quiz_data["questions"]),
            questions=quiz_data["questions"]
        )
        
        return {
            "quiz_id": quiz_id,
            "title": title,
            "provider": quiz_data.get("provider", "AI"),
            "pdf_pages": extracted["total_pages"],
            "word_count": extracted["word_count"],
            "questions": quiz_data["questions"],
            "note": quiz_data.get("note")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-topic")
async def generate_topic_quiz(
    topic: str = Form(...),
    count: int = Form(5),
    difficulty: str = Form("Medium"),
    api_key: Optional[str] = Form(None)
):
    try:
        if not topic.strip():
            raise HTTPException(status_code=400, detail="Topic prompt cannot be empty.")

        quiz_data = AIService.generate_mcqs(
            source_type="topic",
            content=topic,
            count=count,
            difficulty=difficulty,
            api_key=api_key
        )
        
        quiz_id = str(uuid.uuid4())
        title = f"Topic: {topic[:35]}"
        
        DBService.save_quiz(
            quiz_id=quiz_id,
            title=title,
            source_type="topic",
            difficulty=difficulty,
            count=len(quiz_data["questions"]),
            questions=quiz_data["questions"]
        )
        
        return {
            "quiz_id": quiz_id,
            "title": title,
            "provider": quiz_data.get("provider", "AI"),
            "questions": quiz_data["questions"],
            "note": quiz_data.get("note")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/submit-attempt")
async def submit_quiz_attempt(payload: Dict[str, Any]):
    """
    Submits student quiz responses and generates detailed score analysis, 
    strong vs weak topic breakdowns, and saves to database history.
    """
    quiz_id = payload.get("quiz_id")
    user_answers = payload.get("user_answers", {}) # { "1": 0, "2": 3 }
    time_spent = payload.get("time_spent_seconds", 0)
    questions = payload.get("questions", [])
    
    score = 0
    total = len(questions)
    
    topic_performance = {} # subtopic -> {"correct": int, "total": int}
    difficulty_performance = {"Easy": {"correct": 0, "total": 0}, "Medium": {"correct": 0, "total": 0}, "Hard": {"correct": 0, "total": 0}}
    
    question_results = []
    
    for q in questions:
        q_id = str(q.get("id"))
        correct_idx = q.get("correct_option")
        selected_idx = user_answers.get(q_id)
        
        is_correct = (selected_idx == correct_idx)
        if is_correct:
            score += 1
            
        diff = q.get("difficulty", "Medium")
        if diff in difficulty_performance:
            difficulty_performance[diff]["total"] += 1
            if is_correct:
                difficulty_performance[diff]["correct"] += 1
                
        subtopic = q.get("subtopic", "General")
        if subtopic not in topic_performance:
            topic_performance[subtopic] = {"correct": 0, "total": 0}
        topic_performance[subtopic]["total"] += 1
        if is_correct:
            topic_performance[subtopic]["correct"] += 1
            
        question_results.append({
            "id": q.get("id"),
            "question": q.get("question"),
            "options": q.get("options"),
            "selected_option": selected_idx,
            "correct_option": correct_idx,
            "is_correct": is_correct,
            "explanation": q.get("explanation"),
            "subtopic": subtopic,
            "source_page": q.get("source_page")
        })
        
    accuracy_pct = round((score / total) * 100, 1) if total > 0 else 0
    
    # Calculate Strong vs Weak areas
    strong_areas = []
    needs_improvement = []
    
    for topic_name, stats in topic_performance.items():
        pct = (stats["correct"] / stats["total"]) * 100
        if pct >= 75:
            strong_areas.append(f"{topic_name} ({round(pct)}%)")
        else:
            needs_improvement.append(f"{topic_name} ({round(pct)}%)")
            
    if not strong_areas and score > 0:
        strong_areas = ["General Knowledge"]
    if not needs_improvement and score == total:
        needs_improvement = ["None! Perfect Score!"]
        
    performance_analysis = {
        "score": score,
        "total": total,
        "accuracy_pct": accuracy_pct,
        "difficulty_breakdown": {
            k: f"{round((v['correct']/v['total'])*100)}%" if v['total'] > 0 else "N/A" 
            for k, v in difficulty_performance.items()
        },
        "strong_areas": strong_areas,
        "needs_improvement": needs_improvement,
        "question_results": question_results
    }
    
    attempt_id = str(uuid.uuid4())
    DBService.save_attempt(
        attempt_id=attempt_id,
        quiz_id=quiz_id,
        score=score,
        total=total,
        accuracy_pct=accuracy_pct,
        time_spent=time_spent,
        user_answers=user_answers,
        performance_analysis=performance_analysis
    )
    
    return {
        "attempt_id": attempt_id,
        "analysis": performance_analysis
    }


@app.get("/api/history")
async def get_quiz_history():
    history = DBService.get_history()
    return {"history": history}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
