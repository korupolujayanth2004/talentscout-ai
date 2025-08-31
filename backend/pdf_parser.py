import pymupdf as fitz
import re
from difflib import get_close_matches

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def parse_resume_text(text: str) -> dict:
    """Enhanced resume parsing with skill validation"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text_lower = text.lower()
    
    extracted = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "experience": ""
    }
    
    # Valid skills database for matching
    valid_skills = [
        'FastAPI', 'React', 'Next.js', 'Flask', 'MongoDB', 'Tailwind CSS', 
        'Machine Learning', 'Python', 'JavaScript', 'HTML', 'CSS', 'Node.js',
        'Docker', 'Kubernetes', 'AWS', 'Git', 'GitHub', 'TensorFlow', 'PyTorch',
        'Streamlit', 'Qdrant', 'LangChain', 'Gemini API', 'OpenAI', 'Gradio',
        'Pandas', 'NumPy', 'Scikit-learn', 'OpenCV', 'Django', 'Vue.js',
        'Angular', 'TypeScript', 'PostgreSQL', 'MySQL', 'Redis', 'GraphQL',
        'RESTful API', 'Microservices', 'CI/CD', 'Linux', 'Ubuntu', 'Nginx',
        'Apache', 'Jenkins', 'Terraform', 'Ansible', 'Elasticsearch'
    ]
    
    # Extract Email using regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        extracted["email"] = email_match.group()
    
    # Extract Phone using regex
    phone_pattern = r'\b(?:\+91|91)?[6-9]\d{9}\b'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        extracted["phone"] = phone_match.group()
    
    # Extract Name
    for i, line in enumerate(lines[:10]):
        skip_keywords = ['course', 'email', 'mobile', 'cgpa', 'academic', 'details']
        if any(keyword in line.lower() for keyword in skip_keywords):
            continue
        
        if re.match(r'^[A-Z][A-Z\s]+$', line) and len(line.split()) >= 2:
            extracted["name"] = line.title()
            break
    
    # Extract and clean skills
    raw_skills = []
    
    # Look for explicit skill mentions
    for skill in valid_skills:
        if skill.lower() in text_lower:
            raw_skills.append(skill)
    
    # Extract from common skill patterns
    skill_patterns = [
        r'built with (.*?)(?:\.|,|;|\n)',
        r'using (.*?)(?:\.|,|;|\n)',
        r'technologies?:?\s*(.*?)(?:\.|,|;|\n)',
        r'skills?:?\s*(.*?)(?:\.|,|;|\n)',
        r'stack:?\s*(.*?)(?:\.|,|;|\n)'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            # Split by common delimiters
            words = re.split(r'[,\.\sand\s&\s]+', match.strip())
            for word in words:
                word = word.strip()
                if len(word) > 2:
                    # Try to match with valid skills using fuzzy matching
                    close_matches = get_close_matches(word, valid_skills, n=1, cutoff=0.7)
                    if close_matches:
                        raw_skills.append(close_matches[0])
    
    # Remove duplicates and limit
    extracted["skills"] = list(set(raw_skills))[:12]
    
    # Extract Experience
    exp_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*:?\s*(\d+)\+?\s*years?'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted["experience"] = f"{match.group(1)} years"
            break
    
    if not extracted["experience"]:
        if 'intern' in text_lower and 'b.tech' in text_lower:
            extracted["experience"] = "0-1 years (Student/Intern)"
        else:
            extracted["experience"] = "Fresher"
    
    return extracted
