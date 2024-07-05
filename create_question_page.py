import streamlit as st
import csv
import os

UPLOAD_DIR = "uploaded_files"

def save_questions_to_csv(filename, questions):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    with open(os.path.join(UPLOAD_DIR, filename), mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Choice1", "Choice2", "Choice3", "Choice4", "Answer"])
        writer.writerows(questions)

def show_create_question_page():
    st.title("Create Quiz Questions")

    num_questions = st.number_input("Number of Questions", min_value=1, step=1, value=1)
    questions = []

    for i in range(num_questions):
        st.subheader(f"Question {i+1}")
        question = st.text_input(f"Enter Question {i+1}")
        choice1 = st.text_input(f"Choice 1 for Question {i+1}")
        choice2 = st.text_input(f"Choice 2 for Question {i+1}")
        choice3 = st.text_input(f"Choice 3 for Question {i+1}")
        choice4 = st.text_input(f"Choice 4 for Question {i+1}")
        answer = st.selectbox(f"Select the correct answer for Question {i+1}", [1, 2, 3, 4])
        questions.append([question, choice1, choice2, choice3, choice4, answer])

    filename = st.text_input("Enter filename to save the questions (e.g., quiz.csv)")

    if st.button("Save Questions"):
        save_questions_to_csv(filename, questions)
        st.success(f"Questions saved to {filename}")

    if st.button("Back to Question Selection"):
        st.session_state.show_create_question_page = False
        st.session_state.show_homepage = True
        st.experimental_rerun()

if __name__ == "__main__":
    show_create_question_page()
