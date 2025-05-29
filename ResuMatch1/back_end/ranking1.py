import mysql.connector
import json

# 🔌 Connect to MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        port=3308,
        user="root",
        password="CVanalysis@123",
        database="resumes"
    )

# 🔍 Search each resume row and calculate match score with explanations
def match_and_rank_resumes(job_criteria,folder_id=None):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    
    if folder_id:
        cursor.execute("SELECT * FROM structured_resumes WHERE folder_id = %s", (folder_id,))
    else:
        cursor.execute("SELECT * FROM structured_resumes")

    resumes = cursor.fetchall()

    # cursor.execute("SELECT * FROM structured_resumes")
    # resumes = cursor.fetchall()

    all_results = []

    for resume in resumes:
        result = {}
        total_score = 0
        explanations = []

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

            if matched_keywords:
                explanations.append(f"✅ {category}: matched {len(matched_keywords)} of {len(keywords)} ({', '.join(matched_keywords)})")
            else:
                explanations.append(f"❌ {category}: no matches")

        result["TotalScore"] = round(total_score, 1)
        result["Explanation"] = explanations

        all_results.append({
            "name": resume["name"],
            "result": result
        })

    cursor.close()
    db.close()

    return sorted(all_results, key=lambda x: x["result"]["TotalScore"], reverse=True)

# 🥮 Scoring function
def calculate_rank(total_keywords, matched_keywords):
    if total_keywords == 0:
        return 0
    percentage = (len(matched_keywords) / total_keywords) * 100
    return round(percentage / 10, 1)  # Score out of 10

def summarize_comparisons(ranked_results):
    top_candidate = ranked_results[0]
    top_score = top_candidate["result"]["TotalScore"]

    print("\n✨ Candidate Summaries with Explanations:")
    for rank, entry in enumerate(ranked_results, start=1):
        name = entry["name"]
        result = entry["result"]
        score = result["TotalScore"]

        categories = [cat for cat in result if cat not in ("TotalScore", "Explanation")]

        # Classify categories
        strong_areas = []
        weak_areas = []
        detailed_matches = []

        for cat in categories:
            score_cat = result[cat]["Score"]
            matched = result[cat]["Matched Keywords"]

            if score_cat >= 5:
                strong_areas.append(cat)
                if matched:
                    detailed_matches.append(f"{cat} (matched: {', '.join(matched)})")
            elif score_cat == 0:
                weak_areas.append(cat)

        # Compose explanation
        paragraph = f"{name} scored {score}. "

        if detailed_matches:
            paragraph += f"The candidate performed well in areas such as {', '.join(detailed_matches)}. "

        if weak_areas:
            paragraph += f"However, there were no matches found in {', '.join(weak_areas)}, which significantly impacted the score. "

        if not detailed_matches:
            paragraph += "The resume had very few relevant keyword matches across all sections. "

        paragraph += (
            "To improve, the candidate should focus on gaining practical experience, listing personal or academic projects, obtaining relevant certifications, "
            "and highlighting more specific skills that align with the job requirements."
        )

        # Print summary
        print(f"\n{rank}. {name} ➤ Score: {score}")
        print(f"   Summary: {paragraph}")

        if rank == 1:
            print("   🏅 This candidate is the top performer.")
        else:
            diff = round(top_score - score, 1)
            print(f"   ⚠ Missing {diff} points compared to top candidate ({top_candidate['name']})")

# # 🏃️ Main Execution
if __name__ == "__main__":
    # Load job_criteria from file
    with open("job_criteria.json", "r") as f:
        job_criteria = json.load(f)

    folder_id = 26  # Set your actual folder_id here

    ranked_results = match_and_rank_resumes(job_criteria, folder_id)
    print(ranked_results)
    summarize_comparisons(ranked_results)
