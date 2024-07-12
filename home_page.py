import streamlit as st
import os
import csv
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2 as cv
import cvzone as cvz
from cvzone.HandTrackingModule import HandDetector
import datetime
import time

UPLOAD_DIR = "uploaded_files"
VIDEO_OUTPUT_DIR = "video_outputs"
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)  # Buat direktori jika belum ada

# Fungsi logout
def logout():
    st.session_state.is_logged_in = False
    st.session_state.show_homepage = False
    st.session_state.user = None
    st.experimental_rerun()


# Form Pemilihan Soal
def select_csv_file():
    uploaded_files = os.listdir(UPLOAD_DIR)
    selected_file = st.selectbox("Select a CSV file", uploaded_files)
    return selected_file


# Kelas MCQ untuk pertanyaan
class MCQ:
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None

    def update(self, cursor, bboxs, frame):
        for x, box in enumerate(bboxs):
            x1, y1, x2, y2 = box
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), cv.FILLED)


# Kelas VideoProcessor untuk memproses video dan pertanyaan
class VideoProcessor(VideoProcessorBase):
    def __init__(self, mcq_list):
        self.cap = cv.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.detector = HandDetector(detectionCon=0.8)
        self.mcqList = mcq_list
        self.quesNumber = 0
        self.qTotal = len(mcq_list)
        self.score_stored = False  # Add a flag to ensure score is stored once

        # Inisialisasi VideoWriter untuk merekam video
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        video_filename = 'quiz_output.avi'
        self.video_path = os.path.join(VIDEO_OUTPUT_DIR, video_filename)
        self.out = cv.VideoWriter(self.video_path, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

        if "user" in st.session_state and st.session_state.user is not None:
            self.user_id = st.session_state.user['id']
        else:
            st.error("User is not logged in.")
            self.user_id = None

    def transform(self, frame):
        ret, frame = self.cap.read()
        frame = cv.flip(frame, 1)
        hands, frame = self.detector.findHands(frame, flipType=False)
        dt = str(datetime.datetime.now())
        frame = cv.putText(frame, dt, (750, 50), cv.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 4)

        if self.quesNumber < self.qTotal:
            mcq = self.mcqList[self.quesNumber]
            frame, _ = cvz.putTextRect(frame, 'Total Questions: {}'.format(self.qTotal), [50, 50], 2, 2,
                                       colorT=(0, 0, 0), offset=10, border=4)
            frame, box = cvz.putTextRect(frame, mcq.question, [100, 100], 1, 1, cv.FONT_HERSHEY_SCRIPT_COMPLEX,
                                         offset=18, border=4)
            frame, box1 = cvz.putTextRect(frame, mcq.choice1, [100, 250], 2, 1, cv.FONT_HERSHEY_SIMPLEX, offset=15,
                                          border=4)
            frame, box2 = cvz.putTextRect(frame, mcq.choice2, [400, 250], 2, 1, cv.FONT_HERSHEY_SIMPLEX, offset=15,
                                          border=4)
            frame, box3 = cvz.putTextRect(frame, mcq.choice3, [100, 400], 2, 1, cv.FONT_HERSHEY_SIMPLEX, offset=15,
                                          border=4)
            frame, box4 = cvz.putTextRect(frame, mcq.choice4, [400, 400], 2, 1, cv.FONT_HERSHEY_SIMPLEX, offset=15,
                                          border=4)

            if hands:
                lmList = hands[0]['lmList']
                cursor = lmList[8]
                length, info, img = self.detector.findDistance(lmList[4][0:2], lmList[8][0:2], frame)

                if 20 <= length <= 40:
                    mcq.update(cursor, [box1, box2, box3, box4], frame)
                    if mcq.userAns is not None:
                        time.sleep(0.3)
                        self.quesNumber += 1
        else:
            # All questions answered, calculate score and store it
            if not self.score_stored:
                score = sum(mcq.answer == mcq.userAns for mcq in self.mcqList)
                score = round((score / self.qTotal) * 100, 2)
                user_id = st.session_state.get('user_id')
                if user_id is not None:
                    self.score_stored = True  # Set flag to prevent multiple inserts
                    st.session_state.show_profile_page = True
                    st.session_state.quiz_completed = True  # Set flag to indicate quiz completion
                    st.experimental_rerun()
                else:
                    st.error("User ID not found in session state")
            frame, _ = cvz.putTextRect(frame, 'Total No of Questions solved : {}'.format(self.qTotal), [200, 150], 1, 1,
                                       offset=15, border=3, colorB=(130, 200, 255), colorT=(255, 25, 25))
            frame, _ = cvz.putTextRect(frame, "Your Quiz Completed ", [200, 200], 1, 1, offset=15, border=3,
                                       colorB=(130, 200, 255), colorT=(255, 25, 25))
            frame, _ = cvz.putTextRect(frame, f'Your Score: {score}', [200, 250], 1, 1, offset=15, border=3,
                                       colorB=(130, 200, 255), colorT=(255, 25, 25))

        Probar = 150 + (900 // self.qTotal) * self.quesNumber
        cv.rectangle(frame, (150, 600), (Probar, 620), (17, 171, 50), cv.FILLED)
        cv.rectangle(frame, (150, 600), (1050, 620), (255, 255, 255), 5, cv.FILLED)
        frame, _ = cvz.putTextRect(frame, f'{round((self.quesNumber / self.qTotal) * 100)}%', [1150, 610], 2, 2,
                                   offset=16)

        # Menyimpan frame ke file video
        self.out.write(frame)

        return frame

    def __del__(self):
        # Melepaskan resources ketika objek dihancurkan
        self.cap.release()
        self.out.release()
        cv.destroyAllWindows()


def show_homepage():
    st.title("Quiz App Home Page")

    if 'show_profile_page' in st.session_state and st.session_state.show_profile_page:
        import profile_page
        profile_page.show_profile_page()
        return

    if 'show_create_question_page' in st.session_state and st.session_state.show_create_question_page:
        import create_question_page
        create_question_page.show_create_question_page()
        return

    if 'show_upload_page' in st.session_state and st.session_state.show_upload_page:
        show_upload_and_start_quiz_page()
        return

    if 'is_logged_in' in st.session_state and st.session_state.is_logged_in:
        st.write(f"Hello, {st.session_state.user['username']}!")

        if st.session_state.user and st.session_state.user['role'] == 'dosen':
            if st.session_state.show_create_question_page:
                import create_question_page
                create_question_page.show_create_question_page()
                return
            else:
                if st.button("Create Quiz Question"):
                    st.session_state.show_create_question_page = True
                    st.experimental_rerun()

        if st.button("Upload and Start Quiz"):
            st.session_state.show_upload_page = True
            st.session_state.show_homepage = False
            st.experimental_rerun()

        if st.button("View Profile"):
            st.session_state.show_profile_page = True
            st.session_state.show_homepage = False
            st.experimental_rerun()

        if st.button("Logout"):
            logout()

    if 'quiz_completed' in st.session_state and st.session_state.quiz_completed:
        st.success("Quiz completed! You can download the video below.")
        video_path = os.path.join(VIDEO_OUTPUT_DIR, 'quiz_output.avi')
        with open(video_path, 'rb') as video_file:
            st.download_button(label="Download Quiz Video", data=video_file, file_name="quiz_output.avi")


def show_upload_and_start_quiz_page():
    st.title("Upload and Start Quiz")
    if "user" not in st.session_state or st.session_state.user is None:
        st.error("You must be logged in to start the quiz.")
        return

    selected_file = select_csv_file()
    if selected_file:
        with open(os.path.join(UPLOAD_DIR, selected_file), newline='\n') as file:
            reader = csv.reader(file)
            datafile = list(reader)[1:]
            mcq_list = [MCQ(q) for q in datafile]
            webrtc_streamer(key="example", video_processor_factory=lambda: VideoProcessor(mcq_list))

    if st.button("Back to Home"):
        st.session_state.show_upload_page = False
        st.session_state.show_homepage = True
        st.experimental_rerun()


if __name__ == "__main__":
    show_homepage()
