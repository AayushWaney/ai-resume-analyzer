import pdfplumber
import re
import html
from sentence_transformers import SentenceTransformer, util

# --- Global Performance Optimization ---
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')


# --- Categorized Databases ---
SKILL_CATEGORIES = {
    "Programming": ["python", "java", "c++", "c", "c#", "javascript", "typescript", "ruby", "php", "go", "rust", "swift", "kotlin", "r", "bash", "powershell"],
    "Frameworks & Web": ["html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "spring boot", "bootstrap", "tailwind", "api", "rest", "graphql", "microservices"],
    "Data & AI": ["machine learning", "data analysis", "artificial intelligence", "nlp", "deep learning", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "matlab", "tableau", "power bi", "excel", "data visualization"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd", "terraform", "linux"],
    "Databases": ["sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "nosql", "redis", "cassandra", "elasticsearch"],
    "Security & IT": ["cybersecurity", "network administration", "active directory", "troubleshooting", "information security", "system administration", "tcp/ip", "dns"],
    "Methodology & Soft Skills": ["agile", "scrum", "project management", "communication", "leadership", "problem solving", "teamwork", "time management", "critical thinking", "kanban", "sdlc"],
    "Business & Support": ["crm", "sla management", "ticketing systems", "zoom", "slack", "ms teams", "customer retention", "conflict management", "virtual assistance", "customer support", "salesforce", "zendesk", "b2b sales"],
    "Marketing & Content": ["seo", "sem", "content marketing", "digital marketing", "google analytics", "social media management", "email marketing", "copywriting", "branding", "hubspot", "market research"],
    "Core Engineering & Hardware": ["autocad", "solidworks", "plc", "manufacturing", "thermodynamics", "circuit design", "quality assurance", "cad/cam", "material science", "metallurgy", "supply chain", "logistics"]
}


LEARNING_PATHS = {
    "Python": "Complete a structured course like '100 Days of Code' to master the fundamentals.",
    "Sql": "Practice writing complex queries and joins on LeetCode or HackerRank.",
    "Aws": "Start studying for the AWS Certified Cloud Practitioner exam.",
    "Machine Learning": "Learn the basics of scikit-learn and build a linear regression model.",
    "Data Analysis": "Practice cleaning and visualizing datasets using Pandas and Tableau.",
    "Agile": "Read up on Scrum frameworks and sprint planning methodologies.",
    "Java": "Build a simple Object-Oriented application like a banking system.",
    "React": "Follow the official React documentation to build a tic-tac-toe game."
}


# --- Core Functions ---
def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        return extracted_text.strip()
    except Exception as e:
        return ""


def extract_skills_categorized(text):
    text_lower = text.lower()
    found_skills = {}

    for category, skills in SKILL_CATEGORIES.items():
        category_matches = set()
        for skill in skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                category_matches.add(skill.title())
        if category_matches:
            found_skills[category] = list(category_matches)

    return found_skills


def calculate_semantic_match(resume_text, jd_text):
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    resume_embedding = semantic_model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = semantic_model.encode(jd_text, convert_to_tensor=True)
    cosine_scores = util.cos_sim(resume_embedding, jd_embedding)
    return max(0.0, round(cosine_scores[0][0].item() * 100, 2))


def generate_heatmap_html(text, flat_skills_list):
    safe_text = html.escape(text)
    for skill in flat_skills_list:
        pattern = re.compile(r'\b(' + re.escape(skill) + r')\b', re.IGNORECASE)
        safe_text = pattern.sub(
            r'<mark style="background-color: #fef08a; padding: 2px 4px; border-radius: 4px; font-weight: 600; color: #0f172a;">\g<1></mark>',
            safe_text)
    return safe_text


def analyze_structure_and_impact(text):
    """
    Calculates multi-factor scores for the Radar Chart and generates feedback.
    """
    suggestions = []
    warnings = []
    text_lower = text.lower()

    # Base scores out of 100
    structure_score = 100
    impact_score = 100
    ats_formatting_score = 100

    # ATS Compatibility Checks
    if "table" in text_lower or "  " * 5 in text:  # Rudimentary check for columns/tables
        warnings.append("⚠️ Potential multi-column or table layout detected. This can break older ATS parsers.")
        ats_formatting_score -= 25

    # Structure Checks
    if not re.search(r'[•\-\*]', text):
        suggestions.append("Use bullet points. Break up large paragraphs so recruiters can scan easily.")
        structure_score -= 35

    # Impact & Quantified Results Checks
    if not re.search(r'\d', text) and not re.search(r'[%$]', text):
        suggestions.append("Add measurable achievements. Include quantified results (e.g., %, $, numbers).")
        impact_score -= 40

    action_verbs = ['managed', 'led', 'developed', 'created', 'increased', 'improved', 'designed', 'built', 'achieved',
                    'implemented', 'orchestrated']
    found_verbs = [verb for verb in action_verbs if verb in text_lower]

    if len(found_verbs) < 3:
        suggestions.append(
            "Missing strong action verbs. Start bullet points with words like 'Developed', 'Managed', or 'Achieved'.")
        impact_score -= 20

    if not suggestions:
        suggestions.append("✨ Great job! Your resume uses action verbs, quantified results, and clean formatting.")

    return {
        "suggestions": suggestions,
        "warnings": warnings,
        "scores": {
            "structure": max(10, structure_score),
            "impact": max(10, impact_score),
            "ats_optimization": max(10, ats_formatting_score)
        }
    }


# --- Master Engine ---
def run_full_analysis(resume_text, jd_text):
    # Get categorized skills
    resume_skills_dict = extract_skills_categorized(resume_text)
    jd_skills_dict = extract_skills_categorized(jd_text)

    # Flatten lists for cross-referencing and math
    flat_resume_skills = set(skill for category in resume_skills_dict.values() for skill in category)
    flat_jd_skills = set(skill for category in jd_skills_dict.values() for skill in category)

    matched_skills = flat_resume_skills.intersection(flat_jd_skills)
    missing_skills = flat_jd_skills.difference(flat_resume_skills)

    # Calculate Keyword Match Score mathematically
    keyword_score = int((len(matched_skills) / len(flat_jd_skills) * 100)) if flat_jd_skills else 100

    # Deep Learning Score
    semantic_score = calculate_semantic_match(resume_text, jd_text)

    # Structural & Impact Analysis
    structural_analysis = analyze_structure_and_impact(resume_text)

    # Generate Learning Path
    learning_suggestions = []
    for skill in missing_skills:
        path = LEARNING_PATHS.get(skill, f"Explore beginner tutorials and build a small project using {skill}.")
        learning_suggestions.append(f"{skill}: {path}")

    # Pack everything into the elite payload
    analysis_results = {
        "overall_score": semantic_score,  # The main big number
        "radar_scores": {
            "semantic_match": semantic_score,
            "keyword_match": keyword_score,
            "structure": structural_analysis["scores"]["structure"],
            "impact": structural_analysis["scores"]["impact"],
            "ats_compatibility": structural_analysis["scores"]["ats_optimization"]
        },
        "categorized_skills": resume_skills_dict,
        "flat_skills": {
            "matched": list(matched_skills),
            "missing": list(missing_skills)
        },
        "learning_path": learning_suggestions,
        "feedback": structural_analysis["suggestions"],
        "warnings": structural_analysis["warnings"],
        "heatmap_html": generate_heatmap_html(resume_text, list(flat_resume_skills))
    }

    return analysis_results