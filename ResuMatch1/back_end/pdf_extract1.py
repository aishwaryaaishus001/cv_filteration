import os
import re
import json
import requests
import mysql.connector
import mammoth
from docling.document_converter import DocumentConverter


# 🔌 Database connection
db = mysql.connector.connect(
    host="localhost",
    port=3308,
    user="root",
    password="CVanalysis@123",
    database="resumes"
)
cursor = db.cursor()

# 🧼 Clean JSON string from LLM output
def clean_json_output(text):
    try:
        text = re.sub(r'(?<!https:)(?<!http:)//.*', '', text)
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        text = ''.join(ch for ch in text if ch == '\t' or ch == '\n' or ch == '\r' or (ord(ch) >= 0x20))
        return text.strip()
    except Exception as e:
        print(f"❌ Failed to clean JSON output: {e}")
        return text


# 📄 Extract and preprocess text from PDF using Docling
# Note: pyresparser does NOT accept `text`, so we save extracted text to a temp file

def extract_text_docling(file_path):
    try:
        converter = DocumentConverter()
        result = converter.convert(file_path)
        raw_text = result.document.export_to_text().strip()
        print("Raw Text (PDF):", raw_text)

        # Save to temp file for pyresparser
        temp_txt_path = "temp_resume.txt"
        with open(temp_txt_path, "w", encoding="utf-8") as f:
            f.write(raw_text)

        # # Use ResumeParser correctly
        # parsed_data = ResumeParser(temp_txt_path).get_extracted_data()
        # print("Parsed Data (pyresparser):", parsed_data)

        return raw_text
    except Exception as e:
        print(f"❌ Docling extraction or preprocessing failed for {file_path}: {e}")
        return ""

# 📄 Extract text from DOCX using mammoth
def extract_text_docx(file_path):
    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            text = result.value.strip()
            print("Text (DOCX):", text)
            return text
    except Exception as e:
        print(f"❌ DOCX extraction failed for {file_path}: {e}")
        return ""

# 🤖 Call Ollama for structured resume generation
def generate_structured_resume(text):
    prompt = f"""
    You are an expert in extracting structured data from resumes.

    Given the resume text below, extract the information into a *valid JSON object* using double quotes for all keys and string values.

    ### Mapping Instructions:
    - Extract "Name", "Email", and "Phone" if available.
    - Group all educational qualifications under "Education" (as a list of dictionaries with "Degree", "Institution", and "Years").
    - Combine any mentions of "Certificates", "Courses", "Trainings", "Licenses", or "Workshops" into a single flat list under "Certifications".
    - Normalize all skills, software/tools, and programming languages under "Skills": ["Python", "Java", "HTML"].
    - Extract "Languages" as a flat list.
    - Extract "Projects" as a list of dictionaries with "Title" and "Description".
    - Include "Experience" as a flat list. Combine role, company, and years into a single string.

    Always extract the candidate's full name. Prefer lines before email/phone unless address-like.

    ### Output Requirements:
    - Output must be a strict clean JSON object.
    - Use double quotes only. No comments, no explanations.
    - Skip empty fields unless Skills, Languages, or Projects are truly absent.

    ### Resume Text:
    {text}

    Return only the pure JSON object with no extra text.
    """
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json().get("response", "{}").strip()
    except Exception as e:
        print(f"❌ Failed to generate structured resume: {e}")
        return "{}"

# 💾 Save to main structured_resumes table
def save_to_mysql(data_dict, filename):
    try:
        cursor.execute("SELECT source_file FROM structured_resumes")
        if filename in [row[0] for row in cursor.fetchall()]:

            print(f"⚠️ {filename} already exists. Skipping.")
        else:
            resume_path = f"resumes/{filename}"
            
            query = """
            INSERT INTO structured_resumes (
                source_file, name, education, skills, projects,
                certificates, languages, experience, resume_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                filename,
                data_dict.get("Name", ""),
                str(data_dict.get("Education", [])),
                str(data_dict.get("Skills", [])),
                str(data_dict.get("Projects", [])),
                str(data_dict.get("Certifications", [])),
                str(data_dict.get("Languages", [])),
                str(data_dict.get("Experience", [])),
                resume_path
            ))
            db.commit()
            print(f"💾 Saved {filename} to database.")
    except Exception as e:
        print(f"❌ DB Error in {filename}: {e}")

# ⛏ Save to skills table
def save_to_mysql_skills(data_dict, filename):
    try:
        cursor.execute("SELECT skills FROM Skills")
        existing = {row[0] for row in cursor.fetchall()}
        for skill in data_dict.get("Skills", []):
            if skill.strip().lower() not in existing:
                cursor.execute("INSERT INTO Skills (skills) VALUES (%s)", (skill.strip().lower(),))
                db.commit()
                print(f"💾 Skill: {skill}")
    except Exception as e:
        print(f"❌ DB Error for skills in {filename}: {e}")

# ⛏ Save to education table
def save_to_mysql_edu(data_dict, filename):
    try:
        cursor.execute("SELECT degree FROM education")
        existing = {row[0] for row in cursor.fetchall()}
        for edu in data_dict.get("Education", []):
            degree = edu.get("Degree", "").strip().lower()
            if degree and degree not in existing:
                cursor.execute("INSERT INTO education (degree) VALUES (%s)", (degree,))
                db.commit()
                print(f"💾 Education: {degree}")
    except Exception as e:
        print(f"❌ DB Error for education in {filename}: {e}")

# ⛏ Save to project table
def save_to_mysql_project(data_dict, filename):
    try:
        cursor.execute("SELECT title FROM project")
        existing = {row[0] for row in cursor.fetchall()}
        for project in data_dict.get("Projects", []):
            title = project.get("Title", "").strip().lower()
            if title and title not in existing:
                cursor.execute("INSERT INTO project (title) VALUES (%s)", (title,))
                db.commit()
                print(f"💾 Project: {title}")
    except Exception as e:
        print(f"❌ DB Error for project in {filename}: {e}")

# ⛏ Save to certificates table
def save_to_mysql_cert(data_dict, filename):
    try:
        cursor.execute("SELECT certifications FROM certificates")
        existing = {row[0] for row in cursor.fetchall()}
        for cert in data_dict.get("Certifications", []):
            cert = cert.strip().lower()
            if cert and cert not in existing:
                cursor.execute("INSERT INTO certificates (certifications) VALUES (%s)", (cert,))
                db.commit()
                print(f"💾 Certificate: {cert}")
    except Exception as e:
        print(f"❌ DB Error for certificates in {filename}: {e}")

# ⛏ Save to experience table
def save_to_mysql_exp(data_dict, filename):
    try:
        cursor.execute("SELECT experience FROM experiences")
        existing = {row[0] for row in cursor.fetchall()}
        for exp in data_dict.get("Experience", []):
            exp = exp.strip().lower()
            if exp and exp not in existing:
                cursor.execute("INSERT INTO experiences (experience) VALUES (%s)", (exp,))
                db.commit()
                print(f"💾 Experience: {exp}")
    except Exception as e:
        print(f"❌ DB Error for experiences in {filename}: {e}")

# 🚀 Main loop: Process all PDF and DOCX files
FOLDER_PATH = r"D:\deepseek\sampleCVs"

def main_doc():
    for filename in os.listdir(FOLDER_PATH):
        if filename.lower().endswith((".pdf", ".docx")):
            file_path = os.path.join(FOLDER_PATH, filename)
            print(f"\n📄 Processing: {filename}")

            try:
                if filename.lower().endswith(".pdf"):
                    extracted_text = extract_text_docling(file_path)
                else:
                    extracted_text = extract_text_docx(file_path)

                if not extracted_text:
                    print(f"⚠️ Skipping {filename} due to empty text.")
                    continue

                structured_output = generate_structured_resume(extracted_text)
                print(f"🔍 Structured Output:\n{structured_output}\n")

                cleaned_output = clean_json_output(structured_output)
                try:
                    data_dict = json.loads(cleaned_output)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Decode Error in {filename}: {e}")
                    continue

                print(f"\n✅ Parsed Data from {filename}:\n{data_dict}\n")

                # Enable these to save to DB
                save_to_mysql(data_dict, filename)
                save_to_mysql_skills(data_dict, filename)
                save_to_mysql_edu(data_dict, filename)
                save_to_mysql_project(data_dict, filename)
                save_to_mysql_cert(data_dict, filename)
                save_to_mysql_exp(data_dict, filename)

            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    main_doc()

