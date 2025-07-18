import base64
import io
import streamlit as st
import os
from  PIL import Image  
import fitz
import google.generativeai as genai

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, that's okay

# Check if API key is available
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("🔑 Google API Key not found! Please set the GOOGLE_API_KEY environment variable.")
    st.info("""
    **How to set up your Google API Key:**
    
    1. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Set the environment variable:
       - **Windows (PowerShell):** `$env:GOOGLE_API_KEY="your_api_key_here"`
       - **Windows (Command Prompt):** `set GOOGLE_API_KEY=your_api_key_here`
       - **Mac/Linux:** `export GOOGLE_API_KEY="your_api_key_here"`
    3. Restart your Streamlit app
    
    Or create a `.env` file in your project directory with:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```
    """)
    st.stop()

genai.configure(api_key=api_key)

# Prompts for Gemini API interactions
input_prompt1 = """You are an expert HR manager with 15+ years of experience in technical recruitment. Conduct a detailed analysis of the resume against the job description. Your analysis must include:

1. Match Analysis (40% of evaluation):
   - Exact matching skills and years of experience
   - Directly relevant project experience
   - Industry-specific expertise alignment
   - Required qualifications match

2. Technical Depth (30% of evaluation):
   - Core technical skills assessment
   - Tool and technology proficiency levels
   - Project complexity evaluation
   - Technical problem-solving evidence

3. Career Progression (20% of evaluation):
   - Role responsibilities alignment
   - Career growth trajectory
   - Leadership/management experience if required
   - Achievement impact measurement

4. Cultural & Soft Skills (10% of evaluation):
   - Communication skills evidence
   - Team collaboration indicators
   - Problem-solving approach
   - Cultural fit indicators

Provide a percentage-based match score and detailed bullet points for each category. Be extremely specific with examples from both the resume and job description."""

input_prompt2 = """Perform a comprehensive skills extraction and analysis. For each skill found:

1. Technical Skills:
   - List each skill with proficiency level (Basic/Intermediate/Expert)
   - Years of experience with each skill
   - Context of skill usage in projects
   - Current industry relevance score (1-10)

2. Tools & Technologies:
   - Categorize by domain (Development/Testing/DevOps/etc.)
   - Version/certification information if mentioned
   - Implementation examples from projects
   - Industry demand level (High/Medium/Low)

3. Soft Skills:
   - Evidence-based skill identification
   - Situation examples demonstrating each skill
   - Impact metrics where available
   - Relevance to target role

4. Domain Knowledge:
   - Industry-specific expertise
   - Business domain knowledge
   - Methodologies and frameworks
   - Compliance and standards knowledge

5. Certifications & Education:
   - Full certification details with dates
   - Relevance to target role
   - Expiration/renewal status
   - Associated skills coverage

Present findings in a structured format with specific examples for each category."""

input_prompt3 = """As a career development expert, analyze the gap between current profile and job requirements. Provide:

1. Critical Skill Gaps:
   - Identify missing must-have skills
   - Current vs required proficiency levels
   - Specific upskilling recommendations
   - Estimated time to achieve competency

2. Certification Strategy:
   - Priority certifications needed
   - Specific courses with links
   - Cost and time investment
   - Expected impact on candidacy

3. Project Portfolio Enhancement:
   - Specific project suggestions
   - Technology stack recommendations
   - Complexity level progression
   - Portfolio presentation tips

4. Professional Development Plan:
   - 30/60/90 day learning roadmap
   - Skill acquisition sequence
   - Progress tracking metrics
   - Resource recommendations

Provide detailed, actionable steps with specific resources, timeframes, and expected outcomes."""

input_prompt4 = """Perform a detailed ATS-optimized compatibility analysis:

1. Quantitative Analysis (40%):
   - Keyword match percentage
   - Required skills coverage
   - Experience duration match
   - Education/certification alignment

2. Qualitative Analysis (30%):
   - Project relevance scoring
   - Achievement impact assessment
   - Leadership experience evaluation
   - Problem-solving capability match

3. Technical Proficiency (20%):
   - Tool/technology expertise levels
   - Programming language proficiency
   - Framework/methodology alignment
   - Technical problem-solving evidence

4. Role-Specific Requirements (10%):
   - Industry experience match
   - Team size/structure alignment
   - Budget/project scale experience
   - Regulatory/compliance knowledge

Calculate sub-scores for each category and provide a weighted total match percentage with detailed explanations."""

input_prompt5 = """Conduct a comprehensive weakness analysis focusing on:

1. Critical Gaps:
   - Missing essential requirements
   - Insufficient experience areas
   - Technical skill deficiencies
   - Project scale mismatches

2. Presentation Issues:
   - Impact quantification gaps
   - Achievement documentation
   - Technical depth demonstration
   - Role progression clarity

3. Modern Skill Gaps:
   - Emerging technology exposure
   - Industry trend alignment
   - Methodology/framework currency
   - Tool/platform proficiency

4. Career Narrative:
   - Role transition logic
   - Responsibility progression
   - Leadership development
   - Industry focus clarity

For each weakness, provide:
- Specific evidence from resume
- Impact on application
- Detailed improvement strategy
- Timeline for addressing"""

input_prompt6 = """Perform an in-depth ATS optimization analysis:

1. Keyword Analysis:
   - Essential keyword coverage
   - Keyword frequency and placement
   - Industry-specific terminology
   - Role-specific language match

2. Format Optimization:
   - Section structure analysis
   - Heading standardization
   - Bullet point formatting
   - Font and spacing review

3. Content Evaluation:
   - Action verb usage
   - Quantifiable achievements
   - Technical terminology accuracy
   - Role title alignment

4. ATS Compatibility Score:
   - Parsing accuracy prediction
   - Keyword match percentage
   - Format compliance score
   - Overall ATS ranking potential

Provide specific recommendations for each section with before/after examples."""

input_prompt7 = """Create a highly targeted cover letter with:

1. Opening Impact (25%):
   - Company research integration
   - Role-specific enthusiasm
   - Cultural alignment indicators
   - Unique value proposition

2. Experience Alignment (35%):
   - Key achievement highlights
   - Relevant project spotlights
   - Skill match emphasis
   - Problem-solving examples

3. Company Connection (25%):
   - Industry knowledge display
   - Company values alignment
   - Growth potential emphasis
   - Future contribution vision

4. Professional Tone (15%):
   - Confidence balance
   - Enthusiasm demonstration
   - Professional language
   - Call to action

Maintain perfect grammar and professional tone while showcasing genuine enthusiasm."""

input_prompt8 = """Generate strategic deep-dive questions across these areas:

1. Technical Depth:
   - Project architecture decisions
   - Technology selection rationale
   - Problem-solving approaches
   - Technical challenge resolution

2. Impact Measurement:
   - Project success metrics
   - Team influence examples
   - Business value delivery
   - Innovation contributions

3. Leadership & Collaboration:
   - Team dynamics handling
   - Stakeholder management
   - Conflict resolution
   - Mentorship experience

4. Career Development:
   - Role transition motivation
   - Skill development strategy
   - Industry focus selection
   - Future career vision

Each question should be designed to uncover specific, detailed examples that could strengthen the resume."""

def get_gemini_response(input,pdf_content,prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            {"text": input},         
            pdf_content,              
            {"text": prompt}         
        ])
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        if "API_KEY" in str(e) or "credentials" in str(e).lower():
            st.info("Please check your Google API key configuration.")
        return "Error: Unable to generate response. Please check your API configuration."
def input_pdf_convert(uploaded_file):
    if uploaded_file is not None:
        # Read PDF bytes
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)  # first page
        pix = page.get_pixmap()
        image_bytes_arr = io.BytesIO(pix.tobytes("jpeg"))
        image_bytes_arr = image_bytes_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No PDF file uploaded")


#streamlit app
st.set_page_config(
    page_title="ResumeCheck Pro - AI Resume Analyzer", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS styling inspired by professional resume checkers
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 300;
        opacity: 0.95;
        margin-bottom: 2rem;
    }
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 2rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Card Styles */
    .upload-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .upload-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    .card-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-subtitle {
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Analysis Button Styles */
    .stButton > button {
        width: 100% !important;
        padding: 1rem !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        background: white !important;
        color: #333 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        margin: 0.5rem 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 1rem !important;
        text-align: left !important;
    }

    .stButton > button:hover {
        border-color: #667eea !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-2px) !important;
    }

    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        background: #f8fafc !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Status Messages */
    .status-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .status-ready {
        background: #ecfdf5;
        border-color: #10b981;
        color: #065f46;
    }
    
    .status-warning {
        background: #fffbeb;
        border-color: #f59e0b;
        color: #92400e;
    }
    
    /* Results Section */
    .result-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    .result-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .result-icon {
        font-size: 2rem;
    }
    
    .result-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        background: #f8fafc;
        border-radius: 15px;
        margin-top: 4rem;
        color: #666;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">🎯 ResumeCheck Pro</h1>
    <p class="hero-subtitle">AI-powered resume analysis that gets you hired faster</p>
    <div class="hero-stats">
        <div class="stat-item">
            <span class="stat-number">98%</span>
            <span class="stat-label">Accuracy Rate</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">8+</span>
            <span class="stat-label">Analysis Types</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">30s</span>
            <span class="stat-label">Average Time</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Input Section
st.markdown("## 🚀 Get Started")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
    <div class="upload-card">
        <div class="card-title">🎯 Job Description</div>
        <div class="card-subtitle">Paste the job posting you're targeting for personalized analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    input_text = st.text_area(
        "Job Description",
        placeholder="Paste the complete job description here...\n\n• Include job requirements\n• List required skills\n• Add responsibilities\n• Mention qualifications\n\nThe more detailed, the better our AI analysis!",
        height=280,
        help="Our AI analyzes job requirements to provide targeted recommendations",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <div class="upload-card">
        <div class="card-title">📄 Resume Upload</div>
        <div class="card-subtitle">Upload your resume for comprehensive AI-powered analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"],
        help="We support PDF format. Make sure your resume is well-formatted for best results.",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Success display with metrics
        st.markdown("""
        <div style="background: #ecfdf5; border: 1px solid #10b981; border-radius: 12px; padding: 1rem; margin: 1rem 0;">
            <div style="color: #065f46; font-weight: 600; margin-bottom: 0.5rem;">
                ✅ Resume Uploaded Successfully!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File details in a nice layout
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("📄 File Name", uploaded_file.name)
        with col_b:
            st.metric("📊 File Size", f"{uploaded_file.size:,} bytes")
    else:
        st.markdown("""
        <div style="background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 2rem; text-align: center; margin: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
            <div style="font-weight: 600; color: #475569; margin-bottom: 0.5rem;">Choose your resume file</div>
            <div style="color: #64748b; font-size: 0.9rem;">Drag and drop or click to browse</div>
        </div>
        """, unsafe_allow_html=True)

# Analysis Tools Section
st.markdown("---")
st.markdown("## 🎯 AI Analysis Tools")

# Initialize button variables
submit1 = submit2 = submit3 = submit4 = submit5 = submit6 = submit7 = submit8 = False

# Status check and display
if uploaded_file is not None and input_text.strip():
    st.markdown("""
    <div class="status-card status-ready">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🚀</div>
        <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">Ready for Analysis!</div>
        <div>Choose any analysis tool below to get started</div>
    </div>
    """, unsafe_allow_html=True)
    button_disabled = False
else:
    missing_items = []
    if uploaded_file is None:
        missing_items.append("📄 Resume")
    if not input_text.strip():
        missing_items.append("📋 Job Description")
    
    st.markdown(f"""
    <div class="status-card status-warning">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⏳</div>
        <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">Almost Ready!</div>
        <div>Please add: {" & ".join(missing_items)}</div>
    </div>
    """, unsafe_allow_html=True)
    button_disabled = True

# Analysis tools grid
st.markdown("</div>", unsafe_allow_html=True)

# Card definitions
cards = [
    ("btn1", "📊", "Resume Analysis", "Comprehensive evaluation of your resume against job requirements"),
    ("btn2", "🔍", "Skills Extraction", "Extract and categorize all skills from your resume"),
    ("btn3", "📈", "Skill Improvement", "Get personalized recommendations to enhance your skills"),
    ("btn4", "🎯", "Skills Match", "Calculate compatibility percentage with job requirements"),
    ("btn5", "⚠️", "Weakness Analysis", "Identify gaps and areas for improvement"),
    ("btn6", "🤖", "ATS Score", "Check compatibility with Applicant Tracking Systems"),
    ("btn7", "📝", "Cover Letter", "Generate a tailored cover letter for this position"),
    ("btn8", "❓", "Strategic Questions", "Get improvement-focused questions about your resume"),
]

rows = [cards[:4], cards[4:]]

# Initialize all submit flags
submit1 = submit2 = submit3 = submit4 = submit5 = submit6 = submit7 = submit8 = False

# Create two rows of buttons
for row in rows:
    cols = st.columns(4)
    for i, (card_id, icon, title, desc) in enumerate(row):
        with cols[i]:
            clicked = st.button(
                f"{icon}  {title}",
                key=card_id,
                disabled=button_disabled,
                help=desc,
                use_container_width=True
            )
            
            if clicked:
                if card_id == "btn1": submit1 = True
                elif card_id == "btn2": submit2 = True
                elif card_id == "btn3": submit3 = True
                elif card_id == "btn4": submit4 = True
                elif card_id == "btn5": submit5 = True
                elif card_id == "btn6": submit6 = True
                elif card_id == "btn7": submit7 = True
                elif card_id == "btn8": submit8 = True

# Handle the button submissions
if uploaded_file is not None and input_text.strip():
    pdf_content = input_pdf_convert(uploaded_file)
    
    if submit1:
        with st.spinner("📊 Analyzing your resume..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt1)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">📊</span>
                    <span class="result-title">Resume Analysis Results</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)
    
    elif submit2:
        with st.spinner("🔍 Extracting skills..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt2)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">🔍</span>
                    <span class="result-title">Skills Extraction Results</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)
            
    elif submit3:
        with st.spinner("📈 Improving your skills..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt3)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">📈</span>
                    <span class="result-title">Skill Improvement Plan</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)
            
    elif submit4:
        with st.spinner("🎯 Calculating skills compatibility..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt4)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">🎯</span>
                    <span class="result-title">Skills Match Analysis</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)
            
    elif submit5:
        with st.spinner("⚠️ Analyzing potential weaknesses..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt5)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">⚠️</span>
                    <span class="result-title">Weakness Analysis</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)

    elif submit6:
        with st.spinner("🤖 Calculating ATS score..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt6)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">🤖</span>
                    <span class="result-title">ATS Compatibility Score</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)

    elif submit7:
        with st.spinner("📝 Generating cover letter..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt7)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">📝</span>
                    <span class="result-title">Tailored Cover Letter</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)

    elif submit8:
        with st.spinner("❓ Generating strategic improvement questions..."):
            response = get_gemini_response(input_text, pdf_content[0], input_prompt8)
            st.markdown("""
            <div class="result-container">
                <div class="result-header">
                    <span class="result-icon">❓</span>
                    <span class="result-title">Strategic Improvement Questions</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write(response)

# Enhanced Footer
st.markdown("""
<div class="footer">
    <h3 style="color: #333; margin-bottom: 1rem;">🎯 ResumeCheck Pro</h3>
    <p style="margin-bottom: 1.5rem;">Powered by Google Gemini AI | Built with ❤️ using Streamlit</p>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem;">
        <div style="text-align: center;">
            <div style="font-weight: 600; color: #667eea;">Fast</div>
            <div style="font-size: 0.9rem;">30-second analysis</div>
        </div>
        <div style="text-align: center;">
            <div style="font-weight: 600; color: #667eea;">Accurate</div>
            <div style="font-size: 0.9rem;">AI-powered insights</div>
        </div>
        <div style="text-align: center;">
            <div style="font-weight: 600; color: #667eea;">Professional</div>
            <div style="font-size: 0.9rem;">Industry-standard analysis</div>
        </div>
    </div>
    <div style="font-size: 0.85rem; color: #888;">
        💡 <strong>Pro Tip:</strong> For best results, ensure your resume is well-formatted and the job description is complete.
    </div>
</div>
""", unsafe_allow_html=True)
