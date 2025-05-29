import mysql.connector
import json
from jd_generator1 import main_gpt  # Extracts job criteria as a dict

# 🔌 Connect to MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        port=3308,
        user="root",
        password="CVanalysis@123",
        database="resumes"
    )

# 🧮 Scoring function
def calculate_rank(total_keywords, matched_keywords):
    if total_keywords == 0:
        return 0
    percentage = (len(matched_keywords) / total_keywords) * 100
    return round(percentage / 10, 1)  # Score out of 10

# 📝 Generate explanation per candidate
def generate_candidate_summary(name, result):
    explanation_parts = []
    for category, details in result.items():
        if category in ["TotalScore", "Explanation"]:
            continue

        score = details["Score"]
        matched = details["Matched Keywords"]
        if matched:
            explanation_parts.append(
                f"In **{category}**, matched keywords include: {', '.join(matched)} "
                f"({score} points)."
            )
        else:
            explanation_parts.append(
                f"No relevant keywords were found in **{category}**, contributing 0 points."
            )

    total_score = result["TotalScore"]
    summary = (
        f"{name} scored {total_score}. " +
        " ".join(explanation_parts)
    )
    return summary

# 🔍 Resume matching logic
def match_and_rank_resumes(job_criteria):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM structured_resumes")
    resumes = cursor.fetchall()

    all_results = []

    for resume in resumes:
        result = {}
        total_score = 0

        for category, keywords in job_criteria.items():
            category_value = resume.get(category.lower(), "").lower()
            matched_keywords = []

            for keyword in keywords:
                if keyword.lower() in category_value:
                    matched_keywords.append(keyword)

            score = calculate_rank(len(keywords), matched_keywords)
            total_score += score

            result[category] = {
                "Score": score,
                "Matched Keywords": matched_keywords
            }

        result["TotalScore"] = round(total_score, 1)
        explanation = generate_candidate_summary(resume["name"], result)
        result["Explanation"] = explanation

        all_results.append({
            "name": resume["name"],
            "result": result
        })

    cursor.close()
    db.close()

    return sorted(all_results, key=lambda x: x["result"]["TotalScore"], reverse=True)

# 📋 Print summary table
def print_summary_table(results, job_criteria):
    print("\n📊 Summary Table:")
    
    # Create dynamic header based on job criteria
    headers = ["Rank", "Candidate", "Score", "Top Strengths"] + list(job_criteria.keys())
    header_line = "".join(f"{h:<15}" for h in headers)
    print(header_line)
    print("-" * len(header_line))

    for idx, entry in enumerate(results, start=1):
        name = entry['name']
        total_score = entry['result']['TotalScore']

        # Top strengths = categories with non-zero scores
        strengths = [cat for cat, val in entry['result'].items()
                     if cat not in ["TotalScore", "Explanation"] and val["Score"] > 0]
        strengths_summary = ", ".join(strengths) if strengths else "None"

        # Gather scores for each criterion
        category_scores = []
        for cat in job_criteria:
            score = entry['result'].get(cat, {}).get("Score", 0)
            category_scores.append(f"{score:.1f}")

        # Format and print row
        row = f"{idx:<15}{name:<15}{total_score:<15.1f}{strengths_summary:<20}" + "".join(f"{s:<15}" for s in category_scores)
        print(row)



# 🚀 Main Execution
if __name__ == "__main__":
    job_description = """
    Looking for a Python developer.
    """

    # Step 1: Extract job criteria
    job_criteria = main_gpt(job_description)

    # Step 2: Match resumes
    ranked_results = match_and_rank_resumes(job_criteria)
    print("Ranked Results:", ranked_results)

    # Step 3: Show summary table
    print_summary_table(ranked_results, job_criteria)

    # Step 4: Show detailed explanations
    print("\n📝 Detailed Explanations:")
    for rank, entry in enumerate(ranked_results, start=1):
        print(f"\n{rank}. {entry['name']} ➤ Score: {entry['result']['TotalScore']}")
        print("📄 Explanation:", entry["result"]["Explanation"])
