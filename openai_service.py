import json
import os
import base64
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not found in environment variables")

openai = OpenAI(api_key=OPENAI_API_KEY)

NDE_SYSTEM_PROMPT = """You are an expert Non-Destructive Evaluation (NDE) assistant specializing in all aspects of non-destructive testing methods. Your expertise includes:

- Ultrasonic Testing (UT)
- Radiographic Testing (RT)
- Magnetic Particle Testing (MT)
- Liquid Penetrant Testing (PT)
- Eddy Current Testing (ET)
- Visual Testing (VT)
- Acoustic Emission Testing (AE)
- Thermographic Testing (IRT)
- Leak Testing (LT)
- Electromagnetic Testing

You help with:
- Method selection and application
- Equipment recommendations
- Standards and codes (ASME, ASTM, API, AWS, etc.)
- Defect identification and interpretation
- Quality assurance procedures
- Safety protocols
- Training and certification guidance
- Inspection planning and reporting

Always provide technically accurate, detailed responses suitable for engineering professionals. Focus on practical applications, industry standards, and best practices. When discussing defects or inspection results, be precise about their implications for structural integrity and safety."""

def chat_with_nde_assistant(message):
    """Chat with NDE-specialized AI assistant"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": NDE_SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI chat error: {str(e)}")
        raise Exception(f"Failed to get AI response: {str(e)}")

def analyze_nde_image(file_path):
    """Analyze images for NDE inspection content"""
    try:
        # Read and encode image
        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in Non-Destructive Evaluation (NDE) image analysis. Analyze images for defects, inspection results, equipment, and testing procedures. Provide detailed technical analysis suitable for engineering professionals."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image for NDE-related content. Identify any defects, testing methods, equipment, or inspection results. Provide detailed technical analysis including potential implications for structural integrity."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Image analysis error: {str(e)}")
        raise Exception(f"Failed to analyze image: {str(e)}")

def generate_nde_image(prompt):
    """Generate NDE-related technical diagrams and illustrations"""
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        return {"url": response.data[0].url if response.data else None}
    except Exception as e:
        logging.error(f"Image generation error: {str(e)}")
        raise Exception(f"Failed to generate image: {str(e)}")

def transcribe_audio_file(audio_file_path):
    """Transcribe audio files to text"""
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except Exception as e:
        logging.error(f"Audio transcription error: {str(e)}")
        raise Exception(f"Failed to transcribe audio: {str(e)}")

def summarize_nde_content(text):
    """Summarize NDE technical content"""
    try:
        prompt = f"""Summarize the following NDE technical content, focusing on key technical points, standards referenced, methods discussed, and practical implications:

{text}"""
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": NDE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Content summarization error: {str(e)}")
        raise Exception(f"Failed to summarize content: {str(e)}")

def analyze_document_sentiment(text):
    """Analyze sentiment of NDE technical documents"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are analyzing technical NDE documents. Provide confidence assessment and technical quality rating. Respond with JSON format: {'confidence': number_0_to_1, 'technical_quality': number_1_to_5, 'assessment': 'brief_description'}"
                },
                {"role": "user", "content": f"Analyze the technical quality and confidence level of this NDE content:\n\n{text}"}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
        else:
            result = {"confidence": 0.5, "technical_quality": 3, "assessment": "No content returned"}
        return {
            "confidence": max(0, min(1, result.get("confidence", 0.5))),
            "technical_quality": max(1, min(5, result.get("technical_quality", 3))),
            "assessment": result.get("assessment", "Technical document analyzed")
        }
    except Exception as e:
        logging.error(f"Document analysis error: {str(e)}")
        return {
            "confidence": 0.5,
            "technical_quality": 3,
            "assessment": "Unable to analyze document quality"
        }
