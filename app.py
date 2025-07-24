import streamlit as st
import fitz  # PyMuPDF
from docx import Document
import re
import spacy
import pandas as pd
import json
from io import StringIO

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Predefined skill list (expand as needed)
SKILLS_DB = [
    "Python", "Java", "JavaScript", "SQL", "Machine Learning", "Data Analysis", "Excel",
    "Communication", "Project Management", "AWS", "Docker", "Kubernetes", "C++", "C#", "React"
]

def extract_text_from_pdf(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text

def extract_text_from_docx(file_bytes):
    doc = Document(file_bytes)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)

def preprocess_text(text):
    # Remove excess whitespace, non-ascii chars etc
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_email(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def extract_phone(text):
    pattern = r'\b(?:\+?(\d{1,3}))?[-.\s]?(\(?\d{3}\)?)[-.\s]?(\d{3})[-.\s]?(\d{4})\b'
    matches = re.findall(pattern, text)
    if matches:
        phone = "".join(matches[0])
        phone = re.sub(r'[^\d+]', '', phone)
        return phone
    return None

def extract_skills(text):
    text_lower = text.lower()
    skills_found = []
    for skill in SKILLS_DB:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            skills_found.append(skill)
    return list(set(skills_found))

def extract_education(text):
    education = []
    degree_pattern = re.compile(
        r"(Bachelor|Master|B\.Sc|M\.Sc|Ph\.D|BA|MA|BS|MS|BEng|MEng|Bachelors|Masters)[^\.,\n]+", re.I)
    degrees = degree_pattern.findall(text)

    edu_keywords = ["university", "college", "institute", "school"]
    doc = nlp(text.lower())
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    for org in orgs:
        for kw in edu_keywords:
            if kw in text.lower():
                education.append({"institution": org.title(), "degree": None})
                break

    if education and degrees:
        for idx in range(min(len(education), len(degrees))):
            education[idx]["degree"] = degrees[idx]

    return education

def extract_experience(text):
    experience = []
    date_pattern = re.compile(r"(\d{4}[-/]\d{4}|\d{4}\s*-\s*Present|\d{4}\s*-\s*\d{4})")
    doc = nlp(text)

    work_keywords = ["experience", "worked", "work", "employment", "job", "company"]
    sentences = [sent.text for sent in doc.sents]
    for sent in sentences:
        if any(word in sent.lower() for word in work_keywords):
            orgs = [ent.text for ent in nlp(sent).ents if ent.label_ == "ORG"]
            dates = date_pattern.findall(sent)
            for idx, org in enumerate(orgs):
                date_range = dates[idx] if idx < len(dates) else None
                experience.append({"company": org.title(), "date_range": date_range})
    return experience

def parse_resume(text):
    text = preprocess_text(text)
    parsed = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text)
    }
    return parsed

def display_parsed_data(parsed):
    st.subheader("Basic Info")
    st.write(f"**Name:** {parsed.get('name')}")
    st.write(f"**Email:** {parsed.get('email')}")
    st.write(f"**Phone:** {parsed.get('phone')}")

    st.subheader("Skills")
    skills = parsed.get("skills")
    if skills:
        for skill in skills:
            st.markdown(f"- {skill}")
    else:
        st.write("No skills extracted.")

    st.subheader("Education")
    education = parsed.get("education")
    if education:
        df_edu = pd.DataFrame(education)
        st.dataframe(df_edu)
    else:
        st.write("No education info extracted.")

    st.subheader("Experience")
    experience = parsed.get("experience")
    if experience:
        df_exp = pd.DataFrame(experience)
        st.dataframe(df_exp)
    else:
        st.write("No experience info extracted.")

def prepare_csv_bytes(parsed):
    skills = parsed.get("skills", [])
    education = parsed.get("education", [])
    experience = parsed.get("experience", [])

    education_str = "; ".join([f"{ed.get('institution', '')} - {ed.get('degree', '')}" for ed in education]) if education else ""
    experience_str = "; ".join([f"{exp.get('company', '')} - {exp.get('date_range', '')}" for exp in experience]) if experience else ""

    data = {
        "name": parsed.get("name",""),
        "email": parsed.get("email",""),
        "phone": parsed.get("phone",""),
        "skills": ", ".join(skills),
        "education": education_str,
        "experience": experience_str
    }

    df = pd.DataFrame([data])
    csv_bytes = df.to_csv(index=False).encode()
    return csv_bytes

st.title("🧠 Smart Resume Parser")

uploaded_file = st.file_uploader("Upload a Resume (PDF or DOCX)", type=["pdf","docx"])

if uploaded_file:
    st.write(f"Uploaded file: {uploaded_file.name}")

    try:
        if uploaded_file.name.lower().endswith(".pdf"):
            bytes_data = uploaded_file.read()
            raw_text = extract_text_from_pdf(bytes_data)
        elif uploaded_file.name.lower().endswith(".docx"):
            bytes_data = uploaded_file.getvalue()
            raw_text = extract_text_from_docx(bytes_data)
        else:
            st.error("Unsupported file format!")
            st.stop()
    except Exception as e:
        st.error(f"Failed to extract text: {e}")
        st.stop()

    if raw_text:
        st.header("Extracted Resume Text (Preview)")
        st.text(raw_text[:1000] + ("..." if len(raw_text) > 1000 else ""))

        with st.spinner("Parsing resume..."):
            parsed = parse_resume(raw_text)

        st.header("📋 Parsed Data (JSON Format)")
        st.json(parsed)

        display_parsed_data(parsed)

        st.header("Export Parsed Data")

        # JSON export
        json_str = json.dumps(parsed, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="parsed_resume.json",
            mime="application/json"
        )

        # CSV export
        csv_bytes = prepare_csv_bytes(parsed)
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name="parsed_resume.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload a PDF or DOCX resume file to start parsing.")