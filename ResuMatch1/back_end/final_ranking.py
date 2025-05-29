import requests  # Add this import at the top of the file
from rapidfuzz import fuzz  # Add this import at the top of the file
import ast  # For safely parsing stringified lists/dictionaries
import mysql.connector  # Ensure you have this installed


# Database connection
db = mysql.connector.connect(
    host="localhost",
    port=3308,
    user="root",
    password="CVanalysis@123",
    database="resumes"
)
cursor = db.cursor()


# 🔹 Parse stringified lists/dictionaries safely
def safe_parse(value):
    try:
        return ast.literal_eval(value) if isinstance(value, str) else value
    except:
        return []

def match_keywords(resume, keyword_dict):
    matches = {}
    threshold = 80
    partial_match_categories = {'Projects', 'Experience', 'Certificates'}
    exact_match_categories = {'Education', 'Skills'}

    for key, keyword_list in keyword_dict.items():
        db_field = key.lower()
        resume_value = resume.get(db_field, '[]')
        parsed_value = safe_parse(resume_value)

        if key in exact_match_categories:
            # Exact substring matching
            if isinstance(parsed_value, list) and parsed_value and isinstance(parsed_value[0], dict):
                flat_text = " ".join([str(v) for d in parsed_value for v in d.values()])
                match = [kw for kw in keyword_list if kw.lower() in flat_text.lower()]
            else:
                match = [kw for kw in keyword_list if any(kw.lower() in str(item).lower() for item in parsed_value)]
        elif key in partial_match_categories:
            # Fuzzy partial matching
            if isinstance(parsed_value, list) and parsed_value and isinstance(parsed_value[0], dict):
                flat_text = " ".join([str(v) for d in parsed_value for v in d.values()])
                match = []
                for kw in keyword_list:
                    for word in flat_text.split():
                        if fuzz.partial_ratio(kw.lower(), word.lower()) >= threshold:
                            match.append(kw)
                            break
            else:
                match = []
                for kw in keyword_list:
                    for item in parsed_value:
                        if fuzz.partial_ratio(kw.lower(), str(item).lower()) >= threshold:
                            match.append(kw)
                            break
        else:
            # Default to exact matching for other categories
            if isinstance(parsed_value, list) and parsed_value and isinstance(parsed_value[0], dict):
                flat_text = " ".join([str(v) for d in parsed_value for v in d.values()])
                match = [kw for kw in keyword_list if kw.lower() in flat_text.lower()]
            else:
                match = [kw for kw in keyword_list if any(kw.lower() in str(item).lower() for item in parsed_value)]

        matches[key] = list(set(match))  # Remove duplicates
    return matches



# ⭐ Calculate score out of 10
def calculate_rank(total_keywords, matched_keywords):
    if total_keywords == 0:
        return 0
    percentage = (len(matched_keywords) / total_keywords) * 100
    return round((percentage / 10), 1)



def generate_explanation(candidate_name, scored_result, keyword_dict):
    prompt = f"Explain the ranking for candidate {candidate_name} based on the following scores and matches:\\n"
    for cat in keyword_dict:
        score = scored_result.get(cat, {}).get("Score", 0)
        matches = scored_result.get(cat, {}).get("Matches", [])
        prompt += f"{cat}: Score {score}, Matches: {matches}\\n"
    prompt += "Provide a concise explanation highlighting strengths and areas for improvement."

    print(f"🔍 Generating explanation for {candidate_name} with prompt: {prompt}")

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ Failed to generate explaination: {e}")
        return "{no explanation available}"
    




def extract_text_from_db(project_id, folder_id, keyword_dict):

    print(f"🔍 Extracting resumes for project_id: {project_id} and folder_id: {folder_id}")


    # ✅ Step 3: Get resumes by folder_id
    cursor.execute("SELECT * FROM structured_resumes WHERE folder_id = %s", (folder_id,))
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    resumes = [dict(zip(column_names, row)) for row in rows]


    # ✅ Step 4: Process each resume
    results = []
    for resume in resumes:
        name = resume.get('name', 'Unknown')
        sourcefile = resume.get('source_file', 'Unknown')
        match_result = match_keywords(resume, keyword_dict)
        total_score = 0
        scored_result = {}

        for key, matched in match_result.items():
            score = calculate_rank(len(keyword_dict.get(key, [])), matched)
            scored_result[key] = {
                'Score': score,
                'Matches': matched
            }
            total_score += score

        scored_result["TotalScore"] = round(total_score, 1)
        results.append({
            "name": name,
            "source_file": sourcefile,
            "result": scored_result
        })


    # ✅ Step 5: Sort results
    ranked_results = sorted(results, key=lambda x: x["result"]["TotalScore"], reverse=True)

        # ✅ Step 6: Generate explanations using LLM
    for entry in ranked_results:
        name = entry["name"]
        scored_result = entry["result"]

        try:
            explanation = generate_explanation(name, scored_result, keyword_dict)
        except Exception as e:
            explanation = f"❗ Failed to generate explanation: {str(e)}"

        entry["summary"] = explanation  # Add LLM explanation

    # ✅ Step 7: Print formatted summaries
    print("\n📄 Formatted Summaries:", ranked_results)
    
    # Return both enriched results and summaries
    return ranked_results

    # # ✅ Step 6: Generate formatted summaries after sorting
    # formatted_summaries = []
    # for entry in ranked_results:
    #     name = entry["name"]
    #     scored_result = entry["result"]
    #     strong = []
    #     weak = []
        
    #     # Determine strong and weak categories
    #     for cat in keyword_dict:
    #         cat_score = scored_result.get(cat, {}).get("Score", 0)
    #         if cat_score >= 5:
    #             strong.append(cat)
    #         elif cat_score == 0:
    #             weak.append(cat)

    #     # Build summary string
    #     summary = f"{name} ➤ Score: {scored_result['TotalScore']}\n"
    #     for cat in keyword_dict:
    #         cat_score = scored_result.get(cat, {}).get("Score", 0)
    #         matches = scored_result.get(cat, {}).get("Matches", [])
    #         summary += f"   🔹 {cat}: {cat_score} ➤ {matches}\n"
    #     summary += f"   \n\n{name} scored {scored_result['TotalScore']} overall. "
    #     if strong:
    #         summary += f"Strong areas: {', '.join(strong)}. "
    #     if weak:
    #         summary += f"Needs improvement in: {', '.join(weak)}. "
    #     if not strong:
    #         summary += "No strong category matches found. "
    #     summary += "To enhance alignment with the job requirements, consider improving resume sections related to experience, projects, and certifications. Highlight achievements, quantify impacts, and tailor content to better reflect the required keywords or criteria for this specific role."


    #     # 🔹 Append summary to both formatted list and ranked result
    #     formatted_summaries.append(summary)
    #     entry["summary"] = summary  # 🔥 Add summary directly to ranked result

  # Ensure OpenAI is installed and configured







# # Example usage
# extract_text_from_db(project_id=99, folder_id=46, keyword_dict={"Skills": ["python", "html", "css", "javascript", "java", "c++", "django", "database management: mysql, postgresql", "problem-solving", "strong analytical and debugging skills", "nodejs", "react.js", "firebase", "mongodb", "mysql", "git", "version control (git)", "database management (mysql, mongodb)", "problem-solving and troubleshooting"], "Education": ["masters of computer application", "master of computer application", "bsc computer science", "mca", "bsc.computer science", "bachelor of technology (b.tech)"], "Projects": [], "Experience": ["python full stack developer intern", "frontend web developer"], "Certifications": []})





