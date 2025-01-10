from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

def init_llm():
    """Initialize the LLM model"""
    try:
        model_name = "facebook/opt-125m"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
    except Exception as e:
        print(f"Error loading primary model: {e}")
        model_name = "distilgpt2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0.7,
        device=-1
    )
    
    llm = HuggingFacePipeline(pipeline=pipe)
    return llm

def analyze_answer(question, answer, programs):
    """Analyze answers and match with programs"""
    llm = init_llm()
    
    template = """
    You are a career counselor analyzing a student's responses to a career assessment.

    Student's Career Assessment Responses:
    {answer}

    Available Academic Programs:
    {programs}

    Instructions:
    1. First, analyze the student's profile based on their answers:
       - Interest in technology/data: [High/Medium/Low]
       - Math/analytical skills: [High/Medium/Low]
       - People/communication focus: [High/Medium/Low]
       - Learning style: [Theoretical/Practical/Mixed]
       - Career goals alignment: [List relevant goals]

    2. Then categorize ALL programs based on how well they match the student's profile.
    
    Format your response EXACTLY like this:

    Profile Analysis:
    [Write 2-3 lines summarizing key traits from answers]

    Program Recommendations:
    Most Suitable: [Programs that match 80-100% of student traits]
    Suitable: [Programs that match 40-79% of student traits]
    Least Suitable: [Programs that match 0-39% of student traits]

    Remember:
    - EVERY program must be listed in exactly one category
    - Use ONLY the program titles from the list above
    - Consider ALL student answers in your analysis
    """
    
    # Format the available programs as a list with descriptions
    programs_text = "\n".join([
        f"- {p.title}: {p.summary if p.summary else 'No description available'}"
        for p in programs
    ])
    
    prompt = PromptTemplate(
        input_variables=["answer", "programs"],
        template=template
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True  # Enable this to see the full interaction
    )
    
    try:
        response = chain.run(
            answer=answer,
            programs=programs_text
        )
        
        # Clean up the response
        if not response.strip().startswith("Profile Analysis:"):
            program_list = list(programs)
            return (
                "Profile Analysis:\n"
                "Unable to generate detailed analysis.\n\n"
                "Program Recommendations:\n"
                f"Most Suitable: {program_list[0].title}\n"
                f"Suitable: {', '.join(p.title for p in program_list[1:-1])}\n"
                f"Least Suitable: {program_list[-1].title}"
            )
        
        return response
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Error analyzing programs. Please try again." 