import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", None)  

# LLM Settings
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast and smart
GROQ_TEMPERATURE = 0.3  # Lower = more focused, higher = more creative

# Summary Detail Levels
SUMMARY_LEVELS = {
    "short": {
        "description": "2-3 sentences, quick overview",
        "max_tokens": 150
    },
    "medium": {
        "description": "1 paragraph with key findings",
        "max_tokens": 300
    },
    "long": {
        "description": "Detailed analysis with methodology and implications",
        "max_tokens": 600
    }
}

DEFAULT_SUMMARY_LEVEL = "medium"

LIT_REVIEW_DETAIL_LEVELS = {
    "short": {
        "description": "2-3 pages, concise overview",
        "target_words": 500
    },
    "medium": {
        "description": "5-10 pages, comprehensive analysis",
        "target_words": 2000
    },
    "long": {
        "description": "15-20 pages, thesis-ready depth",
        "target_words": 5000
    }
}

LIT_REVIEW_TYPES = ["thematic", "chronological", "methodological"]
DEFAULT_LIT_REVIEW_TYPE = "thematic"




# Cache Settings
CACHE_DIR = ".cache"
CACHE_EXPIRY_DAYS = 7  
ENABLE_CACHE = True
CACHE_EXPIRY_HOURS = CACHE_EXPIRY_DAYS * 24

# Search Settings
DEFAULT_PAPER_LIMIT = 10
MAX_PAPER_LIMIT = 50

# PDF Processing
PDF_TIMEOUT_SECONDS = 30
MAX_PDF_SIZE_MB = 50

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "research_agent.log"

# Render Deployment Settings
PORT = int(os.getenv("PORT", 8501))
