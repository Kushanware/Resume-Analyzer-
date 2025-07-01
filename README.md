# Resume Analyzer

**Live Demo:** [smartresumematch.streamlit.app](https://smartresumematch.streamlit.app/)

A Streamlit web app that analyzes resumes against job descriptions using Google Gemini AI. Upload your resume (PDF) and paste a job description to get:
- Professional resume analysis
- Skill extraction and categorization
- Skill gap and improvement suggestions
- Skill match percentage
- Resume weaknesses
- ATS (Applicant Tracking System) score

## Features
- Upload PDF resumes
- Paste or type job descriptions
- AI-powered analysis using Google Gemini
- No Poppler dependency (uses PyMuPDF for PDF processing)
- Streamlit Cloud compatible

## Requirements
- Python 3.8+
- Streamlit
- PyMuPDF
- Pillow
- python-dotenv
- google-generativeai

## Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Kushanware/Resume-Analyzer-.git
   cd Resume-Analyzer-
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root and add your Google API key:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deploying on Streamlit Cloud
1. Push your code to GitHub (including `requirements.txt`, but **not** your `.env` file).
2. On [Streamlit Cloud](https://streamlit.io/cloud), create a new app from your repo.
3. Set the `GOOGLE_API_KEY` as a secret in the Streamlit Cloud app settings.
4. Deploy and use your app online!

## License
MIT


