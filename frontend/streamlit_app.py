# frontend/streamlit_app.py

import sys
import os
sys.path.append(os.path.abspath("."))  

import streamlit as st
from backend.core import CourtroomSimulator
from backend.utils.helpers import truncate_text
import time
import json
from openai import OpenAI


# Page configuration
st.set_page_config(
    page_title="⚖️ IPC Mock Courtroom",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(180deg, #FF9933 0%, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%, #138808 100%);
        color: #2c3e50;
        padding: 2.5rem 1rem 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 2px solid #34495e;
    }
    
    .agent-card {
        background: #34495e;
        color: #ecf0f1;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    
    .legal-section {
        background: #2c3e50;
        color: #ecf0f1;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #34495e;
        margin: 0.5rem 0;
    }
    
    .verdict-card {
        background: #2c3e50;
        color: #ecf0f1;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #3498db;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: #34495e;
        color: #ecf0f1;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .api-info {
        background: #2c3e50;
        color: #ecf0f1;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def validate_groq_api_key(api_key):
    """Validate if the provided Groq API key works."""
    if not api_key or not api_key.startswith('gsk_'):
        return False, "API key should start with 'gsk_'"
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Test with a simple completion
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Test"}],
            model="llama3-70b-8192",
            max_tokens=5
        )
        return True, "API key validated successfully!"
    
    except Exception as e:
        return False, f"API key validation failed: {str(e)}"

def display_legal_section(section, index):
    """Enhanced display for legal sections with better formatting."""
    st.markdown(f"""
    <div class="legal-section">
        <h4 style="color: #3498db;">📌 {section['doc_type']} Section {section['section_id']}</h4>
        <p style="color: #bdc3c7;"><em>{section['title']}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander(f"📖 Read Full Section {section['section_id']}", expanded=False):
        st.markdown(section["content"])
        if 'score' in section:
            st.metric("Relevance Score", f"{section['score']:.3f}")

def display_agent_response(agent_data, agent_name, icon):
    """Enhanced display for agent responses."""
    st.markdown(f"""
    <div class="agent-card">
        <h3 style="color: #3498db;">{icon} {agent_name} Response</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Main argument
    st.markdown("**Legal Argument:**")
    st.markdown(agent_data["argument"])
    
    # Retrieved sections
    if agent_data.get("retrieved_sections"):
        st.markdown("**📚 Supporting Legal Provisions:**")
        for i, section in enumerate(agent_data["retrieved_sections"]):
            display_legal_section(section, i)

def display_trial_metrics(trial_result):
    """Display trial analytics and metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🏛️ Total Sections</h4>
            <h2 style="color: #3498db;">%d</h2>
        </div>
        """ % (
            len(trial_result["prosecution"]["retrieved_sections"]) +
            len(trial_result["defense"]["retrieved_sections"]) +
            len(trial_result["verdict"]["retrieved_sections"])
        ), unsafe_allow_html=True)
    
    with col2:
        ipc_count = sum(1 for case in [trial_result["prosecution"], trial_result["defense"], trial_result["verdict"]]
                       for section in case["retrieved_sections"] if section["doc_type"] == "IPC")
        st.markdown("""
        <div class="metric-card">
            <h4>📖 IPC Sections</h4>
            <h2 style="color: #e67e22;">%d</h2>
        </div>
        """ % ipc_count, unsafe_allow_html=True)
    
    with col3:
        crpc_count = sum(1 for case in [trial_result["prosecution"], trial_result["defense"], trial_result["verdict"]]
                        for section in case["retrieved_sections"] if section["doc_type"] == "CRPC")
        st.markdown("""
        <div class="metric-card">
            <h4>⚖️ CrPC Sections</h4>
            <h2 style="color: #f1c40f;">%d</h2>
        </div>
        """ % crpc_count, unsafe_allow_html=True)
    
    with col4:
        evidence_count = sum(1 for case in [trial_result["prosecution"], trial_result["defense"], trial_result["verdict"]]
                           for section in case["retrieved_sections"] if section["doc_type"] == "EVIDENCE_ACT")
        st.markdown("""
        <div class="metric-card">
            <h4>🔍 Evidence Act</h4>
            <h2 style="color: #2ecc71;">%d</h2>
        </div>
        """ % evidence_count, unsafe_allow_html=True)

def display_sidebar_info():
    """Enhanced sidebar with system information and API key input."""
    st.sidebar.markdown("## 🔑 API Configuration")
    
    # API Key Input Section
    api_key = st.sidebar.text_input(
        "Enter your Groq API Key:",
        type="password",
        placeholder="gsk_...",
        value=st.session_state.get('groq_api_key', ''),
        help="Get your free API key from https://console.groq.com/"
    )
    
    # Store API key in session state
    if api_key != st.session_state.get('groq_api_key', ''):
        st.session_state.groq_api_key = api_key
        st.session_state.api_validated = False
    
    # API Key Validation
    if api_key:
        if st.sidebar.button("🔍 Validate API Key", use_container_width=True):
            with st.spinner("Validating API key..."):
                is_valid, message = validate_groq_api_key(api_key)
                st.session_state.api_validated = is_valid
                st.session_state.api_message = message
        
        # Show validation status
        if hasattr(st.session_state, 'api_validated'):
            if st.session_state.api_validated:
                st.sidebar.success(f"✅ {st.session_state.api_message}")
            else:
                st.sidebar.error(f"❌ {st.session_state.api_message}")
    else:
        st.sidebar.warning("⚠️ Please enter your Groq API key to use the simulator")
        st.sidebar.markdown("[Get your free API key here](https://console.groq.com/)")
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("## 🏛️ About This System")
    st.sidebar.markdown("""
    **AI-Powered Legal Simulation**
    
    This system uses:
    - 🤖 **Groq LLama 3 70B** for legal reasoning
    - 📚 **RAG Technology** for accurate legal citations
    - ⚖️ **Multi-Agent Architecture** for realistic courtroom simulation
    
    **Legal Documents:**
    - Indian Penal Code (IPC)
    - Code of Criminal Procedure (CrPC)  
    - Indian Evidence Act
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Sample Crime Scenarios")
    
    sample_crimes = [
        "Ramesh Gupta, a 45-year-old businessman, was driving his car under heavy alcohol influence after a party. At 11:30 PM, he lost control and hit a pedestrian, Suresh, who was crossing the road legally. Suresh suffered severe head injuries and died on the spot. Police arrived and conducted a breathalyzer test showing Ramesh's blood alcohol level was 0.15%, well above the legal limit. CCTV footage from nearby shops captured the entire incident. Ramesh tried to flee the scene but was caught by bystanders and handed over to police.",
        
        "Dr. Priya Mehta, a qualified physician, was running an illegal abortion clinic without proper license in Mumbai. She performed an unsafe abortion on 22-year-old Kavya, who was 7 months pregnant. Due to Dr. Mehta's negligence and use of outdated equipment, Kavya suffered severe complications and died during the procedure. Police investigation revealed that Dr. Mehta had been operating without valid medical registration for 2 years and had performed over 50 illegal abortions. Evidence included medical records, witness testimonies from other patients, and forensic reports.",
        
        "Vikash Singh, working as an accountant in XYZ Private Limited, systematically embezzled ₹15,00,000 over 18 months by creating fake vendor entries and diverting company funds to his personal account. He forged the Managing Director's signature on multiple payment vouchers and manipulated the accounting software to hide the transactions. The fraud was discovered during an internal audit when discrepancies were found in vendor payments. Bank statements, forged documents, and digital forensic evidence clearly established Vikash's involvement in the financial fraud.",
        
        "Amit Sharma, a 28-year-old software engineer, created a fake Facebook profile using photos of actress Deepika Padukone and used it to befriend and cheat multiple women. He convinced 5 women to transfer money totaling ₹3,50,000 by claiming he needed funds for a medical emergency. He also morphed intimate photos of his victims and blackmailed them for additional money. Victims filed complaints when they discovered the fraud. Police traced his digital footprint through IP addresses, bank transactions, and mobile phone records."
    ]
    
    for i, crime in enumerate(sample_crimes, 1):
        if st.sidebar.button(f"📝 Example {i}", key=f"example_{i}"):
            st.session_state.crime_description = crime

def main():
    # Initialize session state
    if 'groq_api_key' not in st.session_state:
        st.session_state.groq_api_key = ''
    if 'api_validated' not in st.session_state:
        st.session_state.api_validated = False
    if 'api_message' not in st.session_state:
        st.session_state.api_message = ''
    if 'crime_description' not in st.session_state:
        st.session_state.crime_description = ''
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <h1>⚖️ Indian Legal Courtroom Simulator</h1>
            <p>AI-Powered Mock Trial Based on IPC, CrPC & Evidence Act</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    display_sidebar_info()
    
    # Main content
    st.markdown("### 📝 Case Description")
    st.markdown("Describe the alleged crime scenario and watch our AI agents simulate a complete courtroom trial:")
    
    # Input section
    crime_description = st.text_area(
        "",
        placeholder="",
        height=120,
        key="crime_input",
        value=st.session_state.get('crime_description', '')
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Disable button if API key is not set or validated
        api_ready = st.session_state.get('groq_api_key') and st.session_state.get('api_validated', False)
        start_trial = st.button(
            "🚀 Start Mock Trial" if api_ready else "🔑 Setup API Key First", 
            type="primary", 
            use_container_width=True,
            disabled=not api_ready
        )
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.crime_description = ""
            st.rerun()
    
    with col3:
        if st.button("💡 Get Example", use_container_width=True):
            st.session_state.crime_description = "On the night of January 15th, 2024, Rajesh Kumar broke into Mrs. Sharma's house in Sector 15, Noida, at 2:30 AM by cutting the window grille with wire cutters. He entered the bedroom where Mrs. Sharma was sleeping alone and stole her gold jewelry worth ₹2,50,000 from the bedroom cupboard, along with ₹15,000 cash from her purse. When Mrs. Sharma woke up due to noise and screamed for help, Rajesh panicked and pushed her violently to prevent her from raising an alarm, causing her to fall and fracture her left wrist. A neighbor, Mr. Gupta, witnessed Rajesh climbing out of the window with a bag and immediately called the police. Rajesh was apprehended 500 meters away with the stolen jewelry still in his possession. During interrogation, Rajesh claimed he was heavily intoxicated and doesn't clearly remember committing the offense. Medical examination confirmed Mrs. Sharma's wrist fracture and documented bruises on her arm."
            st.rerun()

    # Trial execution
    if start_trial:
        if not crime_description.strip():
            st.error("⚠️ Please enter a valid crime description to proceed.")
            return
        
        # Check if API key is provided and validated
        if not st.session_state.get('groq_api_key'):
            st.error("🔑 Please enter your Groq API key in the sidebar first.")
            return
        
        if not st.session_state.get('api_validated', False):
            st.warning("⚠️ Please validate your API key in the sidebar before running the trial.")
            return
        
        # Set the API key in environment for the backend to use
        os.environ['GROQ_API_KEY'] = st.session_state.groq_api_key
        
        # Progress tracking
        progress_container = st.container()
        with progress_container:
            st.markdown("### 🔄 Trial in Progress...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate trial with progress updates
            try:
                status_text.text("🏛️ Initializing courtroom...")
                progress_bar.progress(10)
                time.sleep(1)
                
                simulator = CourtroomSimulator()
                
                status_text.text("👨‍⚖️ Prosecution building case...")
                progress_bar.progress(30)
                time.sleep(1)
                
                status_text.text("🧑‍⚖️ Defense preparing argument...")
                progress_bar.progress(60)
                time.sleep(1)
                
                status_text.text("🔍 Cross-examination in progress...")
                progress_bar.progress(80)
                time.sleep(1)
                
                status_text.text("⚖️ Judge deliberating verdict...")
                progress_bar.progress(90)
                
                trial_result = simulator.run_trial(crime_description)
                
                progress_bar.progress(100)
                status_text.text("✅ Trial completed successfully!")
                time.sleep(1)
                
                # Clear progress
                progress_container.empty()
                
            except Exception as e:
                st.error(f"❌ Trial simulation failed: {str(e)}")
                return

        # Display results
        st.success("🎉 **Mock Trial Completed Successfully!**")
        
        # Trial metrics
        st.markdown("### 📊 Trial Analytics")
        display_trial_metrics(trial_result)
        
        st.markdown("---")
        
        # Create tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs([
            "👨‍⚖️ Prosecution", 
            "🧑‍⚖️ Defense", 
            "🔍 Cross-Examination", 
            "⚖️ Final Verdict"
        ])
        
        with tab1:
            display_agent_response(
                trial_result["prosecution"], 
                "Prosecution", 
                "👨‍⚖️"
            )
        
        with tab2:
            display_agent_response(
                trial_result["defense"], 
                "Defense", 
                "🧑‍⚖️"
            )
        
        with tab3:
            st.markdown("""
            <div class="agent-card">
                <h3 style="color: #3498db;">🔍 Cross-Examination Questions</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Critical Questions Raised:**")
            st.markdown(trial_result["cross_examination"]["questions"])
            
            if trial_result["cross_examination"].get("retrieved_sections"):
                st.markdown("**📚 Supporting Legal Analysis:**")
                for i, section in enumerate(trial_result["cross_examination"]["retrieved_sections"]):
                    display_legal_section(section, i)
        
        with tab4:
            st.markdown("""
            <div class="verdict-card">
                <h3 style="color: #3498db;">⚖️ Final Judgment</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Court's Decision:**")
            st.markdown(trial_result["verdict"]["verdict"])
            
            if trial_result["verdict"].get("retrieved_sections"):
                st.markdown("**📚 Legal Basis for Verdict:**")
                for i, section in enumerate(trial_result["verdict"]["retrieved_sections"]):
                    display_legal_section(section, i)
        
        # Download trial transcript
        st.markdown("---")
        st.markdown("### 📄 Trial Transcript")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Download the complete trial proceedings as JSON for your records.")
        
        with col2:
            trial_json = json.dumps(trial_result, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download Transcript",
                data=trial_json,
                file_name=f"trial_transcript_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True
            )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>⚖️ <strong>AI Legal Courtroom Simulator</strong> | Built with Streamlit & Groq API</p>
        <p><em>For educational and demonstration purposes only. Not a substitute for professional legal advice.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()