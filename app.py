import base64
import io
import streamlit as st
import os
from  PIL import Image
import fitz
import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input,pdf_content,prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([
        {"text": input},         
        pdf_content,              
        {"text": prompt}         
    ])
    return response.text
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
st.set_page_config(page_title="Resume Analyzer", page_icon=":books:", layout="wide")

# Native Streamlit header and subtitle
st.title("📚 Resume Analyzer")
st.subheader("AI-powered resume and job description analysis")
st.markdown("""
    <head>
        <title>Smart Resume Analyzer - AI Resume Insights</title>
        <meta name="description" content="Analyze your resume using AI to optimize it for job applications and ATS systems. Get score, tips, and feedback instantly.">
        <meta name="keywords" content="Resume Analyzer, Resume Scanner, ATS Resume Check, AI Resume Review, Smart Resume Tool">
        <meta name="robots" content="index, follow">
    </head>
""", unsafe_allow_html=True)
st.write("Optimize your resume with our smart analyzer. Get your ATS score and improve your chances of landing a job.")

# Main input area in columns
col1, col2 = st.columns([1, 1])
with col1:
    input_text = st.text_area("Job Description", placeholder="Paste or type the job description here", key="input", height=200)
with col2:
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
    if uploaded_file is not None:
        st.success("PDF Uploaded Successfully")

# Action buttons in a horizontal row
st.divider()
col_btns = st.columns(3)
with col_btns[0]:
    submit1 = st.button("Resume Analysis")
    submit2 = st.button("Highlight Skills")
    submit7 = st.button("Generate Cover Letter")
with col_btns[1]:
    submit3 = st.button("Improve Skills")
    submit4 = st.button("Skills Match %")
    submit8 = st.button("Question on resume ")
   
with col_btns[2]:
    submit5 = st.button("Resume Weaknesses")
    submit6 = st.button("ATS Score")
   

# Prompts (unchanged)
input_prompt1 = """
You are an experienced HR manager and resume analyst. Analyze the provided resume and job description in detail. In your response, include:
- A summary of how well the resume aligns with the job requirements.
- The candidate's key strengths relevant to the job.
- Any significant gaps or mismatches.
- Whether the resume would be compelling to a recruiter for this specific role.
Please provide your assessment in clear, actionable bullet points.
"""
input_prompt2 = """
Review the provided resume and extract all key skills, certifications, tools, and technologies. Organize them into categories such as:
- Technical Skills (e.g., programming languages, frameworks)
- Soft Skills (e.g., communication, teamwork)
- Certifications
- Tools & Platforms
Present your findings in a structured list or table.
"""
input_prompt3 = """
Compare the skills in the resume with those required in the job description. For each missing or underdeveloped skill, suggest practical ways to improve (e.g., recommended courses, certifications, or projects). Also, highlight which existing skills should be further developed. Prioritize the most critical skill gaps for the job.
"""
input_prompt4 = """
Compare the required skills from the job description with those in the resume. For each skill, indicate if it is a perfect match, partial match, or missing. Calculate the percentage of required skills present in the resume and explain your calculation. Present your findings in a table and provide a final skill alignment percentage.
"""
input_prompt5 = """
Identify and list the main weaknesses or areas for improvement in the resume, considering the job description. For each weakness (e.g., missing skills, lack of achievements, formatting issues), explain its impact on job prospects and provide specific, actionable suggestions to address it. Prioritize the most critical weaknesses.
"""
input_prompt6 = """
You are an expert ATS system trained to evaluate resumes for job matching and parsing accuracy.

I will provide you with:
1. A job description
2. A candidate's resume

Your task is to perform a full ATS-focused analysis.

Step-by-step, do the following:

1. ATS Score (Out of 100)
Break down the score into:
- Keyword Match (30 points): Match of skills, tools, and job-specific terms
- Formatting (15 points): Is the resume clean, parseable (no tables, images, fancy columns)?
- Relevance (25 points): How well do the candidate's experience, education, and achievements fit the role?
- Skills Coverage (20 points): Are required hard and soft skills from the JD mentioned?
- Section Structure (10 points): Are standard headers like Education, Experience, Skills used?

Then provide a final score out of 100 with a one-line summary.

2. Parsing Issues
List any formatting or structural issues that could prevent proper parsing by an ATS (e.g., images, tables, non-standard fonts, missing section headers, PDF problems, etc.)

3. Suggestions to Improve ATS Optimization
Provide 3–5 realistic suggestions to improve the resume's chances of getting past ATS screening, especially for this job.

Be strict but fair. Do not inflate the score — a good resume should score around 70–80. Only exceptional ones should score 90+.

At the end, provide a summary table of your scoring breakdown.

---

Job Description:
[Insert Job Description Here]

Resume:
[Insert Resume Text Here]
"""
input_prompt7= """
Write a professional and concise cover letter tailored to the provided resume and job description. The letter should include:
- A brief introduction
- A body highlighting the candidate's most relevant skills and experiences
- A closing statement expressing interest in the role
Limit the letter to 3–4 paragraphs.
"""
input_prompt8= """
You are a highly experienced HR specialist and resume strategist. Based on my resume (and job description, if provided), generate 5–7 thought-provoking, improvement-focused questions that will help me strengthen my resume and better align it with the target role. Focus on areas such as skill gaps, achievements, clarity, and relevance to the job.
"""

if uploaded_file is not None:
    if submit1:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt1)
        st.subheader("Resume Analysis")
        st.write(response)
    elif submit2:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt2)
        st.subheader("Skills in the Resume")
        st.write(response)
    elif submit3:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt3)
        st.subheader("Suggestions to Improve Skills")
        st.write(response)
    elif submit4:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt4)
        st.subheader("Skills Match Percentage")
        st.write(response)
    elif submit5:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt5)
        st.subheader("Resume Weaknesses")
        st.write(response)
    elif submit6:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt6)
        st.subheader("Estimated ATS Score")
        st.write(response)
    elif submit7:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt7)
        st.subheader("Generated Cover Letter")
        st.write(response)
        st.download_button("Download Cover Letter", response, file_name="cover_letter.txt")
    elif submit8:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt8)
        st.subheader("Questions on resume")
        st.write(response)
        
   