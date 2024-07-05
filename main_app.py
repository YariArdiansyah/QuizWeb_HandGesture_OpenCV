import streamlit as st
from kreden import login, logout

def show_welcome_page():
    st.title("Welcome to the Quiz App!")

    if st.button("Go to Login Page"):
        st.session_state.show_login_page = True
        st.experimental_rerun()

if __name__ == "__main__":
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "show_profile_page" not in st.session_state:
        st.session_state.show_profile_page = False
    if "show_homepage" not in st.session_state:
        st.session_state.show_homepage = False
    if "show_create_question_page" not in st.session_state:
        st.session_state.show_create_question_page = False
    if "show_login_page" not in st.session_state:
        st.session_state.show_login_page = False
    if "show_upload_page" not in st.session_state:
        st.session_state.show_upload_page = False

    if st.session_state.show_login_page:
        login()
    elif st.session_state.show_homepage:
        import home_page
        home_page.show_homepage()
    elif st.session_state.show_profile_page:
        import profile_page
        profile_page.show_profile_page()
    elif st.session_state.show_upload_page:
        import home_page
        home_page.show_upload_and_start_quiz_page()

    else:
        show_welcome_page()
