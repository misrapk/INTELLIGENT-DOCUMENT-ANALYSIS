import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# --- Session State Setup ---
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "refresh_docs" not in st.session_state:
    st.session_state["refresh_docs"] = False

# --- Home Page ---
def show_homepage():
    st.title("Welcome to Intelligent Document Analysis!")
    st.write("Analyze, summarize, and search your business documents. Sign in or sign up to get started.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In"):
            st.session_state["show_signup"] = False
    with col2:
        if st.button("Sign Up"):
            st.session_state["show_signup"] = True

# --- Signup Form ---
def signup_form():
    st.subheader("Sign Up")
    username = st.text_input("Choose a Username", key="signup_username")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Choose a password", type="password", key="signup_password")
    if st.button("Create Account"):
        resp = requests.post(
            f"{API_URL}/signup",
            json={"username": username, "email": email, "password": password}
        )
        if resp.status_code == 201:
            st.success("Account Created Successfully! Please sign in.")
            st.session_state["show_signup"] = False
        else:
            st.error("Signup failed! Username or email might be taken or password too long.")
    if st.button("Back to Home", key="back_from_signup"):
        st.session_state["show_signup"] = False

# --- Login Form ---
def login_form():
    st.subheader("Sign In")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Log In"):
        resp = requests.post(
            f"{API_URL}/token", 
            data={"username": username, "password": password}
        )
        if resp.status_code == 200:
            token = resp.json()['access_token']
            st.session_state["auth_token"] = token
            st.session_state["username"] = username
                        
            
            st.success("Logged In Successfully")
            st.rerun()
        else:
            st.error("Login failed! Incorrect username or password.")
    if st.button("Back to Home", key="back_from_login"):
        st.session_state["show_signup"] = False
        
#health_scorecard
def health_scorecard():

    
    if not st.session_state.get("auth_token"):
        st.warning("No Token in session state")
        return
    
    token = st.session_state['auth_token']
    # st.write(f"DEBUG - Token exists: {token[:20]}...")
    
     
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with st.spinner("Loading your health dashboard..."):
            
            resp = requests.get(f"{API_URL}/health-dashboard", headers=headers)
            
    except Exception as e:
        st.error(f"❌ Connection error: {e}")
        
        return
    
    
    # with st.spinner("Loading your health dashboard..."):
    #     resp = requests.get(f"{API_URL}/health-dashboard", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        
        if data["has_documents"]:
            st.subheader("📊 Your Health Dashboard")
            st.write(f"Based on {data['document_count']} uploaded report(s)")

            # Display scores in columns with progress bars
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Overall Health",
                    f"{data['overall_health_score']}/100",
                    delta=None,
                )
                st.progress(data['overall_health_score'] / 100)
                
                st.metric(
                    "Physical Health",
                    f"{data['physical_health_score']}/100",
                    delta=None,
                )
                st.progress(data['physical_health_score'] / 100)

            with col2:
                st.metric(
                    "Mental Health",
                    f"{data['mental_health_score']}/100",
                    delta=None,
                )
                st.progress(data['mental_health_score'] / 100)
                
                st.metric(
                    "Internal Health",
                    f"{data['internal_health_score']}/100",
                    delta=None,
                )
                st.progress(data['internal_health_score'] / 100)
                
                
                # Color coding based on score
            if data['overall_health_score'] >= 80:
                st.success("✅ Excellent! Keep maintaining your health.")
            elif data['overall_health_score'] >= 60:
                st.info("ℹ️ Good! Minor improvements recommended.")
            else:
                st.warning("⚠️ Please consult your doctor for personalized advice.")
                
        elif resp.status_code ==401:
            st.error("Unauthorized. Please log in again!")
        else:
            st.info(data["message"])
    else:
        st.error("Could not load health dashboard.")



# --- Dashboard & File Upload ---
def main_dashboard():
    # Header: Profile & Logout Button
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("Logout"):
            st.session_state["auth_token"] = None
            st.session_state["username"] = None
            st.rerun()
    if st.session_state.get("username"):
        with col1:
            st.markdown(
                f'<span style="float:right;">👤 <b>{st.session_state["username"]}</b></span>', unsafe_allow_html=True
            )

    st.title("Upload & Analyze Your Documents")
    st.write("Upload PDFs to extract summaries and insights. Each file remains tied to your account and visible only to you.")
    
    #health scorecard
    health_scorecard()
    
    st.markdown("---")
    st.subheader("Upload a New Report")
    file = st.file_uploader("Choose PDF", type=["pdf"])
    
    
    uploaded = st.session_state.get("uploaded", False)
    if file and not uploaded:
        token = st.session_state["auth_token"]
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": (file.name, file, "application/pdf")}
        with st.spinner("Uploading and analyzing..."):
            resp = requests.post(f"{API_URL}/extract-text", headers=headers, files=files)
        if resp.status_code == 200:
            st.success("Upload & summary complete!")
            st.write("Summary:", resp.json()["extracted_text"])
            st.session_state["uploaded"] = True  # Mark that this file has been uploaded
            st.rerun()
        else:
            st.error("Upload failed! Please re-login or check server.")

    # Reset uploaded flag if no file selected (so next selection triggers upload again)
    if file is None:
        st.session_state["uploaded"] = False

    show_documents()



# --- Display Document History ---
def show_documents():
    token = st.session_state["auth_token"]
    headers = {"Authorization": f"Bearer {token}"}
    st.subheader("Your Uploaded Documents")
    with st.spinner("Loading your documents..."):
        resp = requests.get(f"{API_URL}/my-documents", headers=headers)
    if resp.status_code == 200:
        docs = resp.json()
        if not docs:
            st.info("You have not uploaded any documents yet.")
        for doc in docs:
            with st.expander(doc["filename"]):
                st.write("Uploaded:", doc.get("upload_time", ""))
                st.write("Summary:", doc.get("summary", "No summary yet."))
    else:
        st.error("Could not fetch your documents. Try re-logging in.")

# --- Routing Logic ---
if not st.session_state["auth_token"]:
    if st.session_state["show_signup"]:
        signup_form()
    else:
        show_homepage()
        login_form()
else:
    main_dashboard()



