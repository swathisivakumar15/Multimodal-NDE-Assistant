# Overview

NDE AI Assistant is a Flask-based web application that provides specialized assistance for Non-Destructive Evaluation (NDE) professionals. The application combines AI-powered chat functionality with multiple file processing capabilities, external content integration, and speech recognition to create a comprehensive NDE knowledge platform. It serves as an expert assistant for engineering professionals working with various NDT methods including ultrasonic, radiographic, magnetic particle, and penetrant testing.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **HTML Templates**: Jinja2-based templating system with a base template structure for consistent UI
- **CSS Framework**: Custom CSS with blue gradient color palette and responsive design patterns
- **JavaScript Modules**: Modular approach with separate files for core app functionality (`app.js`) and speech recognition (`speech.js`)
- **Speech Integration**: Web Speech API implementation for hands-free operation in field environments
- **Real-time UI**: Interactive chat interface with sidebar navigation for NDE tools and methods

## Backend Architecture
- **Web Framework**: Flask application with SQLAlchemy ORM for database operations
- **Database Models**: Three core entities - ChatSession, ChatMessage, and UploadedFile with proper foreign key relationships
- **File Processing**: Multi-format file handler supporting PDF, images, and audio with corruption detection and hash validation
- **Modular Services**: Separate service modules for OpenAI integration, web scraping, YouTube search, and NDE knowledge base
- **Session Management**: UUID-based session tracking with persistent chat history

## Data Storage Solutions
- **Primary Database**: SQLite for development with PostgreSQL compatibility built-in
- **File Storage**: Local filesystem storage in uploads directory with configurable file size limits (50MB)
- **Session Persistence**: Database-backed chat sessions with message history tracking
- **File Integrity**: SHA-256 hash validation for uploaded files to detect corruption

## Authentication and Authorization
- **Session-based**: Flask sessions with configurable secret key from environment variables
- **File Access Control**: Session-scoped file uploads tied to individual chat sessions
- **No User Authentication**: Currently operates as a single-user application per session

## External Dependencies

### AI Services
- **OpenAI GPT-4o**: Primary AI model for NDE expertise and chat responses
- **OpenAI API**: Image analysis, generation, and audio transcription capabilities

### Third-party APIs
- **YouTube Data API**: Educational video search functionality filtered for NDE content
- **Web Scraping**: Trafilatura library for extracting technical content from NDE-related websites

### File Processing Libraries
- **PyPDF2**: PDF text extraction and processing
- **PyMuPDF (fitz)**: Advanced PDF manipulation and rendering
- **python-magic**: File type detection and MIME type validation
- **Werkzeug**: Secure filename handling and file utilities

### Database and ORM
- **SQLAlchemy**: ORM with DeclarativeBase for model definitions
- **Flask-SQLAlchemy**: Flask integration with connection pooling and engine options

### Development and Deployment
- **ProxyFix**: Werkzeug middleware for proper proxy header handling
- **Environment Variables**: Configuration management for API keys and database URLs
- **Logging**: Built-in Python logging for debugging and error tracking