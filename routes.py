import os
import uuid
import json
import logging
from flask import render_template, request, jsonify, session
from app import app, db
from models import ChatSession, ChatMessage, UploadedFile
from openai_service import (
    chat_with_nde_assistant,
    analyze_nde_image,
    generate_nde_image,
    transcribe_audio_file
)
from file_handler import handle_file_upload, validate_file_safety
from youtube_service import search_nde_videos, get_video_details
from web_scraper import scrape_nde_content
from nde_knowledge import get_nde_suggestions, search_nde_standards
import pyttsx3
import tempfile
import threading
from datetime import datetime

@app.route('/')
def index():
    """Main chat interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

        # Create new chat session in database
        chat_session = ChatSession()
        chat_session.session_id = session['session_id']
        db.session.add(chat_session)
        db.session.commit()

    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No active session'}), 400

        # Save user message to database
        user_message = ChatMessage()
        user_message.session_id = session_id
        user_message.message_type = 'user'
        user_message.content = message
        db.session.add(user_message)

        # Get AI response
        response = chat_with_nde_assistant(message)

        # Save assistant response to database
        assistant_message = ChatMessage()
        assistant_message.session_id = session_id
        assistant_message.message_type = 'assistant'
        assistant_message.content = response
        db.session.add(assistant_message)
        db.session.commit()

        return jsonify({
            'response': response,
            'status': 'success'
        })

    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Failed to process message. Please try again.'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads (PDF, images)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No active session'}), 400

        # Handle file upload and validation
        result = handle_file_upload(file, session_id)

        if result['status'] == 'error':
            return jsonify(result), 400

        # Process the file based on type
        file_path = result['file_path']
        file_type = result['file_type']

        if file_type.startswith('image/'):
            # Analyze image for NDE content
            analysis = analyze_nde_image(file_path)
            response = f"**Image Analysis Results:**\n\n{analysis}"
        elif file_type == 'application/pdf':
            # Extract and analyze PDF content
            from file_handler import extract_pdf_text
            text_content = extract_pdf_text(file_path)
            if text_content:
                response = chat_with_nde_assistant(
                    f"Please analyze this NDE technical document:\n\n{text_content[:4000]}"
                )
            else:
                response = "Unable to extract text from the PDF document. The file may be image-based or corrupted."
        else:
            response = f"File uploaded successfully: {result['filename']}"

        # Save the interaction to database
        message = ChatMessage()
        message.session_id = session_id
        message.message_type = 'assistant'
        message.content = response
        message.file_path = file_path
        db.session.add(message)
        db.session.commit()

        return jsonify({
            'response': response,
            'filename': result['filename'],
            'file_type': file_type,
            'status': 'success'
        })

    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Failed to process file upload. Please try again.'}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate NDE-related images using DALL-E"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400

        # Enhance prompt for NDE context
        nde_prompt = f"Professional technical diagram for Non-Destructive Evaluation (NDE): {prompt}. High-quality technical illustration style, clean lines, professional appearance suitable for engineering documentation."

        result = generate_nde_image(nde_prompt)

        session_id = session.get('session_id')
        if session_id:
            # Save the interaction
            message = ChatMessage()
            message.session_id = session_id
            message.message_type = 'assistant'
            message.content = f"Generated NDE image: {prompt}"
            db.session.add(message)
            db.session.commit()

        return jsonify({
            'image_url': result['url'],
            'status': 'success'
        })

    except Exception as e:
        logging.error(f"Image generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate image. Please try again.'}), 500

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio to text"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400

        # Save audio file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_audio_{uuid.uuid4()}.wav")
        audio_file.save(temp_path)

        try:
            # Transcribe audio
            transcription = transcribe_audio_file(temp_path)

            # Save user message to database
            session_id = session.get('session_id')
            if session_id:
                user_message = ChatMessage()
                user_message.session_id = session_id
                user_message.message_type = 'user'
                user_message.content = transcription
                db.session.add(user_message)
                db.session.commit()

            return jsonify({
                'transcription': transcription,
                'status': 'success'
            })
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logging.error(f"Transcription error: {str(e)}")
        return jsonify({'error': 'Failed to transcribe audio. Please try again.'}), 500

@app.route('/api/youtube-search', methods=['POST'])
def youtube_search():
    """Search YouTube for NDE educational videos"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({
                'status': 'error',
                'error': 'Search query is required'
            }), 400

        # Add NDE context to search
        nde_query = f"{query} NDE NDT non-destructive testing inspection"

        videos = search_nde_videos(nde_query)

        return jsonify({
            'status': 'success',
            'videos': videos
        })

    except Exception as e:
        logging.error(f"YouTube search error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to search videos. Please try again.'
        }), 500

@app.route('/api/speak', methods=['POST'])
def text_to_speech():
    """Convert text to speech using pyttsx3"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({
                'status': 'error',
                'error': 'Text is required for speech synthesis'
            }), 400

        # Create temporary file for audio
        temp_dir = tempfile.gettempdir()
        audio_filename = f"tts_{uuid.uuid4().hex}_{int(datetime.now().timestamp())}.wav"
        audio_path = os.path.join(temp_dir, audio_filename)

        def generate_speech():
            try:
                # Initialize TTS engine
                engine = pyttsx3.init()

                # Configure voice settings
                voices = engine.getProperty('voices')
                if voices:
                    # Try to set a female voice for better clarity
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break

                # Set speech rate and volume
                engine.setProperty('rate', 160)  # Slower for technical content
                engine.setProperty('volume', 0.9)

                # Clean text for better pronunciation
                clean_text = clean_text_for_speech(text)

                # Save to file
                engine.save_to_file(clean_text, audio_path)
                engine.runAndWait()

            except Exception as e:
                logging.error(f"TTS generation error: {str(e)}")

        # Generate speech in thread to avoid blocking
        speech_thread = threading.Thread(target=generate_speech)
        speech_thread.start()
        speech_thread.join(timeout=10)  # 10 second timeout

        if os.path.exists(audio_path):
            # Create URL for audio file
            audio_url = f"/api/audio/{audio_filename}"

            return jsonify({
                'status': 'success',
                'audio_url': audio_url,
                'message': 'Speech generated successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to generate speech file'
            }), 500

    except Exception as e:
        logging.error(f"TTS error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Text-to-speech service unavailable'
        }), 500

@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, filename)

        if os.path.exists(audio_path) and filename.startswith('tts_'):
            return send_file(audio_path, mimetype='audio/wav')
        else:
            return jsonify({'error': 'Audio file not found'}), 404

    except Exception as e:
        logging.error(f"Audio serve error: {str(e)}")
        return jsonify({'error': 'Failed to serve audio'}), 500

def clean_text_for_speech(text):
    """Clean text for better speech synthesis"""
    # Remove markdown formatting
    text = text.replace('**', '').replace('*', '').replace('`', '')
    text = text.replace('#', '').replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')

    # Handle NDE abbreviations
    text = text.replace('NDE', 'N D E')
    text = text.replace('NDT', 'N D T')
    text = text.replace('UT', 'U T')
    text = text.replace('RT', 'R T')
    text = text.replace('MT', 'M T')
    text = text.replace('PT', 'P T')
    text = text.replace('ET', 'E T')
    text = text.replace('VT', 'V T')
    text = text.replace('ASME', 'A S M E')
    text = text.replace('ASTM', 'A S T M')
    text = text.replace('AWS', 'A W S')
    text = text.replace('API', 'A P I')

    # Handle units
    text = text.replace('mm', 'millimeters')
    text = text.replace('cm', 'centimeters')
    text = text.replace('MHz', 'megahertz')
    text = text.replace('kHz', 'kilohertz')
    text = text.replace('dB', 'decibels')

    return text

@app.route('/api/scrape-content', methods=['POST'])
def scrape_content():
    """Scrape and process web content"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()

        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400

        # Scrape and process content
        result = scrape_nde_content(url)

        session_id = session.get('session_id')
        if session_id and result['status'] == 'success':
            # Save the interaction
            message = ChatMessage()
            message.session_id = session_id
            message.message_type = 'assistant'
            message.content = result['content']
            db.session.add(message)
            db.session.commit()

        return jsonify(result)

    except Exception as e:
        logging.error(f"Content scraping error: {str(e)}")
        return jsonify({'error': 'Failed to scrape content. Please try again.'}), 500

@app.route('/api/nde-suggestions', methods=['GET'])
def nde_suggestions():
    """Get NDE expert suggestions"""
    try:
        suggestions = get_nde_suggestions()
        return jsonify({
            'suggestions': suggestions,
            'status': 'success'
        })

    except Exception as e:
        logging.error(f"NDE suggestions error: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions. Please try again.'}), 500

@app.route('/api/search-standards', methods=['POST'])
def search_standards():
    """Search NDE standards and documentation"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Search query cannot be empty'}), 400

        results = search_nde_standards(query)

        return jsonify({
            'results': results,
            'status': 'success'
        })

    except Exception as e:
        logging.error(f"Standards search error: {str(e)}")
        return jsonify({'error': 'Failed to search standards. Please try again.'}), 500

@app.route('/api/delete-message/<int:message_id>', methods=['DELETE'])
def delete_chat_message(message_id):
    """Delete a specific chat message"""
    try:
        message = ChatMessage.query.get(message_id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404

        # Optional: Add ownership check if users can only delete their own messages
        # if message.session_id != session.get('session_id'):
        #     return jsonify({'error': 'Unauthorized to delete this message'}), 403

        db.session.delete(message)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Message deleted successfully'})

    except Exception as e:
        logging.error(f"Delete message error: {str(e)}")
        db.session.rollback() # Rollback in case of error
        return jsonify({'error': 'Failed to delete message. Please try again.'}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    logging.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'An internal error occurred. Please try again.'}), 500