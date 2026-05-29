"""
Legal Research Assistant - Hugging Face Deployment
Powered by Google Gemini AI
"""

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

import google.generativeai as genai
import gradio as gr

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("⚠️ Please set GEMINI_API_KEY in Space Settings → Repository secrets")

genai.configure(api_key=GEMINI_API_KEY)

# List available models and use the first one that works
def get_available_model():
    """Get the first available Gemini model."""
    try:
        # Try different model names
        model_names = [
            'models/gemini-pro',
            'gemini-pro',
            'models/gemini-1.0-pro',
            'gemini-1.0-pro'
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Test if it works
                test_response = model.generate_content("Hi")
                print(f"✅ Successfully using model: {model_name}")
                return model
            except Exception as e:
                print(f"❌ Model {model_name} failed: {str(e)}")
                continue
        
        # If all fail, list available models
        print("Listing available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Available: {m.name}")
                return genai.GenerativeModel(m.name)
        
        raise Exception("No suitable model found")
        
    except Exception as e:
        raise Exception(f"Failed to initialize model: {str(e)}")

# Initialize model
model = get_available_model()

# Legal knowledge base
LEGAL_KNOWLEDGE = """
TENANT RIGHTS:
- Tenants have the right to a habitable living space
- Landlords must maintain the property in good condition
- Landlords typically must provide 24-48 hours notice before entering
- Tenants cannot be evicted without proper legal notice (usually 30-60 days)
- Security deposits must be returned within a specified time (varies by state)
CONTRACT LAW:
- A valid contract requires: offer, acceptance, and consideration
- All parties must have legal capacity to contract
- Contracts must be for a legal purpose
- Written contracts are required for certain agreements (Statute of Frauds)
- Breach of contract may result in damages or specific performance
EMPLOYMENT LAW:
- Discrimination based on race, color, religion, sex, or national origin is illegal
- Employees have the right to a safe workplace
- Minimum wage and overtime laws apply to most workers
- Wrongful termination may be grounds for legal action
- Whistleblower protections exist for reporting illegal activities
CRIMINAL VS CIVIL LAW:
- Criminal law: Government prosecutes crimes, penalties include jail/fines
- Civil law: Private disputes between parties, remedies are typically monetary
- Burden of proof: "Beyond reasonable doubt" (criminal) vs "Preponderance of evidence" (civil)
SMALL CLAIMS COURT:
- Handles disputes involving smaller amounts (typically under $5,000-$10,000)
- Simplified procedures, lawyers often not required
- Faster resolution than regular court
- Limited appeal options
FAMILY LAW:
- Divorce requires legal grounds (varies by state)
- Child custody determined by "best interests of the child"
- Child support obligations based on income and custody arrangement
- Prenuptial agreements can protect assets in divorce
CONSUMER RIGHTS:
- Right to accurate product information
- Protection against false advertising
- Right to refunds for defective products
- Protection against unfair debt collection practices
"""

def legal_research_assistant(question: str) -> str:
    """Answer legal questions using Gemini with embedded knowledge."""
    
    if not question.strip():
        return "⚠️ Please enter a legal question."
    
    prompt = f"""You are a professional legal research assistant. Answer the following question using the provided legal information.
LEGAL KNOWLEDGE BASE:
{LEGAL_KNOWLEDGE}
USER QUESTION: {question}
INSTRUCTIONS:
- Provide a clear, accurate answer based on the legal knowledge provided
- Use professional but accessible language
- If the question is outside the scope of the provided information, say so and provide general guidance
- Always include this disclaimer at the end: "⚠️ This is for informational purposes only and does not constitute legal advice. Please consult with a qualified attorney for your specific situation."
ANSWER:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            return "⚠️ API Key Error: Please verify your GEMINI_API_KEY is correct in Space Settings → Repository secrets.\n\nMake sure you're using a valid Gemini API key from https://makersuite.google.com/app/apikey"
        elif "404" in error_msg or "not found" in error_msg.lower():
            return f"⚠️ Model Error: The Gemini model is not accessible.\n\nError details: {error_msg}\n\nPlease check:\n1. Your API key is valid\n2. Your API key has access to Gemini models\n3. Try generating a new API key"
        else:
            return f"⚠️ Error: {error_msg}\n\nPlease try again or contact support."

# Create Gradio interface
demo = gr.Interface(
    fn=legal_research_assistant,
    inputs=[
        gr.Textbox(
            label="💬 Ask Your Legal Question",
            placeholder="Example: What are my rights as a tenant?",
            lines=3
        )
    ],
    outputs=[
        gr.Textbox(
            label="📝 Answer",
            lines=12
        )
    ],
    title="⚖️ Legal Research Assistant",
    description="""
    Get AI-powered answers to common legal questions.
    
    **Powered by:** Google Gemini AI
    
    **Topics covered:** Tenant rights, contracts, employment law, criminal vs civil law, family law, consumer rights, and more.
    
    **⚠️ Important:** This tool provides general information only and does not constitute legal advice. 
    Always consult with a qualified attorney for your specific legal situation.
    """,
    examples=[
        ["What are the basic rights of a tenant?"],
        ["What makes a contract legally valid?"],
        ["What should I do if I face workplace discrimination?"],
        ["Can my landlord evict me without notice?"],
        ["What's the difference between civil and criminal law?"],
        ["How does small claims court work?"],
        ["What are my consumer rights when buying products?"],
    ],
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    print("✅ Legal Research Assistant is ready!")
    demo.launch()
