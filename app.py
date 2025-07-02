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
with col_btns[1]:
    submit3 = st.button("Improve Skills")
    submit4 = st.button("Skills Match %")
with col_btns[2]:
    submit5 = st.button("Resume Weaknesses")
    submit6 = st.button("ATS Score")

# Prompts (unchanged)
input_prompt1 = """
You are an experienced HR manager and resume analyst. I have provided a resume and a job description. Please analyze both in detail and provide a professional assessment of the resume in the context of the job description. Mention how well the resume aligns with the job requirements, the strengths of the candidate, and any significant gaps or mismatches. Also, highlight whether the resume would be compelling to a recruiter for this specific job role.
"""
input_prompt2 = """
Based on the resume provided, identify and list all the key technical skills, soft skills, certifications, tools, and technologies mentioned. Categorize them if possible (e.g., Programming Languages, Tools & Platforms, Communication Skills, etc.). This will help in evaluating the skill set of the candidate more effectively.
"""
input_prompt3 = """
Compare the skills listed in the resume with the skills required in the job description. Identify the missing or underdeveloped skills that are critical for the job role. Suggest practical ways the candidate can improve these skills — for example, through specific certifications, online courses, projects, or experiences. Please also highlight which of the existing skills should be enhanced further to improve job readiness.
"""
input_prompt4 = """
Evaluate the resume against the job description and calculate the percentage of skill match. Provide a breakdown of how many required skills are present in the resume and how many are missing. Mention which skills are a perfect match, partial match, or missing entirely. Based on this, give a realistic skill alignment percentage to reflect how well the candidate fits the role.
"""
input_prompt5 = """
After comparing the resume with the job description, identify the key weaknesses or areas for improvement in the resume. This could include missing skills, lack of measurable achievements, formatting issues, vague statements, or outdated technologies. Be specific and constructive, and explain how these weaknesses might affect the chances of getting shortlisted for this particular role.
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
Provide 3–5 realistic suggestions to improve the resume’s chances of getting past ATS screening, especially for this job.

Be strict but fair. Do not inflate the score — a good resume should score around 70–80. Only exceptional ones should score 90+.

---

Job Description:
[Insert Job Description Here]

Resume:
[Insert Resume Text Here]
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
