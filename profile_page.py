import streamlit as st
import mysql.connector

def create_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12718204",
        password="E2xX9CKCYj",
        database="sql12718204"
    )

def get_user_profile(user_id):
    connection = None  # Initialize the connection variable
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user_id,))
        profile = cursor.fetchone()
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        profile = None
    finally:
        if connection:
            connection.close()
    return profile

def show_profile_page():
    st.title("Profile Page")

    if 'user' in st.session_state:
        user_id = st.session_state.user['id']
        profile = get_user_profile(user_id)  # Pastikan fungsi ini ada dan berfungsi

        if profile:
            st.write(f"**Name:** {profile['name']}")
            st.write(f"**NIM:** {profile['nim']}")
            st.write(f"**Prodi:** {profile['prodi']}")
            st.write(f"**Jurusan:** {profile['jurusan']}")

    if st.button("Back to Home"):
        st.session_state.show_profile_page = False
        st.session_state.show_homepage = True
        st.experimental_rerun()

