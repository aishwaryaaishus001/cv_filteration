import openai
import json
import textwrap
import mysql.connector
import os

# Set your API key (you can also use environment variable for safety)
openai.api_key = "sk-proj-LKiobmLKGtcGLo0H1W7VT3BlbkFJQ5KnD6qYP4h8zWNGNAxc"

# 1. Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    port=3308,
    user="root",
    password="CVanalysis@123",
    database="resumes"
)
cursor = db.cursor()


# Fetch distinct items from the database
def select_mysql_skills(folder_id):
    cursor.execute("SELECT DISTINCT skills FROM skills where folder_id = %s", (folder_id,))
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_edu(folder_id):
    cursor.execute("SELECT DISTINCT degree FROM education where folder_id = %s", (folder_id,))
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_project(folder_id):
    cursor.execute("SELECT DISTINCT title FROM project where folder_id = %s", (folder_id,))
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_cert(folder_id):
    cursor.execute("SELECT DISTINCT certifications FROM certificates where folder_id = %s", (folder_id,))
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_exp(folder_id):
    cursor.execute("SELECT DISTINCT experience FROM experiences where folder_id = %s", (folder_id,))
    return [row[0].strip() for row in cursor.fetchall()]



def build_prompt(job_description, skills, education, projects, certifications, experiences):
    return textwrap.dedent(f"""
        You are a strict AI assistant that selects only the required job criteria from the given lists based on the job description.
        Do not include any extra information or context. Only select items that match or are strongly related to the job description.

        --- JOB DESCRIPTION ---
        {job_description.strip()}

        --- ITEMS LIST ---
        Skills: {skills}
        Education: {education}
        Projects: {projects}
        Certifications: {certifications}
        Experience: {experiences}

        --- INSTRUCTIONS ---
        - Select entries only if they are clearly relevant or required for the job.
        - Include skills that are relevant or required for the job.
        - For Education, combine both full forms and abbreviations into a single list.
        - For project, certifiacations and experience, select only *relevant keywords* (not full sentences) that match the job description.
        - Do not invent, rephrase, generalize, or modify any items.
        - Output must be a valid JSON object in the format below:

        {{
            "Skills": [...],
            "Education": [...],
            "Projects": [...],
            "Certifications": [...],
            "Experience": [...]
        }}
    """)



# Query GPT model
def query_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ GPT Query Error: {e}")
        return ""

# Parse output as JSON
def parse_output(output):
    try:
        start = output.find('{')
        end = output.rfind('}') + 1
        json_text = output[start:end]
        return json.loads(json_text)
    except Exception as e:
        print(f"⚠️ JSON Parse Error: {e}")
        print("Raw output:\n", output)
        return {}

# Main function
def main_gpt(job_description, folder_id):
    try:
        skills = select_mysql_skills(folder_id)
        education = select_mysql_edu(folder_id)
        projects = select_mysql_project(folder_id)
        certifications = select_mysql_cert(folder_id)
        experiences = select_mysql_exp(folder_id) 


        prompt = build_prompt(job_description, skills, education, projects, certifications, experiences)
        response = query_gpt(prompt)
        print("📤 Raw GPT Output:\n", response)
        result = parse_output(response)
        print("\n✅ Filtered Job Criteria:")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"❌ Error in main_gpt: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    job_description = """
       We are hiring a skilled data scientist to join our team. The ideal candidate will have experience with machine learning, data visualization
    """
    folder_id = 31
    job_criteria = main_gpt(job_description, folder_id)
    print("\n🎯 Final Job Criteria:", job_criteria)
    # Save job_criteria to a file
    with open("job_criteria.json", "w") as f:
        json.dump(job_criteria, f, indent=2)
    print("Job criteria saved to job_criteria.json")


