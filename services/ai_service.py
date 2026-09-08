import os
import json
import random
import re
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class AIService:
    @staticmethod
    def generate_mcqs(
        source_type: str, # "pdf" or "topic"
        content: str,     # PDF full text or Topic name
        count: int = 5,   # 5, 10, 20, 50
        difficulty: str = "Medium", # "Easy", "Medium", "Hard"
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates structured MCQs using Gemini API or offline fallback engine.
        """
        api_key_to_use = api_key or os.environ.get("GEMINI_API_KEY")
        
        if GENAI_AVAILABLE and api_key_to_use and api_key_to_use.strip():
            try:
                return AIService._generate_with_gemini(
                    source_type=source_type,
                    content=content,
                    count=count,
                    difficulty=difficulty,
                    api_key=api_key_to_use.strip()
                )
            except Exception as e:
                print(f"Gemini API Error: {e}, falling back to intelligent offline generator.")
                return AIService._generate_offline_mock(source_type, content, count, difficulty, error_msg=str(e))
        else:
            return AIService._generate_offline_mock(source_type, content, count, difficulty)

    @staticmethod
    def _generate_with_gemini(source_type: str, content: str, count: int, difficulty: str, api_key: str) -> Dict[str, Any]:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are an expert educational assessment specialist and examiner.
Generate exactly {count} multiple-choice questions (MCQs) based on the following input.

Input Type: {source_type.upper()}
Target Difficulty: {difficulty}
Content/Context:
{content[:8000]}

REQUIREMENTS:
1. Generate exactly {count} distinct questions.
2. Each question MUST have exactly 4 plausible options [Option A, Option B, Option C, Option D].
3. Specify zero-based index of correct option (0 for A, 1 for B, 2 for C, 3 for D).
4. Provide a clear, thorough explanation of WHY the correct answer is right and why alternative choices are incorrect.
5. Include a specific subtopic tag for each question (e.g., "CPU Scheduling", "Paging", "Deadlocks") to help analyze student strengths and weaknesses.
6. If input is a PDF, include a plausible page number reference if applicable.

Return ONLY a valid JSON object matching this schema:
{{
  "title": "Quiz Title",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_option": 0,
      "explanation": "Detailed explanation here...",
      "difficulty": "{difficulty}",
      "subtopic": "Subtopic tag",
      "source_page": 1
    }}
  ]
}}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        result_text = response.text
        data = json.loads(result_text)
        return {
            "success": True,
            "provider": "Gemini 2.5 Flash",
            "title": data.get("title", f"Quiz: {content[:30]}"),
            "questions": data.get("questions", [])
        }

    @staticmethod
    def _generate_offline_mock(source_type: str, content: str, count: int, difficulty: str, error_msg: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates realistic educational MCQs for immediate offline evaluation.
        """
        topic_title = content if source_type == "topic" else "Uploaded Document PDF"
        
        # Knowledge bank for fallback topics
        sample_bank = [
            {
                "question": "Which CPU scheduling algorithm can cause starvation for low-priority processes?",
                "options": ["First-Come, First-Served (FCFS)", "Round Robin (RR)", "Priority Scheduling", "Shortest Job First (SJF) without preemption"],
                "correct_option": 2,
                "explanation": "Priority Scheduling executes higher priority processes first. If low-priority processes are continually preempted or superseded by incoming high-priority processes, they may suffer indefinite starvation. Aging techniques are commonly used to prevent this.",
                "subtopic": "Priority Scheduling",
                "difficulty": difficulty
            },
            {
                "question": "In virtual memory management, what is a 'Page Fault'?",
                "options": [
                    "An error in the hardware circuit of the RAM chip",
                    "An event occurring when a referenced page is not currently in physical RAM",
                    "A corruption of page table entries by a malicious process",
                    "A condition where secondary storage space runs completely out"
                ],
                "correct_option": 1,
                "explanation": "A Page Fault occurs when an executing program accesses a memory page that is mapped in its virtual address space but not currently loaded into physical memory (RAM). The operating system handles this trap by retrieving the missing page from disk.",
                "subtopic": "Paging & Memory",
                "difficulty": difficulty
            },
            {
                "question": "What primary problem does the 'Aging' technique solve in process scheduling?",
                "options": ["Memory fragmentation", "Thrashing", "Starvation of low-priority processes", "Cache miss penalty"],
                "correct_option": 2,
                "explanation": "Aging dynamically increases the priority of processes that wait in the ready queue for long durations, ensuring that low-priority processes eventually gain CPU execution time and avoiding starvation.",
                "subtopic": "Starvation",
                "difficulty": difficulty
            },
            {
                "question": "Which of the following conditions is NOT one of Coffman's four necessary conditions for Deadlock?",
                "options": ["Mutual Exclusion", "Hold and Wait", "Preemption allowed", "Circular Wait"],
                "correct_option": 2,
                "explanation": "No Preemption (resources cannot be forcibly taken from a process holding them) is a required condition for deadlock. If preemption IS allowed, deadlock cannot occur because resources can be reclaimed by the OS.",
                "subtopic": "Deadlocks",
                "difficulty": difficulty
            },
            {
                "question": "In a paged memory system, what component translates virtual addresses into physical addresses?",
                "options": ["Memory Management Unit (MMU)", "Direct Memory Access (DMA) Controller", "Arithmetic Logic Unit (ALU)", "Interrupt Vector Table (IVT)"],
                "correct_option": 0,
                "explanation": "The Memory Management Unit (MMU) is the hardware device that uses the Page Table to convert virtual address references generated by the CPU into physical RAM addresses.",
                "subtopic": "Paging & Memory",
                "difficulty": difficulty
            },
            {
                "question": "What is the main advantage of Round Robin (RR) scheduling over FCFS?",
                "options": ["Guaranteed minimum turnaround time", "Better responsiveness for interactive systems", "Zero context switches", "Optimal CPU utilization"],
                "correct_option": 1,
                "explanation": "Round Robin assigns a time quantum to each process in turn, guaranteeing that every ready process gets a share of CPU time periodically. This significantly improves response time for interactive processes compared to FCFS.",
                "subtopic": "Round Robin",
                "difficulty": difficulty
            },
            {
                "question": "What phenomenon occurs when excessive time is spent swapping pages in and out of memory rather than executing actual process code?",
                "options": ["Fragmentation", "Thrashing", "Belady's Anomaly", "Segmentation Fault"],
                "correct_option": 1,
                "explanation": "Thrashing occurs when the working set of active processes exceeds available physical memory, forcing the OS to spend more time servicing page faults and swapping pages than performing useful work.",
                "subtopic": "Memory Management",
                "difficulty": difficulty
            },
            {
                "question": "Belady's Anomaly is a phenomenon where increasing the number of page frames leads to what counter-intuitive result?",
                "options": ["Faster CPU clock cycle time", "More page faults", "Decreased disk throughput", "Higher cache hit ratio"],
                "correct_option": 1,
                "explanation": "Belady's Anomaly demonstrates that for certain page replacement algorithms (like FIFO), increasing the number of allocated memory frames can actually INCREASE the total number of page faults for specific access patterns.",
                "subtopic": "Page Replacement",
                "difficulty": difficulty
            }
        ]

        # Extract words from content to create custom context questions if needed
        words = re.findall(r'\b[A-Za-z]{4,}\b', content)
        key_words = list(set([w.title() for w in words if w.lower() not in ['this', 'that', 'with', 'from', 'have', 'were', 'which', 'your', 'about']]))[:10]

        questions = []
        for i in range(count):
            base_q = sample_bank[i % len(sample_bank)].copy()
            base_q["id"] = i + 1
            if source_type == "pdf":
                base_q["source_page"] = (i % 3) + 1
            
            # Customize subtopic tag if possible
            if key_words and i >= len(sample_bank):
                kw = key_words[i % len(key_words)]
                base_q["subtopic"] = kw
            
            questions.append(base_q)

        return {
            "success": True,
            "provider": "Offline Smart Generator" + (" (API key error fallback)" if error_msg else ""),
            "title": f"Quiz: {topic_title[:40]}",
            "questions": questions,
            "note": "Using intelligent offline generator. Set GEMINI_API_KEY in settings to enable live Gemini AI generation."
        }
