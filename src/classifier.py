import re

def categorize_job(title: str, description: str = "") -> str:
    """
    Analyzes the job title (and description) to determine the best resume to use.
    Returns one of: 'ai', 'ml', 'da', 'fullstack'
    """
    text = (title + " " + description).lower()
    
    # Keyword scoring
    scores = {
        "ai": len(re.findall(r'\b(ai|artificial intelligence|generative ai|nlp|llm)\b', text)),
        "ml": len(re.findall(r'\b(ml|machine learning|deep learning|computer vision)\b', text)),
        "da": len(re.findall(r'\b(data analyst|data analytics|sql|tableau|powerbi|power bi|data science)\b', text)),
        "fullstack": len(re.findall(r'\b(full stack|frontend|backend|sde|software engineer|react|node|django|spring)\b', text))
    }
    
    # Find the category with the highest score
    best_match = max(scores, key=scores.get)
    
    # Default to fullstack (SDE) if no specific keywords are found
    if scores[best_match] == 0:
        return "fullstack"
        
    return best_match

if __name__ == "__main__":
    # Test cases
    print("Test 1 (AI):", categorize_job("Generative AI Engineer"))
    print("Test 2 (DA):", categorize_job("Data Analyst Intern - SQL"))
    print("Test 3 (Fullstack):", categorize_job("Software Development Engineer I"))
