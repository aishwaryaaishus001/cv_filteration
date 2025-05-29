import mysql.connector
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from collections import defaultdict
from difflib import SequenceMatcher

db = mysql.connector.connect(
    host="localhost",
    port=3308,
    user="root",
    password="CVanalysis@123",
    database="resumes"

)
cursor = db.cursor()

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Abbreviation mapping
abbreviation_map = {
    "mca": "master of computer applications",
    "masters of computer applications": "master of computer applications",
    "masters in computer application": "master of computer applications",
    "master of computer application": "master of computer applications",
    "bca": "bachelor of computer applications",
    "bsc": "bachelor of science",
    "bsc computer science": "bachelor of science in computer science",
    "bsc. computer science": "bachelor of science in computer science",
    "sslc": "secondary school leaving certificate",
    "plus 2": "higher secondary education",
    "plus-two": "higher secondary education"
}

# Normalize terms
def normalize(text):
    if not text:
        return ""
    text = text.lower().replace('.', '').replace('-', ' ').strip()
    for abbr, full_form in abbreviation_map.items():
        if abbr in text:
            text = text.replace(abbr, full_form)
    return text

# Fetch distinct degrees
cursor.execute("SELECT DISTINCT degree FROM education")
education_terms_raw = [row[0] for row in cursor.fetchall() if row[0]]

if not education_terms_raw:
    print("⚠️ No education terms found.")
    exit()

# Normalize and deduplicate terms for clustering
normalized_map = {term: normalize(term) for term in education_terms_raw}
unique_normalized_terms = list(set(normalized_map.values()))
embedding_vectors = model.encode(unique_normalized_terms)
distance_matrix = cosine_distances(embedding_vectors)

# Clustering
clustering = AgglomerativeClustering(
    n_clusters=None,
    distance_threshold=0.2,
    metric="precomputed",
    linkage="average"
)
clustering.fit(distance_matrix)

# Group cluster → normalized terms
cluster_to_normed = defaultdict(list)
for idx, label in enumerate(clustering.labels_):
    cluster_to_normed[label].append(unique_normalized_terms[idx])

# Fuzzy sub-cluster within cluster
def subcluster_similar_terms(cluster):
    result = []
    used = set()
    for i, base in enumerate(cluster):
        if base in used:
            continue
        group = [base]
        used.add(base)
        for j in range(i + 1, len(cluster)):
            candidate = cluster[j]
            if candidate not in used and SequenceMatcher(None, base, candidate).ratio() > 0.85:
                group.append(candidate)
                used.add(candidate)
        result.append(group)
    return result

# Final mapping from original → canonical
original_to_canonical = {}
cluster_id = 0

print("\n📚 Grouped Education Terms by Cluster:\n")
for cluster_terms in cluster_to_normed.values():
    for subcluster in subcluster_similar_terms(cluster_terms):
        canonical = max(subcluster, key=len)
        print(f"Cluster {cluster_id}: {canonical}")
        for norm_term in subcluster:
            # Map all raw terms pointing to this normalized one
            for original, mapped in normalized_map.items():
                if mapped == norm_term:
                    original_to_canonical[original] = canonical
                    print(f"  - {original}")
        print("-" * 50)
        cluster_id += 1

# Optional: Update database
def update_database():
    for original, canonical in original_to_canonical.items():
        cursor.execute("""
            UPDATE education_backup SET degree = %s WHERE degree = %s
        """, (canonical, original))
    db.commit()
    print("\n✅ Canonical degrees updated in education_backup.")

# Uncomment to apply updates
# update_database()
