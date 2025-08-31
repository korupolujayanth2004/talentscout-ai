import streamlit as st
import requests
import re
import time
import os
import html

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Page configuration with dark theme
st.set_page_config(
    page_title="TalentScout AI Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .main > div {
        background-color: #0e1117;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
        border: 1px solid #404040;
    }
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: #ffffff;
        border: 1px solid #404040;
    }
    .stSelectbox > div > div > select {
        background-color: #262730;
        color: #ffffff;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #1e3a8a;
        margin-left: 20%;
        color: #ffffff;
    }
    .assistant-message {
        background-color: #374151;
        margin-right: 20%;
        color: #ffffff;
    }
    .streaming-text {
        color: #ffffff !important;
        background-color: #374151;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-right: 20%;
        font-style: italic;
    }
    .stButton > button {
        background-color: #1f2937;
        color: #ffffff;
        border: 1px solid #404040;
    }
    .stButton > button:hover {
        background-color: #374151;
        border-color: #10b981;
    }
    .stForm {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)

# Inject JS to disable copy/paste, tab switching alerts, and enforce fullscreen
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('copy', function(e){e.preventDefault();return false;});
    document.body.addEventListener('paste', function(e){e.preventDefault();return false;});
    document.body.addEventListener('cut', function(e){e.preventDefault();return false;});
});

window.onblur = function() {
    alert("Tab switching detected! Please remain on this tab during your interview.");
};

window.onload = function() {
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
    }
};

document.addEventListener('fullscreenchange', function() {
    if (!document.fullscreenElement) {
        alert("Please do not exit fullscreen mode during the interview.");
    }
});
</script>
""", unsafe_allow_html=True)

# Initialize session state variables with default values
if "step" not in st.session_state:
    st.session_state.step = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# Constants
MIN_QUESTIONS = 5
MAX_QUESTIONS = 10

def reset():
    if "session_id" in st.session_state:
        try:
            requests.post(f"{BACKEND_URL}/clear-session", json={"session_id": st.session_state.session_id})
        except Exception:
            pass
    keys_to_clear = ["step", "greet", "candidate_data", "session_id", 
                     "chat_history", "parsed_data", "current_question",
                     "question_count", "interview_summary"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def stream_text(text, placeholder):
    words = text.split()
    displayed_text = ""
    for word in words:
        displayed_text += word + " "
        placeholder.markdown(f"""
        <div style="
            color: #ffffff;
            background-color: #374151;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-right: 20%;
            font-style: italic;
        ">
            <strong>🤖 Interviewer:</strong> {displayed_text}▊
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.05)
    placeholder.markdown(f"""
    <div style="
        color: #ffffff;
        background-color: #374151;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-right: 20%;
    ">
        <strong>🤖 Interviewer:</strong> {text}
    </div>
    """, unsafe_allow_html=True)

st.title("🎯 TalentScout AI Hiring Assistant")
st.markdown("---")

# Step 0: Welcome
if st.session_state.step == 0:
    st.markdown("### Welcome to our AI-powered hiring process!")
    st.write("Click below to begin your interactive interview experience.")
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        resp = requests.get(f"{BACKEND_URL}/greet")
        st.session_state.greet = resp.json()["message"]
        st.session_state.step = 1
        st.rerun()
    if "greet" in st.session_state:
        st.info(st.session_state.greet)

# Step 1: Resume or Manual Info
elif st.session_state.step == 1:
    st.header("📄 Upload Resume or Fill Information")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Option 1: Upload Resume")
        uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
        if uploaded_file is not None:
            try:
                files = {"file": ("resume.pdf", uploaded_file.getvalue(), "application/pdf")}
                resp = requests.post(f"{BACKEND_URL}/parse-resume", files=files)
                if resp.status_code == 200:
                    parsed = resp.json()["parsed_data"]
                    st.success("✅ Resume parsed successfully!")
                    st.session_state.parsed_data = parsed
                    with st.expander("📋 Extracted Information"):
                        st.write(f"**Name:** {parsed.get('name', 'Not found')}")
                        st.write(f"**Email:** {parsed.get('email', 'Not found')}")
                        st.write(f"**Phone:** {parsed.get('phone', 'Not found')}")
                        st.write(f"**Experience:** {parsed.get('experience', 'Not found')}")
                        if parsed.get('skills'):
                            st.write(f"**Skills:** {', '.join(parsed.get('skills', []))}")
                else:
                    st.error("❌ Failed to parse resume. Please fill manually.")
            except Exception as e:
                st.error(f"Error uploading resume: {e}")
    with col2:
        st.subheader("Option 2: Fill Manually")
        parsed = st.session_state.get("parsed_data", {})
        with st.form("candidate_form"):
            st.markdown("**📋 Basic Information**")
            name = st.text_input("Full Name *", value=parsed.get("name", ""))
            email = st.text_input("Email *", value=parsed.get("email", ""))
            phone = st.text_input("Phone Number *", value=parsed.get("phone", ""))
            st.markdown("**💼 Professional Information**")
            position = st.text_input("Desired Position(s) *")
            location = st.text_input("Current Location *")
            exp_value = 0
            if parsed.get("experience"):
                exp_match = re.search(r'(\d+)', str(parsed.get("experience", "")))
                if exp_match:
                    try:
                        exp_value = int(exp_match.group(1))
                    except (ValueError, AttributeError):
                        exp_value = 0
            exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=exp_value)
            skills_text = ", ".join(parsed.get("skills", [])) if parsed.get("skills") else ""
            tech_stack = st.text_area("Tech Stack (comma-separated) *",
                                    value=skills_text, help="Enter your technical skills separated by commas")
            st.markdown("**🎓 Additional Information**")
            education = st.text_input("Highest Education", placeholder="e.g., B.Tech Computer Science")
            current_role = st.text_input("Current Role/Status",
                                   value="Student" if parsed.get("experience") and "student" in parsed.get("experience", "").lower() else "",
                                   placeholder="e.g., Software Engineer, Student, etc.")
            submitted = st.form_submit_button("Submit Information", type="primary")
            if submitted:
                required_fields = {
                    "Full Name": name,
                    "Email": email,
                    "Phone Number": phone,
                    "Desired Position": position,
                    "Current Location": location,
                    "Tech Stack": tech_stack
                }
                missing_fields = [field for field, value in required_fields.items() if not value.strip()]
                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                else:
                    data = {
                        "full_name": name,
                        "email": email,
                        "phone": phone,
                        "years_experience": exp,
                        "desired_position": position,
                        "current_location": location,
                        "tech_stack": [t.strip() for t in tech_stack.split(",") if t.strip()],
                        "education": education,
                        "current_role": current_role
                    }
                    resp = requests.post(f"{BACKEND_URL}/candidate-info", json=data)
                    if resp.status_code == 200:
                        st.success("✅ Information saved! Starting interactive interview...")
                        st.session_state.candidate_data = data
                        st.session_state.session_id = resp.json().get("session_id")
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("❌ Failed to save information. Please try again.")

# Step 2: Interactive Chat Interview
elif st.session_state.step == 2:
    st.header("💬 Interactive Interview")
    progress_col1, progress_col2 = st.columns([3, 1])
    with progress_col1:
        progress = min(st.session_state.question_count / MAX_QUESTIONS, 1.0)
        st.progress(progress)
    with progress_col2:
        st.write(f"Question {st.session_state.question_count}/{MAX_QUESTIONS}")
    
    if not st.session_state.chat_history:
        initial_message = "Hello! I'm excited to learn more about you. Let's start with your background and experience. Can you tell me about your current role and what you enjoy most about it?"
        st.session_state.chat_history.append({"role": "assistant", "content": initial_message})
        st.session_state.question_count = 1

    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Interviewer:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_area("Your Response:", key=f"user_message_{len(st.session_state.chat_history)}", height=100)
    with col2:
        st.write("")
        send_button = st.button("Send", type="primary", use_container_width=True)
        
        # Fixed end button logic - no negative values
        if st.session_state.question_count >= MIN_QUESTIONS:
            end_button = st.button("End Interview", type="secondary", use_container_width=True)
        else:
            remaining_questions = max(0, MIN_QUESTIONS - st.session_state.question_count)
            st.write(f"Minimum {remaining_questions} more questions")
            end_button = False

    if send_button and user_input.strip():
        # Always add user message to history
        st.session_state.chat_history.append({"role": "user", "content": html.escape(user_input)})

        
        if st.session_state.question_count >= MAX_QUESTIONS:
            st.session_state.final_message = "Thank you for completing the full interview! I have all the information I need."
            st.session_state.chat_history.append({"role": "assistant", "content": st.session_state.final_message})
            st.session_state.step = 3
            st.rerun()
            
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.chat_history[:-1]
        ]
        
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="streaming-text">🤖 Interviewer is typing...</div>', unsafe_allow_html=True)
        
        try:
            enhanced_prompt = f"""
            You are conducting a professional technical interview. This is question #{st.session_state.question_count + 1}.
            Candidate Info:
            - Name: {st.session_state.candidate_data.get('full_name', 'N/A')}
            - Experience: {st.session_state.candidate_data.get('years_experience', 0)} years
            - Position: {st.session_state.candidate_data.get('desired_position', 'N/A')}
            - Tech Stack: {', '.join(st.session_state.candidate_data.get('tech_stack', []))}
            Guidelines:
            - Ask one focused question at a time
            - Make questions progressively more technical
            - Ask follow-up questions based on their responses
            - Keep questions relevant to their stated tech stack
            - Be professional but conversational
            User's response: {user_input}
            """
            
            resp = requests.post(f"{BACKEND_URL}/chat", json={
                "session_id": st.session_state.session_id,
                "user_message": enhanced_prompt,
                "conversation_history": conversation_history
            })
            
            if resp.status_code == 200:
                data = resp.json()
                reply = data["reply"]
                
                typing_placeholder.empty()
                response_placeholder = st.empty()
                stream_text(reply, response_placeholder)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.session_state.question_count += 1
                time.sleep(1)
                st.rerun()
            else:
                typing_placeholder.empty()
                st.error("❌ Failed to get response. Please try again.")
        except Exception as e:
            typing_placeholder.empty()
            st.error(f"Error: {e}")

    # Handle end interview
    if st.session_state.question_count >= MIN_QUESTIONS and end_button:
        st.session_state.step = 3
        st.rerun()

# Step 3: Interview Summary and AI-Generated Report
elif st.session_state.step == 3:
    st.header("📊 Interview Summary")
    
    # Generate AI summary of the interview
    if "interview_summary" not in st.session_state:
        try:
            # Prepare conversation for summary generation
            conversation_text = "\n".join([
                f"{'Candidate' if msg['role'] == 'user' else 'Interviewer'}: {msg['content']}"
                for msg in st.session_state.chat_history
            ])
            
            summary_prompt = f"""
            Generate a comprehensive interview summary based on the following conversation:
            
            Candidate Information:
            - Name: {st.session_state.candidate_data.get('full_name')}
            - Experience: {st.session_state.candidate_data.get('years_experience')} years
            - Position Applied: {st.session_state.candidate_data.get('desired_position')}
            - Tech Stack: {', '.join(st.session_state.candidate_data.get('tech_stack', []))}
            
            Interview Conversation:
            {conversation_text}
            
            Please provide a structured summary with:
            1. Overall Assessment (1-2 paragraphs)
            2. Technical Skills Evaluation
            3. Communication Skills
            4. Strengths Identified
            5. Areas for Improvement
            6. Recommendation (Hire/Don't Hire/Further Review)
            7. Suggested Next Steps
            
            Keep it professional and objective.
            """
            
            resp = requests.post(f"{BACKEND_URL}/chat", json={
                "session_id": st.session_state.session_id,
                "user_message": summary_prompt,
                "conversation_history": []
            })
            
            if resp.status_code == 200:
                st.session_state.interview_summary = resp.json()["reply"]
            else:
                st.session_state.interview_summary = "Summary generation failed. Please review the conversation manually."
                
        except Exception as e:
            st.session_state.interview_summary = f"Error generating summary: {e}"
    
    # Display candidate information
    st.subheader("👤 Candidate Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {st.session_state.candidate_data.get('full_name')}")
        st.write(f"**Email:** {st.session_state.candidate_data.get('email')}")
        st.write(f"**Phone:** {st.session_state.candidate_data.get('phone')}")
    
    with col2:
        st.write(f"**Experience:** {st.session_state.candidate_data.get('years_experience')} years")
        st.write(f"**Position:** {st.session_state.candidate_data.get('desired_position')}")
        st.write(f"**Location:** {st.session_state.candidate_data.get('current_location')}")
    
    st.write(f"**Tech Stack:** {', '.join(st.session_state.candidate_data.get('tech_stack', []))}")
    
    # Display AI-generated summary
    st.subheader("🤖 AI-Generated Interview Assessment")
    st.write(st.session_state.interview_summary)
    
    # Interview statistics
    st.subheader("📈 Interview Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Questions", st.session_state.question_count)
    
    with col2:
        user_responses = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
        st.metric("Responses Given", user_responses)
    
    with col3:
        avg_response_length = sum(len(msg["content"].split()) for msg in st.session_state.chat_history if msg["role"] == "user") / max(user_responses, 1)
        st.metric("Avg Response Length", f"{int(avg_response_length)} words")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Summary", type="primary", use_container_width=True):
            # Create downloadable summary
            summary_text = f"""
Interview Summary - {st.session_state.candidate_data.get('full_name')}
{'='*60}

Candidate Information:
- Name: {st.session_state.candidate_data.get('full_name')}
- Email: {st.session_state.candidate_data.get('email')}
- Phone: {st.session_state.candidate_data.get('phone')}
- Experience: {st.session_state.candidate_data.get('years_experience')} years
- Position: {st.session_state.candidate_data.get('desired_position')}
- Location: {st.session_state.candidate_data.get('current_location')}
- Tech Stack: {', '.join(st.session_state.candidate_data.get('tech_stack', []))}

AI Assessment:
{st.session_state.interview_summary}

Interview Statistics:
- Total Questions Asked: {st.session_state.question_count}
- Total Responses: {len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])}
- Interview Duration: Full conversation completed

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            st.download_button(
                label="📄 Download as Text File",
                data=summary_text,
                file_name=f"interview_summary_{st.session_state.candidate_data.get('full_name', 'candidate').lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🔄 Start New Interview", type="secondary", use_container_width=True):
            reset()
            st.rerun()
    
    st.success("🎉 Interview completed successfully!")

# Sidebar with helpful information
with st.sidebar:
    st.markdown("### 📋 Interview Guide")
    st.write("**Tips for a great interview:**")
    st.write("• Be specific about your experience")
    st.write("• Provide concrete examples")
    st.write("• Ask questions about the role")
    st.write("• Be honest about your skills")
    
    st.markdown("### 🛠️ Technical Focus")
    if "candidate_data" in st.session_state:
        tech_stack = st.session_state.candidate_data.get("tech_stack", [])
        if tech_stack:
            st.write("We'll focus on:")
            for tech in tech_stack:
                st.write(f"• {tech}")
    
    # Show progress in sidebar during interview
    if st.session_state.step == 2:
        st.markdown("### 📊 Interview Progress")
        st.write(f"Questions asked: {st.session_state.question_count}")
        st.write(f"Minimum required: {MIN_QUESTIONS}")
        st.write(f"Maximum questions: {MAX_QUESTIONS}")
        
        if st.session_state.question_count >= MIN_QUESTIONS:
            st.success("✅ Minimum questions reached!")
        else:
            remaining = max(0, MIN_QUESTIONS - st.session_state.question_count)
            st.info(f"🎯 {remaining} more to go!")
    

