from dotenv import load_dotenv
import base64
import io

load_dotenv()
import streamlit as st
import os
from  PIL import Image
import pdf2image
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
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        #converts to bytes
        image_bytes_arr = io.BytesIO()
        first_page.save(image_bytes_arr,format='JPEG')
        image_bytes_arr=image_bytes_arr.getvalue()

        pdf_parts=[
            {
                "mime_type":"image/jpeg",
                "data":base64.b64encode(image_bytes_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No PDF file uploaded")


#streamlit app
st.set_page_config(page_title="Resume Analyzer",page_icon=":books:",layout="wide")
st.header("Resume Analyzer")
input_text=st.text_area("Enter Your Job Description here",key="input")

uploaded_file=st.file_uploader("Upload Your Resume here",type=["pdf"])


if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

    submit1 = st.button("tell me about the resume")
    submit2 = st.button("Highlight the skills in the resume")
    submit3 = st.button("how can i improve my skills")
    submit4 = st.button("Percentage of skills match with the job description")
    submit5 = st.button("weakness in the resume")
    submit6 = st.button("Ats score the resume")
    
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
    Assuming the resume will be passed through an Applicant Tracking System (ATS), evaluate how well it is optimized for ATS parsing. Provide an estimated ATS score (out of 100) based on keyword usage, formatting, relevance to the job description, and inclusion of required skills. Also, mention any issues that could prevent the resume from being properly parsed or ranked by the ATS.
    """

    if submit1:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt1)
        st.subheader("The Resume Analysis is:")
        st.write(response)

    elif submit2:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt2)
        st.subheader("The Skills in the Resume are:")
        st.write(response)

    elif submit3:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt3)
        st.subheader("Suggestions to Improve Skills:")
        st.write(response)

    elif submit4:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt4)
        st.subheader("Skills Match Percentage:")
        st.write(response)

    elif submit5:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt5)
        st.subheader("Resume Weaknesses:")
        st.write(response)

    elif submit6:
        pdf_content = input_pdf_convert(uploaded_file)
        response = get_gemini_response(input_text, pdf_content[0], input_prompt6)
        st.subheader("Estimated ATS Score:")
        st.write(response)
