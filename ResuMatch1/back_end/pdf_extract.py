import os
import re
import ast
import json
from docling.document_converter import DocumentConverter
import requests
import mysql.connector



# Database connection
db = mysql.connector.connect(
    host="localhost",
    port=3308,
    user="root",
    password="CVanalysis@123",
    database="resumes"
)
cursor = db.cursor()

def clean_json_output(text):
    """
    Remove invalid characters or comments from JSON-like strings and sanitize control characters.
    """
    try:
        # Remove any inline comments (e.g., `// comment`)
        text = re.sub(r'(?<!https:)(?<!http:)//.*', '', text)
        # Remove any trailing commas before } or ]
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)

        # Remove control characters except for valid whitespace (tab, newline, carriage return)
        # Control characters range: 0x00-0x1F except \t (0x09), \n (0x0A), \r (0x0D)
        text = ''.join(ch for ch in text if ch == '\t' or ch == '\n' or ch == '\r' or (ord(ch) >= 0x20))

        # Optionally, escape backslashes and quotes if needed (usually not necessary if JSON is valid)
        # text = text.replace('\\', '\\\\').replace('"', '\\"')

        return text.strip()
    except Exception as e:
        print(f"❌ Failed to clean JSON output: {e}")
        return text



# 📄 Use Docling to extract text from PDF
def extract_text_docling(file_path):
    try:
        converter = DocumentConverter()
        result = converter.convert(file_path)
        # You can use .export_to_markdown(), .export_to_text(), or access structured parts
        text = result.document.export_to_text().strip()

        print("Text:", text)

        return text
    except Exception as e:
        print(f"❌ Docling extraction failed for {file_path}: {e}")
        return ""

# Generate structured resume using Ollama
def generate_structured_resume(text):
    prompt = f"""
    You are an expert in extracting structured data from resumes.

    Given the resume text below, extract the information into a *valid JSON object* using double quotes for all keys and string values.

    ### 🔍 Mapping Instructions:
    - Extract "Name", "Email", and "Phone" if available.
    - Group all educational qualifications under "Education" (as a list of dictionaries with "Degree", "Institution", and "Years").
    - Combine any mentions of "Certificates", "Courses", "Trainings", "Licenses", or "Workshops" into a single flat list under "Certifications".
    - Combine and normalize all *skills*, *technical skills*, *software proficiency*, *programming languages*, or *tools* into a single **flat list** under "Skills", like:
    "Skills": ["Python", "Java", "HTML", "CSS", "MySQL"]    
    - Extract "Languages" as a flat list.
    - Extract "Projects" as a list of dictionaries with "Title" and "Description".
    - Include an "Experience" field with past roles, if available, otherwise return an empty list. Combine the role, company and years into a single "flat list" under "Experience".

    ### Always extract the candidate's full name.
    If a name label is not found, infer it using context:
    - Prefer the first line or first few lines before email or phone number.
    - Avoid using lines with address-like words (PO, Road, House, etc).
    - Return a cleaned name in title case.

    ### ⚠️ Output Requirements:
    - Output must be a *strict and clean JSON object* with **no comments**, **no annotations**, and **no explanations**.
    - Use double quotes for all keys and string values.
    - Do **not** include any inline comments like `// missing` or `// unidentified`.
    - '//' in site links are okay. Try to identify them.
    - Omit any field that is not present or identifiable in the resume.
    - Only include empty lists for "Skills", "Languages", and "Projects" **if truly absent**.
    - Omit all other fields if no data is found.

    ### 📄 Resume Text:
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
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ Failed to generate structured resume: {e}")
        return "{}"




# Save parsed data to MySQL
def save_to_mysql(data_dict, filename, folder_id):
    try:
        query1 = "SELECT source_file FROM structured_resumes"
        source_file = []

        cursor.execute(query1)
        results = cursor.fetchall()

        for row in results:
            source_file.append(row[0])

        if filename in source_file:
            print(f"⚠️ {filename} already exists in the database. Skipping...")
        else:

            query2 = """
            INSERT INTO structured_resumes (
                source_file, name, education, skills, projects,
                certificates, languages, experience, folder_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query2, (
                filename,
                data_dict.get("Name", ""),
                str(data_dict.get("Education", [])),
                str(data_dict.get("Skills", [])),
                str(data_dict.get("Projects", [])),
                str(data_dict.get("Certifications", [])),
                str(data_dict.get("Languages", [])),
                str(data_dict.get("Experience", [])),
                folder_id
            ))
            db.commit()
            print(f"💾 Saved {filename} to database.")
    except Exception as e:
        print(f"❌ DB Error in {filename}: {e}")

# Optional: Save only skills to separate table
def save_to_mysql_skills(data_dict, filename, folder_id):
    print("_______________ Skills Data:", data_dict.get("Skills", []))
    try:
        query1 = "SELECT skills FROM skills where folder_id = %s"

        skills = []

        cursor.execute(query1, (folder_id,))
        results = cursor.fetchall()

        for row in results:
            skills.append(row[0])

        for skill in data_dict.get("Skills", []):
            skill = skill.strip()  # Ensure no leading/trailing spaces
            if not skill:
                continue

            print(f"💻 Skill: {skill}")

            query2 = "INSERT INTO skills (skills ,folder_id) VALUES (%s,%s)"

            if skill.lower() in skills:
                continue
            else:
                cursor.execute(query2, (skill.lower(), folder_id))
                db.commit()
                print(f"💾 Saved skill '{skill}' for {filename} to database.")
    except Exception as e:
        print(f"❌ DB Error for skills in {filename}: {e}")



def save_to_mysql_edu(data_dict, filename,folder_id):
    print("_______________ Education Data:", data_dict.get("Education", []))

    try:
        query1 = "SELECT degree FROM education where folder_id = %s"

        education=[]

        cursor.execute(query1, (folder_id,))
        results = cursor.fetchall()

        for row in results:
            education.append(row[0])


        for edu in data_dict.get("Education", []):
            degree = edu.get("Degree", "").lower()
            if not degree:
                continue

            print(f"💻 Education: {degree}")

            
            query2 = "INSERT INTO education (degree,folder_id) VALUES (%s,%s)"

            if degree.lower() in education:
                continue
            else:   
                cursor.execute(query2, (degree.lower(), folder_id))
                db.commit()
                print(f"💾 Saved education for {filename} to database.")
    except Exception as e:
        print(f"❌ DB Error for education in {filename}: {e}")
    
   
def save_to_mysql_project(data_dict, filename, folder_id):
    print("_______________ Project Data:", data_dict.get("Projects", []))
    try:
        query1 = "SELECT title FROM project where folder_id = %s"

        project=[]

        cursor.execute(query1, (folder_id,))
        results = cursor.fetchall()

        for row in results:
            project.append(row[0])


        for pro in data_dict.get("Projects", []):
            title = pro.get("Title", "").lower()
            if not title:
                continue

            print(f"💻 Project: {title}")

            
            query2 = "INSERT INTO project (title,folder_id) VALUES (%s,%s)"

            if title.lower() in project:
                continue
            else:   
                cursor.execute(query2, (title.lower(),  folder_id))
                db.commit()
                print(f"💾 Saved project for {filename} to database.")
    except Exception as e:
        print(f"❌ DB Error for project in {filename}: {e}")
    

    
def save_to_mysql_cert(data_dict, filename, folder_id):
    print("_______________ Certificate Data:", data_dict.get("Certifications", []))
    
    try:
        query1 = "SELECT certifications FROM certificates where folder_id = %s"

        certifications=[]

        cursor.execute(query1, (folder_id,))
        results = cursor.fetchall()

        for row in results:
            certifications.append(row[0])


        for cert in data_dict.get("Certifications", []):
            if not cert:
                continue

            print(f"💻 Certificates: {cert}")

            
            query2 = "INSERT INTO certificates (certifications,folder_id) VALUES (%s,%s)"

            if cert.lower() in certifications:
                continue
            else:   
                cursor.execute(query2, (cert.lower(), folder_id))
                db.commit()
                print(f"💾 Saved certifications for {filename} to database.")
    except Exception as e:
        print(f"❌ DB Error for certifications in {filename}: {e}")
    


def save_to_mysql_exp(data_dict, filename,folder_id):
    print("_______________ Experience Data:", data_dict.get("Experience", []))

    try:
        query1 = "SELECT experience FROM experiences where folder_id = %s"
        experience = []

        cursor.execute(query1, (folder_id,))
        results = cursor.fetchall()

        for row in results:
            experience.append(row[0])

        for exp in data_dict.get("Experience", []):
            if not exp:
                continue

            print(f"💻 Experience: {exp}")

            # exp_str = json.dumps(exp, sort_keys=True)  # Convert dict to string

            query2 = "INSERT INTO experiences (experience,folder_id) VALUES (%s,%s)"

            if exp.lower() in experience:
                continue
            else:
                cursor.execute(query2, (exp.lower(), folder_id))
                db.commit()
                print(f"💾 Saved experiences for {filename} to database.")
    except Exception as e:
        print(f"❌ DB Error for experiences in {filename}: {e}")



# Main loop: Process all PDFs in a folder
# Define the folder path as a constant

def main_doc(FOLDER_PATH, folder_id):
    for filename in os.listdir(FOLDER_PATH):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(FOLDER_PATH, filename)
            print(f"\n📄 Processing: {filename}")

            try:
                extracted_text = extract_text_docling(file_path)
                if not extracted_text:
                    print(f"⚠️ Skipping {filename} due to empty text.")
                    continue

                structured_output = generate_structured_resume(extracted_text)

                print(f"🔍 Generated structured output:\n{structured_output}\n")

                # Use safer JSON parsing
                cleaned_output = clean_json_output(structured_output)
                try:
                    data_dict = json.loads(cleaned_output)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error in {filename}: {e}")
                    print(f"⚠️ Raw JSON received:\n{cleaned_output}")
                    continue

                print(f"\n✅ {filename} Parsed:\n{data_dict}\n")

                # Uncomment when ready
                save_to_mysql(data_dict, filename, folder_id)
                save_to_mysql_skills(data_dict, filename, folder_id)
                save_to_mysql_edu(data_dict, filename, folder_id)
                save_to_mysql_project(data_dict, filename, folder_id)
                save_to_mysql_cert(data_dict, filename, folder_id)
                save_to_mysql_exp(data_dict, filename, folder_id)

            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")



if __name__ == "__main__":
    main_doc()
