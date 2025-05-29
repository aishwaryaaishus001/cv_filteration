# sk-proj-LKiobmLKGtcGLo0H1W7VT3BlbkFJQ5KnD6qYP4h8zWNGNAxc

import os
import pdfplumber
from docling.document_converter import DocumentConverter
from jd_generator1 import main_gpt


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
    

# # 🔹 Extract text from PDF
# def extract_text_from_pdf(pdf_path):
#     text = ""
#     if not os.path.exists(pdf_path):
#         print(f"❌ Error: File '{pdf_path}' not found.")
#         return None
    
#     try:
#         with pdfplumber.open(pdf_path) as pdf:
#             for page in pdf.pages:
#                 extracted_text = page.extract_text()
#                 if extracted_text:
#                     text += extracted_text + "\n"
#         print("Text:", text)

#         return text.strip()
#     except Exception as e:
#         print(f"❌ Error reading PDF: {e}")
#         return None

# 🔹 Wrap extracted text in a dictionary
def convert_text_to_object(text):
    return {
        "content": text
    }

# 🔍 Search for multiple keywords in the content
def search_keywords(content_object, keywords):
    content = content_object.get("content", "").lower()
    found = [keyword for keyword in keywords if keyword.lower() in content]
    return found

# ⭐ Rank the match by percentage and convert to score out of 10
def calculate_rank(total_keywords, matched_keywords):
    if total_keywords == 0:
        return 0
    percentage = (len(matched_keywords) / total_keywords) * 100
    score = round((percentage / 10), 1)
    return score



#     all_results = []

#     for filename in os.listdir(folder_path):
#         if filename.endswith(".pdf"):
#             file_path = os.path.join(folder_path, filename)
#             resume_text = extract_text_from_pdf(file_path)

#             if resume_text:
#                 result_object = convert_text_to_object(resume_text)
#                 final_result = {}
#                 total_score = 0

#                 for category, keywords in keywords_to_search.items():
#                     matched_keywords = search_keywords(result_object, keywords)
#                     score = calculate_rank(len(keywords), matched_keywords)
#                     total_score += score

#                     final_result[category] = {
#                         "Score": score,
#                         "Matched Keywords": matched_keywords
#                     }

#                 final_result["TotalScore"] = round(total_score, 1)
#                 all_results.append({
#                     "filename": filename,
#                     "result": final_result
#                 })

#                 print(f"\n📄 Processed: {filename}")
#             else:
#                 print(f"❌ Skipped (no content): {filename}")

#     # 📊 Sort PDFs by total score in descending order
#     ranked_results = sorted(all_results, key=lambda x: x["result"]["TotalScore"], reverse=True)

#     # 🧾 Show Final Ranked Output
#     print("\n🏆 Final Ranked Results:")
#     for rank, entry in enumerate(ranked_results, start=1):
#         print(f"\n{rank}. {entry['filename']} ➤ Score: {entry['result']['TotalScore']}")
#         print(entry["result"])


# 🔹 Main Execution
if __name__ == "__main__":
    folder_path = r"D:\deepseek\sampleCVs"


    job_description = """
     looking for a bank manager with 2+ years of experience in financial services.
    """

    job_criteria = main_gpt(job_description)

    keywords_to_search = job_criteria
    
    all_results = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            resume_text = extract_text_docling(file_path)

            if resume_text:
                result_object = convert_text_to_object(resume_text)
                final_result = {}
                total_score = 0

                for category, keywords in keywords_to_search.items():
                    matched_keywords = search_keywords(result_object, keywords)
                    score = calculate_rank(len(keywords), matched_keywords)
                    total_score += score

                    final_result[category] = {
                        "Score": score,
                        "Matched Keywords": matched_keywords
                    }

                final_result["TotalScore"] = round(total_score, 1)
                all_results.append({
                    "filename": filename,
                    "result": final_result
                })

                print(f"\n📄 Processed: {filename}")
            else:
                print(f"❌ Skipped (no content): {filename}")

    # 📊 Sort PDFs by total score in descending order
    ranked_results = sorted(all_results, key=lambda x: x["result"]["TotalScore"], reverse=True)

    # 🧾 Show Final Ranked Output
    print("\n🏆 Final Ranked Results:")
    for rank, entry in enumerate(ranked_results, start=1):
        print(f"\n{rank}. {entry['filename']} ➤ Score: {entry['result']['TotalScore']}")
        print(entry["result"])
