import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "quiz_platform.db")

class DBService:
    @staticmethod
    def init_db():
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Quizzes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source_type TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            question_count INTEGER NOT NULL,
            questions_json TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
        ''')
        
        # Attempts & Results table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id TEXT PRIMARY KEY,
            quiz_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            accuracy_pct REAL NOT NULL,
            time_spent_seconds INTEGER NOT NULL,
            user_answers_json TEXT NOT NULL,
            performance_analysis_json TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
        ''')
        
        conn.commit()
        conn.close()

    @staticmethod
    def save_quiz(quiz_id: str, title: str, source_type: str, difficulty: str, count: int, questions: list) -> dict:
        DBService.init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        created_at = int(time.time())
        
        cursor.execute('''
        INSERT OR REPLACE INTO quizzes (id, title, source_type, difficulty, question_count, questions_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (quiz_id, title, source_type, difficulty, count, json.dumps(questions), created_at))
        
        conn.commit()
        conn.close()
        return {"id": quiz_id, "title": title, "created_at": created_at}

    @staticmethod
    def save_attempt(
        attempt_id: str,
        quiz_id: str,
        score: int,
        total: int,
        accuracy_pct: float,
        time_spent: int,
        user_answers: dict,
        performance_analysis: dict
    ) -> dict:
        DBService.init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        created_at = int(time.time())
        
        cursor.execute('''
        INSERT INTO quiz_attempts (id, quiz_id, score, total_questions, accuracy_pct, time_spent_seconds, user_answers_json, performance_analysis_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (attempt_id, quiz_id, score, total, accuracy_pct, time_spent, json.dumps(user_answers), json.dumps(performance_analysis), created_at))
        
        conn.commit()
        conn.close()
        return {"id": attempt_id, "score": score, "total": total, "accuracy": accuracy_pct}

    @staticmethod
    def get_history() -> List[Dict[str, Any]]:
        DBService.init_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            a.id as attempt_id,
            q.id as quiz_id,
            q.title,
            q.source_type,
            q.difficulty,
            a.score,
            a.total_questions,
            a.accuracy_pct,
            a.time_spent_seconds,
            a.performance_analysis_json,
            a.created_at
        FROM quiz_attempts a
        JOIN quizzes q ON a.quiz_id = q.id
        ORDER BY a.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        history = []
        for r in rows:
            history.append({
                "attempt_id": r["attempt_id"],
                "quiz_id": r["quiz_id"],
                "title": r["title"],
                "source_type": r["source_type"],
                "difficulty": r["difficulty"],
                "score": r["score"],
                "total_questions": r["total_questions"],
                "accuracy_pct": r["accuracy_pct"],
                "time_spent": r["time_spent_seconds"],
                "performance": json.loads(r["performance_analysis_json"]) if r["performance_analysis_json"] else {},
                "created_at": r["created_at"]
            })
            
        conn.close()
        return history
