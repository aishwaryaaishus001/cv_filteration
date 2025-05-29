import openai
import json
import textwrap
import mysql.connector

# Set your API key
openai.api_key = "sk-proj-LKiobmLKGtcGLo0H1W7VT3BlbkFJQ5KnD6qYP4h8zWNGNAxc"

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    port=3308,
    user="root",
    password="CVanalysis@123",
    database="resumes"
)
cursor = db.cursor()


# Fetch distinct items from the database
def select_mysql_skills():
    cursor.execute("SELECT DISTINCT skills FROM skills;")
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_edu():
    cursor.execute("SELECT DISTINCT degree FROM education;")
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_project():
    cursor.execute("SELECT DISTINCT title FROM project;")
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_cert():
    cursor.execute("SELECT DISTINCT certifications FROM certificates;")
    return [row[0].strip() for row in cursor.fetchall()]

def select_mysql_exp():
    cursor.execute("SELECT DISTINCT experience FROM experiences;")
    return [row[0].strip() for row in cursor.fetchall()]

# Build the GPT prompt with instructions for simple keywords
def build_prompt(job_description, skills, education, projects, certifications, experiences):
    return textwrap.dedent(f"""
        You are an intelligent AI assistant that filters and extracts only the simplest and most relevant job keywords.

        --- JOB DESCRIPTION ---
        {job_description.strip()}

        --- DATABASE ITEMS ---
        Skills: {skills}
        Education: {education}
        Projects: {projects}
        Certifications: {certifications}
        Experience: {experiences}

        --- INSTRUCTIONS ---
        - Return only simple, clear, and common keywords that anyone can quickly understand.
        - Do NOT return full sentences or complex terms.
        - For Skills and Education, select directly from the lists if relevant.
        - For Projects, Certifications, and Experience:
          - Analyze the full entries from the database.
          - Extract ONLY simple, easy-to-understand keywords relevant to the job.
          - If no clear matches, you may add AI-suggested simple keywords relevant to the job.
        - Output a clean JSON object with 5 fields:

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

# Parse GPT JSON output
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
def main_gpt(job_description):
    try:
        skills = select_mysql_skills()
        education = select_mysql_edu()
        projects = select_mysql_project()
        certifications = select_mysql_cert()
        experiences = select_mysql_exp()

        prompt = build_prompt(job_description, skills, education, projects, certifications, experiences)
        response = query_gpt(prompt)
        print("📤 Raw GPT Output:\n", response)
        result = parse_output(response)

        print("\n✅ Final Job Criteria (Keywords Only):")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"❌ Error in main_gpt: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    job_description = """
       We are hiring a data analyst Candidates should have prior experience working with databases and version control (Git).
    """
    job_criteria = main_gpt(job_description)
    print("\n🎯 Final Job Criteria:", job_criteria)