import google.generativeai as genai
from .secrets import GEMINI_API_KEY

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def init_llm():
    """Initialize the Gemini model"""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        return model
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return None

def analyze_answer(question, answer, programs):
    """Analyze answers and match with programs using Gemini"""
    model = init_llm()
    if not model:
        return "Error: Could not initialize Gemini model."
    
    # Format programs list
    programs_text = "\n".join([
        f"- {p.title}: {p.summary if p.summary else 'No description available'}"
        for p in programs
    ])
    
    prompt = f"""
    You are a career counselor analyzing a student's responses to recommend educational programs.
    
    Student's Assessment Responses:
    {answer}

    Available Educational Programs:
    {programs_text}

    Task: Based on the student's answers, create a detailed analysis following this EXACT format:

    Profile Analysis:
    - Primary Interests: [Technology/Creative/Business/Communication]
    - Technical Aptitude: [High/Medium/Low]
    - Communication Skills: [Strong/Moderate/Developing]
    - Learning Preference: [Hands-on/Theoretical/Mixed]
    - Career Direction: [Brief one-line description]

    Program Recommendations:

    Most Suitable (Top matches):
    [List  programs that best align with the student's profile, considering their interests and aptitudes]

    Suitable (Next best options):
    [List programs that somewhat match their interests and could be good secondary choices]

    Less Suitable (Not recommended):
    [List remaining programs that don't align well with the student's profile]

    Rules:
    1. Use ONLY programs from the provided list
    2. Each program must appear exactly once
    3. Base recommendations strictly on the student's answers
    4. Consider both stated preferences and implied skills
    5. Focus on matching programs to student's demonstrated interests and abilities
    6. Ensure recommendations align with their career goals and learning style
    7. Don't use ** (make a text bold)
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            ),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        )
        
        response_text = response.text.strip()
        if "Profile Analysis:" not in response_text or "Program Recommendations:" not in response_text:
            print(f"Invalid response format: {response_text}")
            program_list = list(programs)
            return (
                "Profile Analysis:\n"
                "- Primary Interests: Technology\n"
                "- Technical Aptitude: Medium\n"
                "- Communication Skills: Moderate\n"
                "- Learning Preference: Mixed\n"
                "- Career Direction: Exploring technical and creative fields\n\n"
                "Program Recommendations:\n\n"
                f"Most Suitable (Top matches):\n"
                f"{program_list[0].title if len(program_list) > 0 else ''}\n"
                f"{program_list[1].title if len(program_list) > 1 else ''}\n"
                f"{program_list[2].title if len(program_list) > 2 else ''}\n\n"
                f"Suitable (Next best options):\n"
                f"{', '.join(p.title for p in program_list[3:7] if len(program_list) > 3)}\n\n"
                f"Less Suitable (Not recommended):\n"
                f"{', '.join(p.title for p in program_list[7:])}"
            )
        
        return response_text
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Error analyzing programs. Please try again." 