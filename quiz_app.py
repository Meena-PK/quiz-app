import streamlit as st
import pandas as pd
import time
import os

# Load questions from CSV file
@st.cache_data
def load_questions(file_path="questions.csv"):
    df = pd.read_csv(file_path)
    quiz = []
    for _, row in df.iterrows():
        quiz.append({
            "question": row["question"],
            "options": [row["option1"], row["option2"], row["option3"], row["option4"]],
            "correct_answer": row["correct_answer"]
        })
    return quiz

# Initialize session state
def initialize_session_state(quiz):
    if 'quiz' not in st.session_state:
        st.session_state.quiz = quiz
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'player_score' not in st.session_state:
        st.session_state.player_score = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = [None] * len(quiz)
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False
    if 'name' not in st.session_state:
        st.session_state.name = ""
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

# Check answer correctness
def is_correct(user_option, correct_option):
    return user_option.strip().lower() == correct_option.strip().lower()

# Display question
def display_question(idx):
    question = st.session_state.quiz[idx]
    st.markdown(f"### Q{idx + 1}: {question['question']}")
    selected = st.radio(
        "Choose your answer:",
        question['options'],
        key=f"question_{idx}",
        index=st.session_state.user_answers[idx] if st.session_state.user_answers[idx] is not None else 0
    )
    return question['options'].index(selected) if selected is not None else None

# Save results to a file
def save_results(name, score, total, answers, quiz):
    os.makedirs("results", exist_ok=True)
    filename = f"results/{name}_{score}of{total}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Name: {name}\nScore: {score}/{total}\n\n")
        for i, q in enumerate(quiz):
            user_index = answers[i]
            user_ans = q["options"][user_index] if user_index is not None else "Not Answered"
            correct = q["correct_answer"]
            f.write(f"Q{i+1}: {q['question']}\n")
            f.write(f"  Your Answer: {user_ans} {'✅' if is_correct(user_ans, correct) else '❌'}\n")
            f.write(f"  Correct Answer: {correct}\n\n")
    return filename

# Main app
def quiz_app():
    st.markdown("<h1 style='color:#4CAF50;'>🧠 Quiz App</h1>", unsafe_allow_html=True)
    quiz = load_questions()
    initialize_session_state(quiz)

    if not st.session_state.name:
        name = st.text_input("Enter your name to begin:")
        if name:
            st.session_state.name = name
            st.session_state.start_time = time.time()
        else:
            st.stop()

    if not st.session_state.quiz_finished:
        idx = st.session_state.current_question
        total = len(st.session_state.quiz)

        elapsed = int(time.time() - st.session_state.start_time)
        time_left = 30 - elapsed

        if time_left <= 0:
            st.warning("⏰ Time's up! Moving to next question...")
            if st.session_state.user_answers[idx] is None:
                st.session_state.user_answers[idx] = 0
            if idx < total - 1:
                st.session_state.current_question += 1
                st.session_state.start_time = time.time()
                st.rerun()
            else:
                st.session_state.quiz_finished = True
                st.rerun()

        st.markdown(f"⏱️ Time left: **{time_left}** seconds")
        st.progress((idx + 1) / total)
        selected_option_index = display_question(idx)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back") and idx > 0:
                st.session_state.current_question -= 1
                st.session_state.start_time = time.time()
        with col2:
            if st.button("➡️ Save and Next"):
                if selected_option_index is not None:
                    st.session_state.user_answers[idx] = selected_option_index
                    if idx < total - 1:
                        st.session_state.current_question += 1
                        st.session_state.start_time = time.time()
                    else:
                        if None not in st.session_state.user_answers:
                            score = 0
                            for i, q in enumerate(st.session_state.quiz):
                                user_ans = q["options"][st.session_state.user_answers[i]]
                                if is_correct(user_ans, q["correct_answer"]):
                                    score += 1
                            st.session_state.player_score = score
                            st.session_state.quiz_finished = True
                            st.rerun()
                        else:
                            st.warning("⚠️ Please answer all questions before finishing.")

    if st.session_state.quiz_finished:
        st.success("✅ Quiz Completed!")
        name = st.session_state.name
        score = st.session_state.player_score
        total = len(st.session_state.quiz)
        st.markdown(f"### 🏆 {name}, Your Score: **{score}/{total}**")

        for i, q in enumerate(st.session_state.quiz):
            user_index = st.session_state.user_answers[i]
            user_ans = q["options"][user_index] if user_index is not None else "Not Answered"
            correct = q["correct_answer"]
            st.markdown(f"**Q{i+1}: {q['question']}**")
            st.markdown(f"- Your answer: `{user_ans}` {'✅' if is_correct(user_ans, correct) else '❌'}")
            st.markdown(f"- Correct answer: `{correct}`")

        file_path = save_results(name, score, total, st.session_state.user_answers, st.session_state.quiz)
        st.info(f"📁 Your result has been saved to: `{file_path}`")

        if st.button("🔄 Restart Quiz"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

quiz_app()
