import streamlit as st
import mysql.connector

# Fungsi login
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.is_logged_in = True
            st.session_state.user = user
            st.session_state.user_id = user['id']
            st.session_state.show_homepage = True
            st.session_state.show_create_question_page = False
            st.session_state.show_login_page = False
            st.success("Login successful")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Fungsi autentikasi pengguna
def authenticate_user(username, password):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            return user
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
            return None
        finally:
            connection.close()

# Fungsi logout
def logout():
    st.session_state.is_logged_in = False
    st.session_state.show_homepage = False
    st.session_state.show_create_question_page = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.experimental_rerun()

# Koneksi DB
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="sql12.freesqldatabase.com",
            user="sql12718204",
            password="E2xX9CKCYj",
            database="sql12718204"
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Main
if __name__ == '__main__':
    if 'is_logged_in' not in st.session_state:
        st.session_state.is_logged_in = False
        st.session_state.user = None
        st.session_state.user_id = None

    if not st.session_state.is_logged_in:
        login()
    else:
        st.write(f"Welcome {st.session_state.user['username']}")
        if st.button("Logout"):
            logout()
