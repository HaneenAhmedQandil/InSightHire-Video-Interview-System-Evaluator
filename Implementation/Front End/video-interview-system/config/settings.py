# # # import os

# # # class Config:
# # #     # Base directories
# # #     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # #     SRC_DIR = os.path.join(BASE_DIR, "src")
# # #     MODELS_DIR = os.path.join(SRC_DIR, "models")
# # #     DATA_DIR = os.path.join(BASE_DIR, "data")
    
# # #     # Model paths
# # #     EMOTION_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.keras")
# # #     SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
# # #     ENCODER_PATH = os.path.join(MODELS_DIR, "encoder.pkl")
    
# # #     # Data directories
# # #     RECORDINGS_DIR = os.path.join(DATA_DIR, "recordings")
# # #     TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")
    
# # #     # Recording settings
# # #     RECORDING_DURATION = 60  # seconds
    
# # #     # Model settings
# # #     WHISPER_MODEL_NAME = "base"
    
# # #     # Interview questions
# # #     QUESTIONS = [
# # #         "Tell me about yourself and your background.",
# # #         "Why are you interested in this position?", 
# # #         "What are your greatest strengths?",
# # #         "Describe a challenging situation you faced and how you handled it.",
# # #         "Where do you see yourself in 5 years?"
# # #     ]
    
# # #     @classmethod
# # #     def create_directories(cls):
# # #         """Create necessary directories if they don't exist"""
# # #         directories = [cls.RECORDINGS_DIR, cls.TRANSCRIPTS_DIR, cls.MODELS_DIR]
        
# # #         for directory in directories:
# # #             try:
# # #                 # Check if path exists and is a file (not directory)
# # #                 if os.path.exists(directory) and os.path.isfile(directory):
# # #                     print(f"Warning: {directory} exists as a file, removing it...")
# # #                     os.remove(directory)
                
# # #                 # Create directory
# # #                 os.makedirs(directory, exist_ok=True)
# # #                 print(f"✅ Directory created/verified: {directory}")
                
# # #             except Exception as e:
# # #                 print(f"❌ Error creating directory {directory}: {e}")
# # #                 # Try alternative approach
# # #                 try:
# # #                     if not os.path.exists(directory):
# # #                         os.makedirs(directory)
# # #                 except Exception as e2:
# # #                     print(f"❌ Alternative approach also failed: {e2}")
    
# # #     @classmethod
# # #     def verify_model_files(cls):
# # #         """Verify that all required model files exist"""
# # #         required_files = [
# # #             cls.EMOTION_MODEL_PATH,
# # #             cls.SCALER_PATH,
# # #             cls.ENCODER_PATH
# # #         ]
        
# # #         missing_files = []
# # #         for file_path in required_files:
# # #             if not os.path.exists(file_path):
# # #                 missing_files.append(file_path)
        
# # #         if missing_files:
# # #             print("Missing model files:")
# # #             for file_path in missing_files:
# # #                 print(f"  - {file_path}")
# # #             return False
        
# # #         print("All model files found:")
# # #         for file_path in required_files:
# # #             print(f"  ✅ {file_path}")
# # #         return True


# # import os
# # from pathlib import Path

# # class Config:
# #     # Base directories
# #     BASE_DIR = Path(__file__).parent.parent
# #     DATA_DIR = BASE_DIR / "data"
# #     SRC_DIR = BASE_DIR / "src"
    
# #     # Model paths for emotion analysis


# #     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# #     SRC_DIR = os.path.join(BASE_DIR, "src")
# #     MODELS_DIR = os.path.join(SRC_DIR, "models")
# #     DATA_DIR = os.path.join(BASE_DIR, "data")
    
# #     # Model paths
# #     EMOTION_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.keras")
# #     SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
# #     ENCODER_PATH = os.path.join(MODELS_DIR, "encoder.pkl")
    
# #     # Audio/Video settings
# #     WHISPER_MODEL_NAME = "base"
# #     RECORDING_DURATION = 60  # seconds
    
# #     # Data directories
# #     RECORDINGS_DIR = DATA_DIR / "recordings"
# #     TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
# #     AUDIO_DIR = DATA_DIR / "audio"
# #     VIDEOS_DIR = DATA_DIR / "videos"
# #     RESULTS_DIR = DATA_DIR / "results"
# #     EVALUATION_DIR = DATA_DIR / "evaluation"
    
# #     # Evaluation data paths
# #     TECHNICAL_DIR = DATA_DIR / "Technical"
# #     HR_DIR = DATA_DIR / "HR"
    
# #     TECH_CSV_PATH = TECHNICAL_DIR / "dataset.csv"
# #     TECH_RUBRIC_PATH = TECHNICAL_DIR / "tech_rubric.json"
# #     TECH_OLD_RESULTS_PATH = TECHNICAL_DIR / "tech_evaluation_results.json"
    
# #     HR_CSV_PATH = HR_DIR / "interview_best_answers_samples.csv"
# #     HR_RUBRIC_PATH = HR_DIR / "hr_rubric.json"
# #     HR_OLD_RESULTS_PATH = HR_DIR / "hr_evaluation_results_with_samples.json"
    
# #     # Interview questions
# #     QUESTIONS = [
# #         "Explain how you would implement a Transformer-based Speech Emotion Recognition (SER) pipeline end-to-end, from raw audio input to predicted emotion labels.",
# #         "Given a large dataset of audio recordings, describe at least three feature-extraction techniques (e.g., Mel-spectrogram, log-Mel, MFCC) and discuss the pros and cons of each for a SER task.",
# #         "How does Retrieval-Augmented Generation (RAG) improve answer evaluation compared to using a vanilla LLM? Illustrate with a pseudo-code or high-level workflow.",
# #         "Suppose you have to fine-tune a pre-trained wav2vec 2.0 model on a new emotional‐speech dataset. Which steps would you follow (data preprocessing, training loop, hyperparameter tuning), and why?",
# #         "Tell me about a time you faced a conflict in a team. How did you resolve it?",
# #         "What are your greatest strengths and how do they apply to this role?",
# #         "Describe a situation when you had to adapt quickly to a significant change at work or in school. What did you learn?",
# #         "How do you handle constructive criticism? Give an example?"
# #     ]
    
# #     @staticmethod
# #     def create_directories():
# #         """Create necessary directories if they don't exist"""
# #         directories = [
# #             Config.DATA_DIR,
# #             Config.RECORDINGS_DIR,
# #             Config.TRANSCRIPTS_DIR,
# #             Config.AUDIO_DIR,
# #             Config.VIDEOS_DIR,
# #             Config.RESULTS_DIR,
# #             Config.EVALUATION_DIR,
# #             Config.TECHNICAL_DIR,
# #             Config.HR_DIR
# #         ]
        
# #         for directory in directories:
# #             directory.mkdir(parents=True, exist_ok=True)
    
# #     @staticmethod
# #     def verify_model_files():
# #         """Verify that required model files exist"""
# #         required_files = [
# #             Config.EMOTION_MODEL_PATH,
# #             Config.SCALER_PATH,
# #             Config.ENCODER_PATH
# #         ]
        
# #         return all(file.exists() for file in required_files)
    
# #     @staticmethod
# #     def verify_evaluation_files():
# #         """Verify that required evaluation files exist"""
# #         required_files = [
# #             Config.TECH_RUBRIC_PATH,
# #             Config.HR_RUBRIC_PATH,
# #             Config.TECH_CSV_PATH,
# #             Config.HR_CSV_PATH
# #         ]
        
# #         return all(file.exists() for file in required_files)

# import os
# from pathlib import Path

# class Config:
#     # ─── Compute project root (where “video-interview-system” lives) ─────────────
#     # settings.py is at: <…>/video-interview-system/src/config/settings.py
#     CONFIG_DIR   = Path(__file__).resolve().parent           # …/video-interview-system/src/config
#     SRC_DIR      = CONFIG_DIR.parent                          # …/video-interview-system/src
#     PROJECT_ROOT = SRC_DIR.parent                             # …/video-interview-system

#     # ─── Define “data” under PROJECT_ROOT ────────────────────────────────────────
#     DATA_DIR = PROJECT_ROOT / "data"

#     # ─── Define “models” under SRC_DIR ───────────────────────────────────────────
#     MODELS_DIR = SRC_DIR / "models"

#     # ─── Model paths (emotion analysis) ──────────────────────────────────────────
#     EMOTION_MODEL_PATH = MODELS_DIR / "best_model.keras"
#     SCALER_PATH        = MODELS_DIR / "scaler.pkl"
#     ENCODER_PATH       = MODELS_DIR / "encoder.pkl"

#     # ─── Audio/Video settings ────────────────────────────────────────────────────
#     WHISPER_MODEL_NAME = "base"
#     RECORDING_DURATION = 60  # seconds

#     # ─── Data subdirectories ─────────────────────────────────────────────────────
#     RECORDINGS_DIR   = DATA_DIR / "recordings"
#     TRANSCRIPTS_DIR  = DATA_DIR / "transcripts"
#     AUDIO_DIR        = DATA_DIR / "audio"
#     VIDEOS_DIR       = DATA_DIR / "videos"
#     RESULTS_DIR      = DATA_DIR / "results"
#     EVALUATION_DIR   = DATA_DIR / "evaluation"

#     # ─── Evaluation subdirectories ──────────────────────────────────────────────
#     TECHNICAL_DIR = EVALUATION_DIR / "Technical"
#     HR_DIR        = EVALUATION_DIR / "HR"

#     # ─── Paths under each evaluation folder ─────────────────────────────────────┐
#     TECH_CSV_PATH         = TECHNICAL_DIR / "dataset.csv"
#     TECH_RUBRIC_PATH      = TECHNICAL_DIR / "tech_rubric.json"
#     TECH_OLD_RESULTS_PATH = TECHNICAL_DIR / "tech_evaluation_results.json"

#     HR_CSV_PATH         = HR_DIR / "interview_best_answers_samples.csv"
#     HR_RUBRIC_PATH      = HR_DIR / "hr_rubric.json"
#     HR_OLD_RESULTS_PATH = HR_DIR / "hr_evaluation_results_with_samples.json"
#     # ─────────────────────────────────────────────────────────────────────────────┘

#     # ─── Hard-coded interview questions (example) ─────────────────────────────────
#     QUESTIONS = [
#         "Explain how you would implement a Transformer-based Speech Emotion Recognition (SER) pipeline end-to-end, from raw audio input to predicted emotion labels.",
#         "Given a large dataset of audio recordings, describe at least three feature-extraction techniques (e.g., Mel-spectrogram, log-Mel, MFCC) and discuss the pros and cons of each for a SER task.",
#         "How does Retrieval-Augmented Generation (RAG) improve answer evaluation compared to using a vanilla LLM? Illustrate with a pseudo-code or high-level workflow.",
#         "Suppose you have to fine-tune a pre-trained wav2vec 2.0 model on a new emotional‐speech dataset. Which steps would you follow (data preprocessing, training loop, hyperparameter tuning), and why?",
#         "Tell me about a time you faced a conflict in a team. How did you resolve it?",
#         "What are your greatest strengths and how do they apply to this role?",
#         "Describe a situation when you had to adapt quickly to a significant change at work or in school. What did you learn?",
#         "How do you handle constructive criticism? Give an example?"
#     ]

#     @staticmethod
#     def create_directories():
#         """Create necessary directories (if they don't exist) in one shot."""
#         folders = [
#             Config.DATA_DIR,
#             Config.RECORDINGS_DIR,
#             Config.TRANSCRIPTS_DIR,
#             Config.AUDIO_DIR,
#             Config.VIDEOS_DIR,
#             Config.RESULTS_DIR,
#             Config.EVALUATION_DIR,
#             Config.TECHNICAL_DIR,
#             Config.HR_DIR
#         ]
#         for folder in folders:
#             folder.mkdir(parents=True, exist_ok=True)

#     @staticmethod
#     def verify_model_files():
#         """Verify that required model files exist; returns True/False."""
#         required = [
#             Config.EMOTION_MODEL_PATH,
#             Config.SCALER_PATH,
#             Config.ENCODER_PATH
#         ]
#         missing = [p for p in required if not p.exists()]
#         if missing:
#             print("Missing model files:")
#             for p in missing:
#                 print(f"  - {p}")
#             return False

#         print("All model files found:")
#         for p in required:
#             print(f"  ✅ {p}")
#         return True

#     @staticmethod
#     def verify_evaluation_files():
#         """Verify that required evaluation files exist; returns True/False."""
#         required = [
#             Config.TECH_RUBRIC_PATH,
#             Config.HR_RUBRIC_PATH,
#             Config.TECH_CSV_PATH,
#             Config.HR_CSV_PATH
#         ]
#         missing = [p for p in required if not p.exists()]
#         if missing:
#             print("Missing evaluation files:")
#             for p in missing:
#                 print(f"  - {p}")
#             return False

#         print("All evaluation files found:")
#         for p in required:
#             print(f"  ✅ {p}")
#         return True


import os
from pathlib import Path

class Config:
    # Base directories - Fixed to point to the correct project structure
    BASE_DIR = Path(__file__).parent.parent  # This points to video-interview-system/
    DATA_DIR = BASE_DIR / "data"
    SRC_DIR = BASE_DIR / "src"
    
    # Model paths for emotion analysis - Fixed to use correct path
    MODELS_DIR = BASE_DIR / "models"  # Changed from SRC_DIR to BASE_DIR
    EMOTION_MODEL_PATH = MODELS_DIR / "best_model.keras"
    SCALER_PATH = MODELS_DIR / "scaler.pkl"
    ENCODER_PATH = MODELS_DIR / "encoder.pkl"  # Fixed filename from label_encoder.pkl to encoder.pkl
    
    # Audio/Video settings
    WHISPER_MODEL_NAME = "base"
    RECORDING_DURATION = 60  # seconds
        # PDF Report Settings
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    PDF_PAGE_SIZE = "letter"  # or "A4"
    PDF_MARGINS = {"top": 1, "bottom": 1, "left": 1, "right": 1}  # inches
    

    # Data directories
    RECORDINGS_DIR = DATA_DIR / "recordings"
    TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
    AUDIO_DIR = DATA_DIR / "audio"
    VIDEOS_DIR = DATA_DIR / "videos"
    RESULTS_DIR = DATA_DIR / "results"
    EVALUATION_DIR = DATA_DIR / "evaluation"
    
    # Evaluation data paths - Fixed to match your actual structure
    TECHNICAL_DIR = DATA_DIR / "evaluation" / "Technical"  # Changed path structure
    HR_DIR = DATA_DIR / "evaluation" / "HR"  # Changed path structure
    
    TECH_CSV_PATH = TECHNICAL_DIR / "dataset.csv"
    TECH_RUBRIC_PATH = TECHNICAL_DIR / "tech_rubric.json"
    TECH_OLD_RESULTS_PATH = TECHNICAL_DIR / "tech_evaluation_results.json"
    
    HR_CSV_PATH = HR_DIR / "interview_best_answers_samples.csv"
    HR_RUBRIC_PATH = HR_DIR / "hr_rubric.json"
    HR_OLD_RESULTS_PATH = HR_DIR / "hr_evaluation_results_with_samples.json"
    GRAMMAR_BASIC_ENABLED = True          # LanguageTool (always available)
    GRAMMAR_AI_ENABLED = False            # GPT-4o (optional premium)
    GRAMMAR_AI_THRESHOLD = 30             # Min words for AI analysis
    GRAMMAR_AI_AUTO_TRIGGER = True        # Auto-use AI for poor scores
    
    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    AZURE_OPENAI_API_VERSION = "2023-12-01-preview"
    AZURE_DEPLOYMENT_NAME = "GPT-4O-50-1"
    OPENAI_API_TYPE = "Azure"
    
    # Grammar scoring thresholds
    EXCELLENT_GRAMMAR_THRESHOLD = 85
    GOOD_GRAMMAR_THRESHOLD = 70
    FAIR_GRAMMAR_THRESHOLD = 50
        # Speech-aware grammar checking
    SPEECH_AWARE_GRAMMAR = True
    IGNORE_PROPER_NAMES = True
    IGNORE_CASUAL_PUNCTUATION = True
    IGNORE_NATURAL_SPEECH_PATTERNS = True
    
    # Speech grammar scoring (more lenient)
    SPEECH_GRAMMAR_MIN_SCORE = 30        # Higher minimum than formal writing
    SPEECH_GRAMMAR_MAX_PENALTY = 40      # Lower max penalty than formal writing
    # AI trigger conditions
    AI_TRIGGER_ERROR_RATE = 0.08          # 8% error rate triggers AI
    AI_TRIGGER_LOW_SCORE = 65     
    # Interview questions
    QUESTIONS = [
        "Explain how you would implement a Transformer-based Speech Emotion Recognition (SER) pipeline end-to-end, from raw audio input to predicted emotion labels.",
        "Given a large dataset of audio recordings, describe at least three feature-extraction techniques (e.g., Mel-spectrogram, log-Mel, MFCC) and discuss the pros and cons of each for a SER task.",
        "How does Retrieval-Augmented Generation (RAG) improve answer evaluation compared to using a vanilla LLM? Illustrate with a pseudo-code or high-level workflow.",
        "Suppose you have to fine-tune a pre-trained wav2vec 2.0 model on a new emotional‐speech dataset. Which steps would you follow (data preprocessing, training loop, hyperparameter tuning), and why?",
        "Tell me about a time you faced a conflict in a team. How did you resolve it?",
        "What are your greatest strengths and how do they apply to this role?",
        "Describe a situation when you had to adapt quickly to a significant change at work or in school. What did you learn?",
        "How do you handle constructive criticism? Give an example?"
    ]
    # Grammar checking settings
    GRAMMAR_BASIC_ENABLED = True          # LanguageTool (always available)
    GRAMMAR_AI_ENABLED = True             # Azure OpenAI (optional premium)
    GRAMMAR_AI_THRESHOLD = 30             # Min words for AI analysis
    GRAMMAR_AI_AUTO_TRIGGER = True        # Auto-use AI for poor scores
    
    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    AZURE_OPENAI_API_VERSION = "2023-12-01-preview"
    AZURE_DEPLOYMENT_NAME = "GPT-4O-50-1"
    OPENAI_API_TYPE = "Azure"
    
    # Grammar scoring thresholds
    EXCELLENT_GRAMMAR_THRESHOLD = 85
    GOOD_GRAMMAR_THRESHOLD = 70
    FAIR_GRAMMAR_THRESHOLD = 50
    
    # AI trigger conditions
    AI_TRIGGER_ERROR_RATE = 0.08          # 8% error rate triggers AI
    AI_TRIGGER_LOW_SCORE = 65             # Scores below this trigger AI
    
    # Speech-aware grammar checking
    SPEECH_AWARE_GRAMMAR = True
    IGNORE_PROPER_NAMES = True
    IGNORE_CASUAL_PUNCTUATION = True
    IGNORE_NATURAL_SPEECH_PATTERNS = True
    
    # Speech grammar scoring (more lenient)
    SPEECH_GRAMMAR_MIN_SCORE = 30        # Higher minimum than formal writing
    SPEECH_GRAMMAR_MAX_PENALTY = 40      # Lower max penalty than formal writing
    @staticmethod
    def setup_reports_directory():
        """Create reports directory if it doesn't exist"""
        os.makedirs(Config.REPORTS_DIR, exist_ok=True)
        return Config.REPORTS_DIR    
    @classmethod
    def setup_azure_openai_env(cls):
        """Setup Azure OpenAI environment variables"""
        os.environ["AZURE_OPENAI_API_KEY"] = cls.AZURE_OPENAI_API_KEY
        os.environ["AZURE_OPENAI_ENDPOINT"] = cls.AZURE_OPENAI_ENDPOINT
        os.environ["OPENAI_API_TYPE"] = cls.OPENAI_API_TYPE
    
    @classmethod
    def is_azure_openai_available(cls):
        """Check if Azure OpenAI is configured"""
        return bool(cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT and cls.GRAMMAR_AI_ENABLED)
    @staticmethod
    def create_directories():
        """Create necessary directories if they don't exist"""
        directories = [
            Config.DATA_DIR,
            Config.RECORDINGS_DIR,
            Config.TRANSCRIPTS_DIR,
            Config.AUDIO_DIR,
            Config.VIDEOS_DIR,
            Config.RESULTS_DIR,
            Config.EVALUATION_DIR,
            Config.TECHNICAL_DIR,
            Config.HR_DIR,
            Config.MODELS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def verify_model_files():
        """Verify that required model files exist"""
        required_files = [
            Config.EMOTION_MODEL_PATH,
            Config.SCALER_PATH,
            Config.ENCODER_PATH
        ]
        
        print("Checking model files:")
        missing_files = []
        for file_path in required_files:
            if file_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
                missing_files.append(str(file_path))
        
        return len(missing_files) == 0
    
    @staticmethod
    def verify_evaluation_files():
        """Verify that required evaluation files exist"""
        required_files = [
            Config.TECH_RUBRIC_PATH,
            Config.HR_RUBRIC_PATH,
            Config.TECH_CSV_PATH,
            Config.HR_CSV_PATH,
            Config.TECH_OLD_RESULTS_PATH,
            Config.HR_OLD_RESULTS_PATH
        ]
        
        print("Checking evaluation files:")
        missing_files = []
        for file_path in required_files:
            if file_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
                missing_files.append(str(file_path))
        
        return len(missing_files) == 0
    
    @staticmethod
    def get_missing_files():
        """Get detailed information about missing files"""
        missing_info = {
            "model_files": [],
            "evaluation_files": []
        }
        
        # Check model files
        model_files = [
            (Config.EMOTION_MODEL_PATH, "Keras emotion recognition model"),
            (Config.SCALER_PATH, "Feature scaler for preprocessing"),
            (Config.ENCODER_PATH, "Label encoder for emotions")
        ]
        
        for file_path, description in model_files:
            if not file_path.exists():
                missing_info["model_files"].append({
                    "path": str(file_path),
                    "description": description
                })
        
        # Check evaluation files
        eval_files = [
            (Config.TECH_RUBRIC_PATH, "Technical evaluation rubric"),
            (Config.HR_RUBRIC_PATH, "HR evaluation rubric"),
            (Config.TECH_CSV_PATH, "Technical questions dataset"),
            (Config.HR_CSV_PATH, "HR questions dataset"),
            (Config.TECH_OLD_RESULTS_PATH, "Technical evaluation results"),
            (Config.HR_OLD_RESULTS_PATH, "HR evaluation results")
        ]
        
        for file_path, description in eval_files:
            if not file_path.exists():
                missing_info["evaluation_files"].append({
                    "path": str(file_path),
                    "description": description
                })
        
        return missing_info
    
    @staticmethod
    def debug_paths():
        """Debug function to print all expected paths"""
        print("=== DEBUG: Expected file paths ===")
        print(f"BASE_DIR: {Config.BASE_DIR}")
        print(f"DATA_DIR: {Config.DATA_DIR}")
        print(f"MODELS_DIR: {Config.MODELS_DIR}")
        print(f"TECHNICAL_DIR: {Config.TECHNICAL_DIR}")
        print(f"HR_DIR: {Config.HR_DIR}")
        print()
        print("Model files:")
        print(f"  EMOTION_MODEL_PATH: {Config.EMOTION_MODEL_PATH}")
        print(f"  SCALER_PATH: {Config.SCALER_PATH}")
        print(f"  ENCODER_PATH: {Config.ENCODER_PATH}")
        print()
        print("Evaluation files:")
        print(f"  TECH_RUBRIC_PATH: {Config.TECH_RUBRIC_PATH}")
        print(f"  HR_RUBRIC_PATH: {Config.HR_RUBRIC_PATH}")
        print(f"  TECH_CSV_PATH: {Config.TECH_CSV_PATH}")
        print(f"  HR_CSV_PATH: {Config.HR_CSV_PATH}")
        print(f"  TECH_OLD_RESULTS_PATH: {Config.TECH_OLD_RESULTS_PATH}")
        print(f"  HR_OLD_RESULTS_PATH: {Config.HR_OLD_RESULTS_PATH}")
        print("=== END DEBUG ===")