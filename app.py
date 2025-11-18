import streamlit as st
from agents.planner_agent import PlannerAgent
from agents.retriever_agent import RetrieverAgent
from agents.quiz_agent import QuizGeneratorAgent
from utils.student_profiles import StudentProfileManager
import os
from dotenv import load_dotenv


load_dotenv()


st.set_page_config(
    page_title="AI Tutor - Adaptive Learning",
    page_icon="🎓",
    layout="wide"
)


if 'student_id' not in st.session_state:
    st.session_state.student_id = "student_001"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False


@st.cache_resource
def initialize_agents():
    retriever = RetrieverAgent()
    quiz_generator = QuizGeneratorAgent()
    profile_manager = StudentProfileManager()
    planner = PlannerAgent(retriever, quiz_generator, profile_manager)
    return planner, profile_manager

planner_agent, profile_manager = initialize_agents()


st.sidebar.title("🎓 AI Tutor")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["💬 Chat & Learn", "📝 Practice Quiz", "📊 My Progress"]
)


if page == "💬 Chat & Learn":
    st.title("Chat with Your AI Tutor")
    st.markdown("Ask questions, request explanations, or get practice problems!")
    
    
    user_query = st.text_input(
        "Your question:",
        placeholder="e.g., I'm struggling with probability in math"
    )
    
    if st.button("Ask"):
        if user_query:
            with st.spinner("Thinking..."):
                result = planner_agent.decide_action(
                    st.session_state.student_id,
                    user_query
                )
                
                
                if result["action"] == "explanation":
                    st.markdown("### 📖 Explanation")
                    st.write(result["explanation"])
                    
                    st.markdown("### 🎯 Practice Questions")
                    for q in result["practice_quiz"]:
                        with st.expander(f"Question {q['id']}"):
                            st.write(q["question"])
                            for opt in q["options"]:
                                st.write(opt)
                            st.info(f"Correct Answer: {q['correct_answer']}")
                            st.write(f"**Explanation:** {q['explanation']}")
                    
                    st.success("✅ " + " → ".join(result["plan_executed"]))
                
                elif result["action"] == "chat":
                    st.markdown("### 💡 Response")
                    st.write(result["response"])
        else:
            st.warning("Please enter a question!")

elif page == "📝 Practice Quiz":
    st.title("Practice Quiz")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("Topic", placeholder="e.g., Probability")
    with col2:
        num_questions = st.selectbox("Number of Questions", [3, 5, 10])
    
    if st.button("Generate Quiz"):
        if topic:
            with st.spinner("Generating quiz..."):
                result = planner_agent._handle_quiz_request(
                    f"quiz on {topic}",
                    st.session_state.student_id
                )
                
                st.session_state.quiz_data = result["quiz"]
                st.session_state.quiz_active = True
                st.session_state.quiz_topic = topic
                st.rerun()
    
    
    if st.session_state.quiz_active:
        st.markdown(f"## Quiz: {st.session_state.quiz_topic}")
        
        user_answers = {}
        
        for q in st.session_state.quiz_data:
            st.markdown(f"**Question {q['id']}:** {q['question']}")
            
            
            option_letters = [opt.split(")")[0] for opt in q["options"]]
            
            user_answers[q["id"]] = st.radio(
                "Select your answer:",
                option_letters,
                key=f"q_{q['id']}"
            )
            st.markdown("---")
        
        if st.button("Submit Quiz"):
            
            correct = 0
            total = len(st.session_state.quiz_data)
            
            for q in st.session_state.quiz_data:
                if user_answers[q["id"]] == q["correct_answer"]:
                    correct += 1
            
            accuracy = (correct / total) * 100
            
            
            profile_manager.update_topic_performance(
                st.session_state.student_id,
                st.session_state.quiz_topic,
                accuracy
            )
            
            
            st.success(f"Score: {correct}/{total} ({accuracy:.1f}%)")
            
            
            st.markdown("### 📚 Review")
            for q in st.session_state.quiz_data:
                with st.expander(f"Question {q['id']}"):
                    is_correct = user_answers[q["id"]] == q["correct_answer"]
                    
                    if is_correct:
                        st.success("✅ Correct!")
                    else:
                        st.error(f"Incorrect. Correct answer: {q['correct_answer']}")
                    
                    st.write(f"**Explanation:** {q['explanation']}")
            
            st.session_state.quiz_active = False

elif page == "My Progress":
    st.title("Your Learning Progress")
    
    report = profile_manager.get_progress_report(st.session_state.student_id)
    
    if report:
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Topics Practiced", len(report["progress"]))
        with col2:
            st.metric("Total Quizzes", report["total_quizzes"])
        with col3:
            weak_count = len(report["weak_topics"])
            st.metric("Topics Needing Focus", weak_count)
        
        st.markdown("---")
        
        
        st.markdown("### Topic Performance")
        
        for topic, data in report["progress"].items():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{topic}**")
            with col2:
                st.write(f"{data['accuracy']:.1f}%")
            with col3:
                if data['strength'] == "strong":
                    st.success("Strong")
                elif data['strength'] == "medium":
                    st.warning("Medium")
                else:
                    st.error("Weak")
        
        
        if report["weak_topics"]:
            st.markdown("### 💡 Recommendations")
            st.info(f"Focus on: {', '.join(report['weak_topics'])}")
    else:
        st.info("No progress data yet. Start practicing to see your progress!")


st.sidebar.markdown("---")
st.sidebar.markdown("**Student ID:** " + st.session_state.student_id)
