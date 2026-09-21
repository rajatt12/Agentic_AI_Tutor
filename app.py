import streamlit as st
import os
import httpx
from dotenv import load_dotenv

from backend.database import SessionLocal, engine, Base
from backend.services.student_service import StudentService
from backend.services.agent_service import agent_service
from backend.schemas.schemas import UserQuestionSubmission

load_dotenv()

# Initialize DB tables on launch
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

st.set_page_config(
    page_title="AI Tutor - Fast & Adaptive Learning",
    page_icon="⚡",
    layout="wide"
)

# Initialize Session State
if 'student_id' not in st.session_state:
    st.session_state.student_id = "student_001"
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")
if 'groq_model' not in st.session_state:
    st.session_state.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
if 'backend_url' not in st.session_state:
    st.session_state.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

# Check Backend API Health
def check_backend_health():
    try:
        r = httpx.get(f"{st.session_state.backend_url}/health", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

backend_online = check_backend_health()

# Sidebar: Configuration
st.sidebar.title("⚡ AI Tutor")
st.sidebar.caption("Groq Cloud + PostgreSQL + Hybrid RAG")

if backend_online:
    st.sidebar.success("🟢 FastAPI Backend: Connected")
else:
    st.sidebar.info("🔵 Storage Mode: Direct Database")

st.sidebar.markdown("---")

with st.sidebar.expander("⚙️ Settings & Credentials", expanded=not bool(st.session_state.groq_api_key and st.session_state.groq_api_key != "your_groq_api_key_here")):
    user_api_key = st.text_input(
        "Groq API Key",
        value=st.session_state.groq_api_key if st.session_state.groq_api_key != "your_groq_api_key_here" else "",
        type="password",
        placeholder="gsk_...",
        help="Free API keys at https://console.groq.com/keys"
    )
    
    available_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    current_idx = available_models.index(st.session_state.groq_model) if st.session_state.groq_model in available_models else 0
    selected_model = st.selectbox("Groq Model", available_models, index=current_idx)

    student_id_input = st.text_input("Student ID", value=st.session_state.student_id)

    if (user_api_key != st.session_state.groq_api_key or 
        selected_model != st.session_state.groq_model or 
        student_id_input != st.session_state.student_id):
        st.session_state.groq_api_key = user_api_key
        st.session_state.groq_model = selected_model
        st.session_state.student_id = student_id_input
        st.rerun()

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["💬 Chat & Learn", "📝 Practice Quiz", "📊 My Progress", "📚 Study Materials"]
)

if not st.session_state.groq_api_key or st.session_state.groq_api_key == "your_groq_api_key_here":
    st.warning("⚠️ **Groq API Key Required**: Enter your API key in the sidebar or update `.env` to start learning. Get one free at [console.groq.com](https://console.groq.com/keys).")

# ================= PAGE 1: CHAT & LEARN =================
if page == "💬 Chat & Learn":
    st.title("💬 Chat with Your AI Tutor")
    st.markdown("Ask conceptual questions, request explanations, or get practice problems powered by Groq & Hybrid RAG!")
    
    user_query = st.text_input(
        "Your question:",
        placeholder="e.g., Explain Bayes' Theorem with an intuitive formula and example"
    )
    
    if st.button("Ask Tutor", type="primary"):
        if user_query:
            with st.spinner(f"Thinking with {st.session_state.groq_model}..."):
                # Call FastAPI or direct agent service
                if backend_online:
                    try:
                        res = httpx.post(
                            f"{st.session_state.backend_url}/api/v1/chat",
                            json={
                                "student_id": st.session_state.student_id,
                                "query": user_query,
                                "groq_api_key": st.session_state.groq_api_key,
                                "groq_model": st.session_state.groq_model
                            },
                            timeout=45.0
                        ).json()
                    except Exception as e:
                        st.error(f"API Error: {e}")
                        res = None
                else:
                    db = SessionLocal()
                    try:
                        res = agent_service.process_chat(
                            db=db,
                            student_id=st.session_state.student_id,
                            query=user_query,
                            api_key=st.session_state.groq_api_key,
                            model=st.session_state.groq_model
                        )
                    finally:
                        db.close()
                
                if res:
                    if res.get("action") == "explanation":
                        st.markdown("### 📖 Concept Explanation")
                        st.write(res.get("explanation", ""))
                        
                        if res.get("practice_quiz"):
                            st.markdown("### 🎯 Adaptive Practice Questions")
                            for q in res["practice_quiz"]:
                                with st.expander(f"Question {q.get('id', '')}: {q.get('question', '')[:60]}..."):
                                    st.write(q.get("question", ""))
                                    for opt in q.get("options", []):
                                        st.write(opt)
                                    st.info(f"**Correct Answer:** {q.get('correct_answer', '')}")
                                    st.write(f"**Explanation:** {q.get('explanation', '')}")
                        
                        if res.get("plan_executed"):
                            st.success("✅ " + " → ".join(res["plan_executed"]))
                    
                    elif res.get("action") == "chat":
                        st.markdown("### 💡 Response")
                        st.write(res.get("response", ""))
                    
                    elif res.get("action") == "quiz":
                        st.session_state.quiz_data = res.get("quiz", [])
                        st.session_state.quiz_active = True
                        st.session_state.quiz_topic = res.get("topic", "General")
                        st.info(f"Quiz on **{res.get('topic', 'General')}** generated! Go to the '📝 Practice Quiz' tab.")
                    
                    elif res.get("action") == "progress":
                        st.markdown("### 📊 Progress Report")
                        st.write(res.get("recommendation", res.get("message", "")))
        else:
            st.warning("Please enter a question or topic!")

# ================= PAGE 2: PRACTICE QUIZ =================
elif page == "📝 Practice Quiz":
    st.title("📝 Adaptive Practice Quiz")
    st.markdown("Generate quizzes that dynamically match your skill level saved in PostgreSQL.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("Topic", placeholder="e.g., Newton's Laws, Probability, Thermodynamics")
    with col2:
        num_questions = st.selectbox("Number of Questions", [3, 5, 10], index=0)
    
    if st.button("Generate Quiz", type="primary"):
        if topic:
            with st.spinner(f"Generating {num_questions} questions on '{topic}'..."):
                if backend_online:
                    try:
                        res = httpx.post(
                            f"{st.session_state.backend_url}/api/v1/quiz/generate",
                            json={
                                "student_id": st.session_state.student_id,
                                "topic": topic,
                                "num_questions": num_questions,
                                "groq_api_key": st.session_state.groq_api_key,
                                "groq_model": st.session_state.groq_model
                            },
                            timeout=45.0
                        ).json()
                        st.session_state.quiz_data = res.get("questions", [])
                        st.session_state.quiz_topic = res.get("topic", topic)
                        st.session_state.quiz_difficulty = res.get("difficulty", "medium")
                        st.session_state.quiz_active = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate quiz: {e}")
                else:
                    db = SessionLocal()
                    try:
                        res = agent_service.generate_adaptive_quiz(
                            db=db,
                            student_id=st.session_state.student_id,
                            topic=topic,
                            num_questions=num_questions,
                            api_key=st.session_state.groq_api_key,
                            model=st.session_state.groq_model
                        )
                        st.session_state.quiz_data = res.get("questions", [])
                        st.session_state.quiz_topic = res.get("topic", topic)
                        st.session_state.quiz_difficulty = res.get("difficulty", "medium")
                        st.session_state.quiz_active = True
                        st.rerun()
                    finally:
                        db.close()
        else:
            st.warning("Please enter a topic!")

    if st.session_state.quiz_active and getattr(st.session_state, 'quiz_data', None):
        st.markdown(f"## Quiz: **{st.session_state.quiz_topic}** *(Difficulty: {st.session_state.get('quiz_difficulty', 'medium').title()})*")
        
        user_answers = {}
        with st.form("quiz_form"):
            for q in st.session_state.quiz_data:
                st.markdown(f"**Question {q.get('id', '')}:** {q.get('question', '')}")
                options = q.get("options", [])
                user_answers[q["id"]] = st.radio(
                    "Choose one:",
                    options,
                    key=f"q_{q['id']}"
                )
                st.markdown("---")
            
            submitted = st.form_submit_button("Submit Answers & Save to PostgreSQL")
        
        if submitted:
            # Package submission
            submission_payload = []
            for q in st.session_state.quiz_data:
                submission_payload.append({
                    "id": q["id"],
                    "question": q["question"],
                    "options": q["options"],
                    "user_answer": user_answers.get(q["id"], ""),
                    "correct_answer": q["correct_answer"],
                    "explanation": q.get("explanation", "")
                })

            if backend_online:
                try:
                    submit_res = httpx.post(
                        f"{st.session_state.backend_url}/api/v1/quiz/submit",
                        json={
                            "student_id": st.session_state.student_id,
                            "topic": st.session_state.quiz_topic,
                            "difficulty": st.session_state.get("quiz_difficulty", "medium"),
                            "questions": submission_payload
                        },
                        timeout=30.0
                    ).json()
                except Exception as e:
                    st.error(f"Submission error: {e}")
                    submit_res = None
            else:
                db = SessionLocal()
                try:
                    # Convert to schema objects for service
                    obj_payload = [UserQuestionSubmission(**item) for item in submission_payload]
                    record = StudentService.record_quiz_attempt(
                        db=db,
                        student_id=st.session_state.student_id,
                        topic=st.session_state.quiz_topic,
                        difficulty=st.session_state.get("quiz_difficulty", "medium"),
                        questions_data=obj_payload
                    )
                    attempt = record["attempt"]
                    topic_perf = record["topic_perf"]
                    submit_res = {
                        "score": attempt.score,
                        "total_questions": attempt.total_questions,
                        "accuracy": attempt.accuracy,
                        "updated_topic_accuracy": round(topic_perf.accuracy, 1),
                        "updated_topic_strength": topic_perf.strength,
                        "results": [
                            {
                                "id": i + 1,
                                "question": eq["question"],
                                "user_answer": eq["user_answer"],
                                "correct_answer": eq["correct_answer"],
                                "is_correct": eq["is_correct"],
                                "explanation": eq["explanation"]
                            }
                            for i, eq in enumerate(record["evaluated_questions"])
                        ]
                    }
                finally:
                    db.close()

            if submit_res:
                st.success(f"🏆 Score: {submit_res['score']}/{submit_res['total_questions']} ({submit_res['accuracy']:.1f}%) — Saved permanently to PostgreSQL!")
                st.info(f"📊 Topic Mastery for **{st.session_state.quiz_topic}**: {submit_res['updated_topic_accuracy']}% ({submit_res['updated_topic_strength'].upper()})")

                st.markdown("### 📚 Review & Explanations")
                for r in submit_res.get("results", []):
                    is_correct = r["is_correct"]
                    with st.expander(f"Question {r['id']} - {'✅ Correct' if is_correct else '❌ Incorrect'}"):
                        if is_correct:
                            st.success(f"Your answer: {r['user_answer']}")
                        else:
                            st.error(f"Your answer: {r['user_answer']} | Correct answer: {r['correct_answer']}")
                        st.write(f"**Explanation:** {r['explanation']}")

                st.session_state.quiz_active = False

# ================= PAGE 3: MY PROGRESS =================
elif page == "📊 My Progress":
    st.title("📊 Your Learning Progress (PostgreSQL Analytics)")
    
    if backend_online:
        try:
            report = httpx.get(
                f"{st.session_state.backend_url}/api/v1/progress/{st.session_state.student_id}",
                timeout=10.0
            ).json()
        except Exception:
            report = None
    else:
        db = SessionLocal()
        try:
            report = StudentService.get_progress_report(db, st.session_state.student_id)
        finally:
            db.close()

    if report and report.get("progress"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Topics Practiced", report.get("topics_practiced", len(report["progress"])))
        with col2:
            st.metric("Total Quizzes Taken", report.get("total_quizzes", 0))
        with col3:
            weak_count = len(report.get("weak_topics", []))
            st.metric("Topics Needing Focus", weak_count)
        
        st.markdown("---")
        st.markdown("### Topic Mastery Breakdown")
        
        for topic_name, data in report["progress"].items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{topic_name}** ({data.get('attempts', 1)} attempts)")
            with col2:
                st.write(f"{data['accuracy']:.1f}%")
            with col3:
                if data['strength'] == "strong":
                    st.success("Strong")
                elif data['strength'] == "medium":
                    st.warning("Medium")
                else:
                    st.error("Weak")
        
        if report.get("recommendations"):
            st.markdown("### 💡 Tutor Recommendations")
            for rec in report["recommendations"]:
                st.info(rec)
    else:
        st.info("No quiz records found in PostgreSQL for this student ID. Complete a practice quiz to start tracking!")

# ================= PAGE 4: STUDY MATERIALS INGESTION =================
elif page == "📚 Study Materials":
    st.title("📚 Ingest Study Materials (Hybrid RAG)")
    st.markdown("Add notes, formulas, or textbook summaries to the **ChromaDB + BM25** knowledge base.")
    
    doc_title = st.text_input("Document / Subject Title:", placeholder="e.g., Physics Mechanics Cheat Sheet")
    doc_content = st.text_area("Paste Content / Notes:", height=200, placeholder="Paste equations, definitions, or textbook paragraphs here...")
    
    if st.button("Index into Knowledge Base", type="primary"):
        if doc_title and doc_content:
            with st.spinner("Indexing into ChromaDB (HNSW) and BM25..."):
                if backend_online:
                    try:
                        res = httpx.post(
                            f"{st.session_state.backend_url}/api/v1/documents/ingest",
                            json={"title": doc_title, "content": doc_content},
                            timeout=30.0
                        ).json()
                        st.success(f"✅ {res.get('message', 'Document indexed!')}")
                    except Exception as e:
                        st.error(f"Ingestion error: {e}")
                else:
                    chunks = agent_service.ingest_document(doc_title, doc_content)
                    st.success(f"✅ Successfully indexed '{doc_title}' ({chunks} chunks) into ChromaDB & BM25!")
        else:
            st.warning("Please provide both a title and content.")

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Student ID:** `{st.session_state.student_id}`")
st.sidebar.markdown(f"**Groq Model:** `{st.session_state.groq_model}`")
st.sidebar.markdown(f"**Database:** `PostgreSQL (Docker)`")
