import streamlit as st
import requests

# Change to wherever your FastAPI backend is running
API_URL = "http://127.0.0.1:8000"

st.title("Document Analysis Dashboard")

# --- SESSION STATE for login token ---
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

# --- LOGIN FORM ---
def login():
    """
    Renders the login form and performs authentication by requesting token from API.
    """
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Make POST request to /token endpoint for JWT authentication token
        resp = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        if resp.status_code == 200:
            st.session_state["auth_token"] = resp.json()["access_token"]
            st.success("Logged in!")
            st.experimental_rerun()  # refresh page to show dashboard
        else:
            st.error("Login failed! Please check your credentials.")

# --- DASHBOARD SCREEN ---
def dashboard():
    """
    Fetches the documents for the logged-in user and renders them in the dashboard.
    """
    token = st.session_state["auth_token"]
    headers = {"Authorization": f"Bearer {token}"}
    st.header("My Uploaded Documents")
    with st.spinner("Loading documents..."):
        resp = requests.get(f"{API_URL}/my-documents", headers=headers)
    if resp.status_code == 200:
        docs = resp.json()
        if not docs:
            st.info("You have not uploaded any documents yet.")
        for doc in docs:
            st.subheader(doc["filename"])
            st.write("Uploaded:", doc["upload_time"])
            st.write("Summary:", doc["summary"])
            # You can later add buttons for view, download, or delete!
    else:
        st.error("Could not fetch documents. Try re-logging in.")

    # --- Logout functionality
    if st.button("Logout"):
        st.session_state["auth_token"] = None
        st.experimental_rerun()

# --- MAIN PAGE LOGIC ---
# Show login form if not logged in, otherwise show dashboard.
if not st.session_state["auth_token"]:
    login()
else:
    dashboard()
