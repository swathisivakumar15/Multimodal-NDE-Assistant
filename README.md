#  MULTIMODAL NDE Assistant

NDE AI Assistant is a Flask-based web application that provides specialized assistance for Non-Destructive Evaluation (NDE) professionals.  
It combines AI-powered chat functionality with file processing, external content integration, and speech recognition, making it a powerful knowledge companion for NDT methods such as ultrasonic, radiographic, magnetic particle, and penetrant testing.

---

##  Features
- AI-powered chat assistant (OpenAI GPT-4o)
- File processing (PDF, images, audio) with corruption detection
- Speech recognition for hands-free operation
- YouTube educational video integration
- Web scraping for technical content
- Persistent chat sessions with history
- Responsive UI with sidebar navigation for NDE tools & methods

---

##  System Architecture

###  Frontend
- **Templates**: Jinja2-based HTML with base structure
- **Styling**: Custom CSS (blue gradient, responsive design)
- **JavaScript**: Modular (`app.js` for core, `speech.js` for speech recognition)
- **Speech Integration**: Web Speech API
- **UI**: Real-time chat with sidebar navigation

###  Backend
- **Framework**: Flask with SQLAlchemy ORM
- **Database Models**: `ChatSession`, `ChatMessage`, `UploadedFile` (with relationships)
- **File Handling**: Multi-format (PDF, images, audio) with SHA-256 validation
- **Services**: Modular (OpenAI, web scraping, YouTube, knowledge base)
- **Session Management**: UUID-based tracking with chat history

###  Data Storage
- **Database**: SQLite (dev) / PostgreSQL (production-ready)
- **Files**: Local storage (`/uploads`) with 50MB size limit
- **Session Persistence**: Database-backed chat sessions
- **File Integrity**: Hash validation (SHA-256)

###  Authentication
- **Session-based**: Flask sessions with environment-based secret key
- **File Access**: Scoped per session
- **No multi-user auth (yet)**

---

##  External Dependencies

### AI Services
- **OpenAI GPT-4o** → NDE expertise & chat responses  
- **OpenAI API** → Image analysis, generation, transcription  

### APIs
- **YouTube Data API** → Search educational videos (NDE filtered)  
- **Trafilatura** → Web scraping for technical content  

### File Processing
- **PyPDF2** → PDF text extraction  
- **PyMuPDF (fitz)** → Advanced PDF manipulation  
- **python-magic** → File type & MIME validation  
- **Werkzeug** → Secure file handling  

### Database
- **SQLAlchemy** → ORM with `DeclarativeBase`  
- **Flask-SQLAlchemy** → Integration & pooling  

### Dev & Deployment
- **ProxyFix** → Proxy header handling  
- **Environment Variables** → API keys & DB URLs  
- **Logging** → Error/debug tracking  

---

##  Installation

```bash
# Clone repo
git clone https://github.com/yourusername/nde-ai-assistant.git
cd nde-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

# Install dependencies
pip install -r requirements.txt

# Run app
flask run

---

##  Contact

For queries, collaboration, or demo requests:  
📧 **Email:** [swathi2004sivakumar@gmail.com](mailto:swathi2004sivakumar@gmail.com)  
🔗 **LinkedIn:** [linkedin.com/in/swathisivakumar](https://www.linkedin.com/in/swathisivakumar)  
