

import streamlit as st
import sys
import os
import time
import cv2
import json
import random
import subprocess
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from components.audio_video_recorder import AudioVideoRecorder
from components.emotion_analyzer import EmotionAnalyzer
from components.transcription import Transcription
from components.grammar_checker import HybridGrammarChecker

# Only import CandidateEvaluator if evaluation files are available
try:
    from components.candidate_evaluator import CandidateEvaluator
except ImportError as e:
    CandidateEvaluator = None
    print(f"Warning: Could not import CandidateEvaluator: {e}")

def calculate_aggregate_score(analysis_results):
    """Calculate aggregate score from all analysis components"""
    scores = {}
    weights = {}
    
    # 1. Emotion Analysis Score (0-100)
    if analysis_results.get('emotion_analysis'):
        emotion_data = analysis_results['emotion_analysis']
        
        # Calculate emotion score based on confidence and positive emotions
        emotion_score = 0
        if emotion_data.get('avg_confidence') is not None:
            confidence_score = emotion_data['avg_confidence'] * 100
            
            # Bonus for positive emotions (happy, neutral are good for interviews)
            positive_emotions = ['happy', 'neutral', 'calm']
            negative_emotions = ['angry', 'fear', 'sad', 'disgust']
            
            emotion_dist = emotion_data.get('emotion_distribution', {})
            total_segments = emotion_data.get('total_segments', 0)
            
            # FIX: Check for zero division
            if total_segments > 0:
                positive_ratio = sum(emotion_dist.get(emotion, 0) for emotion in positive_emotions) / total_segments
                negative_ratio = sum(emotion_dist.get(emotion, 0) for emotion in negative_emotions) / total_segments
                
                # Emotion balance score (0-100)
                balance_score = (positive_ratio * 100) - (negative_ratio * 30)  # Penalize negative emotions less
                balance_score = max(0, min(100, balance_score))
                
                # Combine confidence and emotion balance
                emotion_score = (confidence_score * 0.4) + (balance_score * 0.6)
            else:
                # No segments detected - use only confidence score or set to low score
                emotion_score = confidence_score * 0.5  # Reduced score for no emotional segments
            
            emotion_score = max(0, min(100, emotion_score))
        
        scores['emotion'] = round(emotion_score, 2)
        weights['emotion'] = 20  # 20% weight
    
    # 2. Grammar Analysis Score (0-100)
    if analysis_results.get('grammar_analysis'):
        grammar_data = analysis_results['grammar_analysis']
        grammar_score = grammar_data.get('grammar_score', 0)
        
        scores['grammar'] = grammar_score
        weights['grammar'] = 25  # 25% weight
    
    # 3. Answer Evaluation Score (0-100)
    if analysis_results.get('answer_evaluation'):
        eval_data = analysis_results['answer_evaluation']
        answer_score = eval_data.get('final_combined_score', 0)
        
        scores['answer'] = answer_score
        weights['answer'] = 55  # 55% weight (most important)
    
    # Calculate weighted average
    if not scores:
        return {
            'aggregate_score': 0,
            'breakdown': {},
            'weights_used': {},
            'total_weight': 0,
            'components_available': [],
            'error': 'No analysis components available'
        }
    
    # Normalize weights to sum to 100
    total_available_weight = sum(weights.values())
    normalized_weights = {k: (v / total_available_weight) * 100 for k, v in weights.items()}
    
    # Calculate weighted score
    weighted_sum = sum(scores[component] * (normalized_weights[component] / 100) for component in scores)
    
    return {
        'aggregate_score': round(weighted_sum, 1),
        'breakdown': scores,
        'weights_used': normalized_weights,
        'total_weight': total_available_weight,
        'components_available': list(scores.keys())
    }

def display_aggregate_results(aggregate_data):
    """Display the aggregate evaluation results"""
    st.subheader("🎯 Overall Interview Performance")
    
    # Check if there's an error or no components
    if aggregate_data.get('error') or not aggregate_data.get('components_available'):
        st.warning("⚠️ Unable to calculate aggregate score - insufficient analysis data")
        st.info("This may occur when:")
        st.write("- No speech was detected in the recording")
        st.write("- Audio quality was too poor for analysis")
        st.write("- Recording was too short")
        return
    
    aggregate_score = aggregate_data['aggregate_score']
    
    # Main score display
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Large score display with color coding
        score_color = "#28a745" if aggregate_score >= 80 else "#ffc107" if aggregate_score >= 60 else "#dc3545"
        
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            background: linear-gradient(135deg, {score_color}20, {score_color}10);
            border: 2px solid {score_color};
            margin: 10px 0;
        ">
            <h1 style="
                color: {score_color};
                font-size: 3em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            ">{aggregate_score}/100</h1>
            <h3 style="
                color: {score_color};
                margin: 10px 0 0 0;
            ">Overall Performance</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Performance level
        if aggregate_score >= 85:
            st.success("🌟 **Excellent**")
            st.write("Outstanding interview performance!")
        elif aggregate_score >= 75:
            st.success("⭐ **Very Good**")
            st.write("Strong interview performance!")
        elif aggregate_score >= 65:
            st.info("👍 **Good**")
            st.write("Solid interview performance!")
        elif aggregate_score >= 50:
            st.warning("📈 **Fair**")
            st.write("Room for improvement!")
        else:
            st.error("❌ **Needs Work**")
            st.write("Significant improvement needed!")
    
    with col3:
        # Components analyzed
        components = aggregate_data['components_available']
        st.write("**Components Analyzed:**")
        component_icons = {
            'emotion': '🎭',
            'grammar': '📝', 
            'answer': '🤖'
        }
        for comp in components:
            icon = component_icons.get(comp, '📊')
            st.write(f"{icon} {comp.title()}")
    
    # Only show detailed breakdown if we have valid scores
    if aggregate_data.get('breakdown'):
        # Detailed breakdown
        st.markdown("---")
        st.subheader("📊 Score Breakdown")
        
        breakdown = aggregate_data['breakdown']
        weights = aggregate_data['weights_used']
        
        # Create columns for each component
        cols = st.columns(len(breakdown))
        
        component_details = {
            'emotion': {'name': 'Emotional Intelligence', 'icon': '🎭', 'desc': 'Confidence & emotional control'},
            'grammar': {'name': 'Communication Skills', 'icon': '📝', 'desc': 'Grammar & language quality'},
            'answer': {'name': 'Content Quality', 'icon': '🤖', 'desc': 'Answer relevance & depth'}
        }
        
        for i, (component, score) in enumerate(breakdown.items()):
            with cols[i]:
                details = component_details.get(component, {'name': component.title(), 'icon': '📊', 'desc': ''})
                weight = weights.get(component, 0)
                
                # Component score card
                score_color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
                
                st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 15px;
                    border-radius: 10px;
                    background: {score_color}15;
                    border: 1px solid {score_color}50;
                    margin: 5px 0;
                ">
                    <div style="font-size: 2em;">{details['icon']}</div>
                    <h4 style="margin: 5px 0; color: {score_color};">{details['name']}</h4>
                    <h2 style="margin: 5px 0; color: {score_color};">{score:.2f}/100</h2>
                    <small style="color: #666;">Weight: {weight:.1f}%</small>
                    <br>
                    <small style="color: #888;">{details['desc']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Progress bars for visual representation
        st.markdown("### 📈 Visual Breakdown")
        for component, score in breakdown.items():
            details = component_details.get(component, {'name': component.title(), 'icon': '📊'})
            weight = weights.get(component, 0)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{details['icon']} **{details['name']}** (Weight: {weight:.1f}%)")
                st.progress(score / 100)
            with col2:
                st.metric("Score", f"{score:.2f}/100")

def initialize_session_state():
    """Initialize session state variables"""
    # Setup Azure OpenAI environment
    Config.setup_azure_openai_env()
    if 'selected_questions' not in st.session_state:
        # Select 2 Technical and 1 HR questions randomly
        tech_questions = [(i, q) for i, q in enumerate(Config.QUESTIONS[:4])]  # First 4 are Technical
        hr_questions = [(i, q) for i, q in enumerate(Config.QUESTIONS[4:], 4)]  # Last 4 are HR

        selected_tech = random.sample(tech_questions, 2)
        selected_hr = random.sample(hr_questions, 1)

        # Combine and shuffle
        selected_questions = selected_tech + selected_hr
        random.shuffle(selected_questions)

        st.session_state.selected_questions = selected_questions
        st.session_state.current_question_idx = 0
        st.session_state.completed_questions = []
        st.session_state.analysis_results = {}

    if 'recorder' not in st.session_state:
        st.session_state.recorder = AudioVideoRecorder()

    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False

    if 'recording' not in st.session_state:
        st.session_state.recording = False

    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

    if 'viewing_question_details' not in st.session_state:
        st.session_state.viewing_question_details = False

def show_missing_files_info():
    """Display information about missing files"""
    missing_info = Config.get_missing_files()

    if missing_info["model_files"]:
        st.error("❌ Required Emotion Analysis Model Files Missing:")
        for file_info in missing_info["model_files"]:
            st.write(f"📁 **{file_info['description']}**")
            st.code(file_info['path'])

        with st.expander("ℹ️ How to get the model files"):
            st.write("""
            **The emotion analysis requires trained model files:**
            
            1. **best_model.keras** - The trained emotion recognition model
            2. **scaler.pkl** - Feature scaler used during training
            3. **encoder.pkl** - Label encoder for emotion classes
            
            **To obtain these files:**
            - Train your own emotion recognition model using your training data
            - Or contact your project supervisor for the pre-trained models
            - Place the files in the `models/` directory
            """)

    if missing_info["evaluation_files"]:
        st.warning("⚠️ Evaluation Files Missing (Answer evaluation will be limited):")
        for file_info in missing_info["evaluation_files"]:
            st.write(f"📁 **{file_info['description']}**")
            st.code(file_info['path'])

def create_sidebar():
    """Create the enhanced sidebar with navigation"""
    with st.sidebar:
        st.title("🎥 Interview System")

        # Progress indicator
        current_idx = st.session_state.current_question_idx
        total_questions = len(st.session_state.selected_questions)
        progress = current_idx / total_questions if total_questions > 0 else 0

        st.subheader("📊 Progress")
        st.progress(progress)
        st.write(f"Question {current_idx + 1} of {total_questions}")

        st.markdown("---")

        # Question navigation
        st.subheader("📋 Interview Questions")

        for i, (q_idx, question) in enumerate(st.session_state.selected_questions):
            question_type = "Technical" if q_idx < 4 else "HR"

            # Status indicators
            if i in st.session_state.completed_questions:
                status = "✅"
            elif i == current_idx:
                status = "▶️"
            else:
                status = "⏳"

            # Question preview
            preview = question[:60] + "..." if len(question) > 60 else question

            if i == current_idx:
                st.markdown(f"**{status} Q{i+1}: {question_type}**")
                st.info(preview)
            else:
                st.write(f"{status} Q{i+1}: {question_type}")
                with st.expander(f"Preview Q{i+1}"):
                    st.write(preview)

        st.markdown("---")

        # Navigation controls
        st.subheader("🎮 Navigation")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous", disabled=current_idx == 0):
                if current_idx > 0:
                    st.session_state.current_question_idx -= 1
                    st.session_state.analysis_complete = False
                    st.session_state.viewing_question_details = False
                    st.rerun()

        with col2:
            if st.button("➡️ Next", disabled=current_idx >= total_questions - 1):
                if current_idx < total_questions - 1:
                    st.session_state.current_question_idx += 1
                    st.session_state.analysis_complete = False
                    st.session_state.viewing_question_details = False
                    st.rerun()

        # Reset interview
        if st.button("🔄 New Interview", type="secondary"):
            # Clear all question recordings from recorder
            if 'recorder' in st.session_state:
                # Delete all question recordings
                all_recordings = st.session_state.recorder.get_all_recordings()
                for question_id in list(all_recordings.keys()):
                    st.session_state.recorder.delete_question_recording(question_id)
            
            # Clear session state for new interview
            keys_to_clear = [
                'selected_questions', 'current_question_idx', 'completed_questions',
                'analysis_results', 'video_file', 'show_results',
                'analysis_complete', 'viewing_question_details'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        # Summary section
        if st.session_state.completed_questions:
            st.markdown("---")
            st.subheader("📈 Summary")
            completed_count = len(st.session_state.completed_questions)
            st.metric("Completed", f"{completed_count}/{total_questions}")

            if st.button("📋 View All Results"):
                st.session_state.show_results = True
                st.session_state.viewing_question_details = False
                st.rerun()

def get_current_question_info():
    """Get current question information"""
    if not st.session_state.selected_questions:
        return None, None, None

    current_idx = st.session_state.current_question_idx
    if current_idx >= len(st.session_state.selected_questions):
        return None, None, None

    q_idx, question = st.session_state.selected_questions[current_idx]
    question_type = "Technical" if q_idx < 4 else "HR"

    return question, question_type, current_idx + 1

def create_main_content():
    """Create the main content area"""
    # 1) If user wants to see all results, show complete summary page
    if st.session_state.get('show_results', False):
        show_complete_results()
        return

    # 2) If viewing a single question's details, show that
    if st.session_state.get('viewing_question_details', False):
        current_idx = st.session_state.current_question_idx
        show_question_details(current_idx)
        return

    # 3) Otherwise, show the next question to record/analyze
    question, question_type, question_num = get_current_question_info()
    total_questions = len(st.session_state.selected_questions)

    if question is None:
        st.success("🎉 Congratulations! You have completed all interview questions!")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📊 View Complete Results", type="primary"):
                st.session_state.show_results = True
                st.rerun()
        return

    # Question display
    st.header(f"📝 Question {question_num} ({question_type})")

    # Question card (styled container)
    with st.container():
        st.markdown(f"""
        <div style="
            padding: 20px; 
            border-radius: 10px; 
            background: linear-gradient(90deg, #f0f2f6 0%, #e8eaed 100%);
            border-left: 5px solid {'#1f77b4' if question_type == 'Technical' else '#ff7f0e'};
            margin: 20px 0;
        ">
            <h4 style="color: #333; margin-top: 0;">{question_type} Question</h4>
            <p style="font-size: 16px; line-height: 1.6; color: #444;">{question}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    current_idx = st.session_state.current_question_idx
    # 4) If this question has been analyzed, show the "Show Results" button + navigation
    if current_idx in st.session_state.analysis_results:
        st.success("✅ Analysis completed for this question!")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Reset show_results just in case
            st.session_state.show_results = False
            if st.button("📊 Show Results", key=f"show_results_btn_{current_idx}", type="primary"):
                st.session_state.viewing_question_details = True
                st.rerun()

        with col2:
            if current_idx < total_questions - 1:
                if st.button("➡️ Next Question", key=f"next_btn_{current_idx}", type="secondary"):
                    st.session_state.current_question_idx += 1
                    st.session_state.analysis_complete = False
                    st.session_state.viewing_question_details = False
                    st.rerun()

        with col3:
            if st.button("🔄 Re-record", key=f"re_record_btn_{current_idx}", type="secondary"):
                # Clear current results to allow re-recording
                if current_idx in st.session_state.analysis_results:
                    del st.session_state.analysis_results[current_idx]
                if current_idx in st.session_state.completed_questions:
                    st.session_state.completed_questions.remove(current_idx)
                if 'video_file' in st.session_state:
                    del st.session_state['video_file']
                st.session_state.recorder.delete_question_recording(current_idx)
                st.session_state.analysis_complete = False
                st.session_state.viewing_question_details = False
                st.rerun()

        return

    # 5) Otherwise, show the recording section
    create_recording_section(question, question_type)

def show_question_details(question_idx):
    """Show detailed results for a specific question"""
    if question_idx not in st.session_state.analysis_results:
        st.warning("No results found for this question.")
        return

    results_data = st.session_state.analysis_results[question_idx]
    question = results_data['question']
    question_type = results_data['question_type']
    results = results_data['results']

    st.header(f"📊 Results for Question {question_idx + 1}")
    st.info(f"**{question_type} Question:** {question}")

    # Show aggregate results first if available
    if results.get('aggregate_evaluation'):
        display_aggregate_results(results['aggregate_evaluation'])
        st.markdown("---")

    # Show video if available
    if 'video_file' in results_data and os.path.exists(results_data['video_file']):
        st.video(results_data['video_file'])

    # Emotion Analysis
    if results.get('emotion_analysis'):
        st.subheader("🎭 Emotion Analysis Results")
        display_emotion_results(results['emotion_analysis'])
    else:
        st.info("ℹ️ Emotion analysis not available.")

    # Transcript
    if results.get('transcript'):
        st.subheader("📝 Transcription")
        st.text_area("Interview Transcript:", results['transcript'], height=200, key=f"transcript_{question_idx}")
    else:
        st.info("ℹ️ Transcript not available.")

    # Grammar Analysis
    if results.get('grammar_analysis'):
        st.subheader("📝 Grammar & Communication Analysis")
        display_grammar_results(results['grammar_analysis'], use_expanders=True)
    else:
        st.info("ℹ️ Grammar analysis not available.")

    # AI Answer Evaluation
    if results.get('answer_evaluation'):
        st.subheader("🤖 AI Answer Evaluation")
        display_evaluation_results(results['answer_evaluation'], question_type, context="details")
    else:
        st.info("ℹ️ Answer evaluation not available.")

    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Back to Question", key=f"back_{question_idx}"):
            st.session_state.viewing_question_details = False
            st.rerun()

    with col2:
        if question_idx < len(st.session_state.selected_questions) - 1:
            if st.button("➡️ Next Question", key=f"next_{question_idx}"):
                st.session_state.current_question_idx += 1
                st.session_state.analysis_complete = False
                st.session_state.viewing_question_details = False
                st.rerun()

    with col3:
        if st.button("📋 All Results", key=f"all_{question_idx}"):
            st.session_state.show_results = True
            st.session_state.viewing_question_details = False
            st.rerun()

import time, os, cv2
import streamlit as st

import time, os, cv2
import streamlit as st

def create_recording_section(question, question_type):
    """Create the recording section—now with an in‐frame timer overlay."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🎬 Recording Center")

        # CAMERA PREVIEW + IN‐FRAME TIMER
        video_placeholder = st.empty()

        # Camera controls
        cam_col1, cam_col2 = st.columns(2)
        with cam_col1:
            if st.button("📹 Start Camera", type="secondary", key="start_cam"):
                # Start the camera preview
                if st.session_state.recorder.start_preview():
                    st.session_state.camera_active = True
                    st.success("✅ Camera started!")
                    st.rerun()

        with cam_col2:
            if st.button("⏹️ Stop Camera", key="stop_cam"):
                st.session_state.recorder.stop_preview()
                st.session_state.camera_active = False
                st.info("📹 Camera stopped")
                st.rerun()

        # Live feed + overlay
        if st.session_state.get("camera_active", False):
            frame = st.session_state.recorder.get_frame()
            if frame is not None:
                # If we are recording, compute elapsed time and draw it on the frame
                if st.session_state.get("recording", False):
                    # elapsed seconds since we hit “Start Recording”
                    elapsed = int(time.time() - st.session_state.record_start_time)
                    # Clip at 120 so it never prints > 120:
                    if elapsed > 120:
                        elapsed = 120

                    # Draw a semi‐opaque rectangle background (optional) for readability
                    (h, w) = frame.shape[:2]
                    cv2.rectangle(
                        frame,
                        (10, 10),
                        (10 + 120, 10 + 40),
                        (0, 0, 0),
                        thickness=-1,  # filled
                        lineType=cv2.LINE_AA,
                    )

                    # Then draw the elapsed time in bright red
                    cv2.putText(
                        frame,
                        f"⏱️ {elapsed:3d}s",
                        (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        2,
                        cv2.LINE_AA,
                    )

                # Convert to RGB and show
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, caption="Live Camera Feed", width=400)
            else:
                video_placeholder.info("📹 Camera is starting...")
        else:
            video_placeholder.info("📹 Click 'Start Camera' to see yourself")

        st.markdown("---")

        # RECORD / STOP buttons
        rec_col1, rec_col2 = st.columns(2)
        with rec_col1:
            if st.button("🔴 Start Recording", type="primary", key="start_rec"):
                start_recording(question, question_type)

        with rec_col2:
            if st.button("⏹️ Stop Recording", key="stop_rec"):
                stop_recording()

        # ANALYZE button (once there’s a saved file)
        if "video_file" in st.session_state and os.path.exists(st.session_state.video_file):
            if st.button("🔍 Analyze Recording", type="primary", key="analyze"):
                analyze_current_recording(question, question_type)

        # (Assume you have a function to show overall status somewhere below)
        show_recording_status()


def start_recording(video_placeholder, question, question_type):
    """Start recording with countdown and automatic stop after 2 minutes"""
    if not st.session_state.get('camera_active', False):
        st.warning("⚠️ Please start camera first")
        return

    # Get current question index
    current_question_idx = st.session_state.current_question_idx
    
    # Show 3-second countdown
    countdown_placeholder = st.empty()
    for i in range(3, 0, -1):
        countdown_placeholder.markdown(f"<h2 style='text-align: center; color: red;'>Recording starts in {i}...</h2>", unsafe_allow_html=True)
        time.sleep(1)
    
    countdown_placeholder.markdown("<h2 style='text-align: center; color: green;'>🔴 RECORDING!</h2>", unsafe_allow_html=True)
    
    # Start recording with 2-minute duration (120 seconds)
    max_duration = 120  # 2 minutes
    output_path = st.session_state.recorder.start_recording(duration=max_duration, question_id=current_question_idx)

    if output_path:
        st.session_state.recording = True
        st.session_state.record_start_time = time.time()
        st.success("🎬 Recording started!")

        # Create placeholders for timer and progress
        timer_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        # Recording loop with counter and manual stop checking
        for elapsed_seconds in range(max_duration + 1):
            # Check if recording was stopped manually FIRST
            if not st.session_state.get('recording', False):
                # Recording was stopped manually
                timer_placeholder.markdown("""
                <div style="
                    text-align: center;
                    padding: 15px;
                    border-radius: 10px;
                    background: linear-gradient(135deg, #ffc107, #fd7e14);
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0;
                    box-shadow: 0 4px 8px rgba(255, 193, 7, 0.3);
                ">
                    ⏹️ RECORDING STOPPED MANUALLY
                </div>
                """, unsafe_allow_html=True)
                progress_placeholder.empty()
                countdown_placeholder.empty()
                break
            
            # Calculate remaining time
            remaining_seconds = max_duration - elapsed_seconds
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            
            # Calculate progress
            progress = elapsed_seconds / max_duration
            
            # Update timer display
            if remaining_seconds > 0:
                timer_placeholder.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 15px;
                    border-radius: 10px;
                    background: linear-gradient(135deg, #ff4444, #cc0000);
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0;
                    box-shadow: 0 4px 8px rgba(255, 68, 68, 0.3);
                ">
                    🔴 RECORDING: {minutes:02d}:{seconds:02d} remaining
                </div>
                """, unsafe_allow_html=True)
            else:
                # Time's up - auto stop
                timer_placeholder.markdown("""
                <div style="
                    text-align: center;
                    padding: 15px;
                    border-radius: 10px;
                    background: linear-gradient(135deg, #28a745, #20c997);
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0;
                    box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
                ">
                    ✅ RECORDING COMPLETE (TIME LIMIT REACHED)!
                </div>
                """, unsafe_allow_html=True)
                break
            
            # Update progress bar
            progress_placeholder.progress(progress)
            
            # Update live feed during recording
            frame = st.session_state.recorder.get_frame()
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Add recording indicator with timer
                cv2.circle(frame_rgb, (30, 30), 15, (255, 0, 0), -1)
                cv2.putText(frame_rgb, "REC", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(frame_rgb, f"{minutes:02d}:{seconds:02d}", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                video_placeholder.image(frame_rgb, caption="🔴 RECORDING", width=400)

            # Sleep for 1 second but check for manual stop more frequently
            for i in range(10):  # Check 10 times per second for responsiveness
                time.sleep(0.1)
                if not st.session_state.get('recording', False):
                    break

        # Ensure recording is stopped
        st.session_state.recording = False
        
        # Stop recording and get final file
        final_video = st.session_state.recorder.stop_recording()
        if final_video:
            st.success("✅ Recording completed and saved successfully!")
            # Clear the timer and progress displays after a short delay
            time.sleep(2)
            timer_placeholder.empty()
            progress_placeholder.empty()
            countdown_placeholder.empty()
        else:
            st.error("❌ Failed to process recording")
    else:
        st.error("❌ Failed to start recording")
def stop_recording():
    """Manual Stop (invoked by the Stop Recording button)."""
    if st.session_state.get("recording", False):
        final_path = st.session_state.recorder.stop_recording()
        st.session_state.recording = False

        if final_path and os.path.exists(final_path):
            st.success("✅ Recording saved successfully!")
        else:
            st.error("❌ Recording failed")
    else:
        st.warning("⚠️ No active recording to stop")



def show_recording_status():
    """Show current recording status for the current question"""
    current_question_idx = st.session_state.current_question_idx
    
    if st.session_state.get('recording', False):
        st.error("🔴 Currently recording...")
    elif st.session_state.get('camera_active', False):
        st.info("📹 Camera is active")
    elif st.session_state.recorder.has_question_recording(current_question_idx):
        status = st.session_state.recorder.get_recording_status(current_question_idx)
        filename = os.path.basename(status['file_path'])
        st.success(f"📁 Recording ready for Q{current_question_idx + 1}: {filename}")
    else:
        st.info(f"📝 No recording for Question {current_question_idx + 1}")

def analyze_current_recording(question, question_type):
    """Analyze the current recording with aggregate scoring"""
    current_question_idx = st.session_state.current_question_idx
    
    # Check if THIS question has a recording using the recorder's method
    if not st.session_state.recorder.has_question_recording(current_question_idx):
        st.warning(f"⚠️ No recording found for Question {current_question_idx + 1}. Please record first.")
        return

    # Use the question-specific video file from recorder
    video_file = st.session_state.recorder.get_question_recording(current_question_idx)
    
    # Perform analysis
    analysis_results = perform_analysis(video_file, question, question_type)

    if analysis_results:
        # Calculate aggregate score
        aggregate_data = calculate_aggregate_score(analysis_results)
        analysis_results['aggregate_evaluation'] = aggregate_data
        
        # Store results with question-specific video file
        st.session_state.analysis_results[current_question_idx] = {
            'question': question,
            'question_type': question_type,
            'video_file': video_file,  # Use question-specific file
            'results': analysis_results
        }

        # Mark as completed
        if current_question_idx not in st.session_state.completed_questions:
            st.session_state.completed_questions.append(current_question_idx)

        st.session_state.analysis_complete = True

        # Show aggregate results
        st.markdown("---")
        st.subheader("🎯 Overall Performance Score")
        display_aggregate_results(aggregate_data)

        # Show success message and options
        st.balloons()
        st.success("✅ Analysis completed successfully!")

        # Show navigation options
        st.markdown("---")
        st.subheader("🎯 What's Next?")

        col1, col2 = st.columns(2)

        with col1:
            if current_question_idx < len(st.session_state.selected_questions) - 1:
                if st.button("➡️ Next Question", key="next_after_analysis", type="secondary"):
                    st.session_state.current_question_idx += 1
                    st.session_state.analysis_complete = False
                    st.session_state.viewing_question_details = False
                    st.rerun()
            else:
                if st.button("🎉 View All Results", key="final_results", type="secondary"):
                    st.session_state.show_results = True
                    st.session_state.viewing_question_details = False
                    st.rerun()

        with col2:
            if st.button("🔄 Re-record", key="re_record_after_analysis", type="secondary"):
                # Clear current results to allow re-recording
                if current_question_idx in st.session_state.analysis_results:
                    del st.session_state.analysis_results[current_question_idx]
                if current_question_idx in st.session_state.completed_questions:
                    st.session_state.completed_questions.remove(current_question_idx)
                # Delete question-specific recording
                st.session_state.recorder.delete_question_recording(current_question_idx)
                st.session_state.analysis_complete = False
                st.session_state.viewing_question_details = False
                st.rerun()

# Update the create_recording_section function
def create_recording_section(question, question_type):
    """Create the recording and analysis section"""
    # Center the recording controls
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("🎬 Recording Center")

        # Camera preview
        camera_container = st.container()
        with camera_container:
            video_placeholder = st.empty()

            # Camera controls
            cam_col1, cam_col2 = st.columns(2)
            with cam_col1:
                if st.button("📹 Start Camera", type="secondary", key="start_cam"):
                    if st.session_state.recorder.start_preview():
                        st.session_state.camera_active = True
                        st.rerun()

            with cam_col2:
                if st.button("📹 Stop Camera", type="secondary", key="stop_cam"):
                    st.session_state.recorder.stop_preview()
                    st.session_state.camera_active = False
                    st.rerun()

            # Show camera feed
            if st.session_state.get('camera_active', False):
                frame = st.session_state.recorder.get_frame()
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_placeholder.image(frame_rgb, caption="Live Camera Feed", width=400)
                else:
                    video_placeholder.info("📹 Camera is starting...")
            else:
                video_placeholder.info("📹 Click 'Start Camera' to see yourself")

        st.markdown("---")

        # Recording controls
        rec_col1, rec_col2 = st.columns(2)

        with rec_col1:
            if st.button("🔴 Start Recording", type="primary", key="start_rec"):
                start_recording(video_placeholder, question, question_type)

        with rec_col2:
            if st.button("⏹️ Stop Recording", key="stop_rec"):
                stop_recording()

        # Analysis button - CHECK QUESTION-SPECIFIC RECORDING
        current_question_idx = st.session_state.current_question_idx
        
        if st.session_state.recorder.has_question_recording(current_question_idx):
            if st.button("🔍 Analyze Recording", type="primary", key="analyze"):
                analyze_current_recording(question, question_type)
        
        # Status display - SHOW QUESTION-SPECIFIC STATUS
        show_recording_status()

# Update the main question display to also check question-specific recordings
def display_current_question():
    current_idx = st.session_state.current_question_idx
    total_questions = len(st.session_state.selected_questions)
    current_question = st.session_state.selected_questions[current_idx]
    
    question = current_question['question']
    question_type = current_question['type']
    
    # Display question header
    st.header(f"Question {current_idx + 1} of {total_questions}")
    st.subheader(f"📝 {question_type} Question")
    
    # Question text
    question_style = """
    <div style="
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    ">
        <h4 style="color: #1f77b4; margin-bottom: 0.5rem;">Question:</h4>
        <p style="font-size: 1.1rem; margin: 0;">{}</p>
    </div>
    """.format(question)
    
    st.markdown(question_style, unsafe_allow_html=True)
    
    # Progress bar
    progress = (current_idx + 1) / total_questions
    st.progress(progress)
    
    # Check if THIS question has been analyzed
    if current_idx in st.session_state.analysis_results:
        st.success("✅ Analysis completed for this question!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Show Results", key=f"show_results_btn_{current_idx}", type="primary"):
                st.session_state.viewing_question_details = True
                st.rerun()
        
        with col2:
            if current_idx < total_questions - 1:
                if st.button("➡️ Next Question", key=f"next_btn_{current_idx}", type="secondary"):
                    st.session_state.current_question_idx += 1
                    st.session_state.analysis_complete = False
                    st.session_state.viewing_question_details = False
                    st.rerun()
        
        with col3:
            if st.button("🔄 Re-record", key=f"re_record_btn_{current_idx}", type="secondary"):
                # Clear current results to allow re-recording
                if current_idx in st.session_state.analysis_results:
                    del st.session_state.analysis_results[current_idx]
                if current_idx in st.session_state.completed_questions:
                    st.session_state.completed_questions.remove(current_idx)
                # Delete question-specific recording using recorder
                st.session_state.recorder.delete_question_recording(current_idx)
                st.session_state.analysis_complete = False
                st.session_state.viewing_question_details = False
                st.rerun()
        
        return
    
    # Otherwise, show the recording section
    create_recording_section(question, question_type)

# Also update any other functions that reference 'video_file' in session_state
# Replace all instances of st.session_state['video_file'] with the appropriate recorder method calls

def perform_analysis(video_file, question, question_type):
    """Perform comprehensive analysis of the video"""
    
    # Initialize components based on available files
    model_files_available = Config.verify_model_files()
    evaluation_files_available = Config.verify_evaluation_files()

    emotion_analyzer = None
    transcription = None
    evaluator = None
    grammar_checker = None

    try:
        # Always try to initialize transcription
        transcription = Transcription(model_name=Config.WHISPER_MODEL_NAME)
        # Initialize grammar checker
        if Config.GRAMMAR_BASIC_ENABLED:
            grammar_checker = HybridGrammarChecker()
            
            # Show checker capabilities
            checker_info = grammar_checker.get_analysis_summary()
            if checker_info['hybrid_mode']:
                st.info("🤖 Hybrid grammar analysis available (Local + AI)")
            elif checker_info['local_available']:
                st.info("⚡ Local grammar analysis available")
            else:
                st.warning("⚠️ Grammar analysis unavailable")

        # Initialize emotion analyzer if model files are available
        if model_files_available:
            emotion_analyzer = EmotionAnalyzer(
                model_path=Config.EMOTION_MODEL_PATH,
                scaler_path=Config.SCALER_PATH,
                encoder_path=Config.ENCODER_PATH
            )

        # Initialize evaluator if files are available
        if evaluation_files_available and CandidateEvaluator:
            try:
                evaluator = CandidateEvaluator()
            except Exception as e:
                st.warning(f"⚠️ Answer evaluator initialization failed: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error initializing components: {str(e)}")
        return None

    with st.spinner("🔍 Performing comprehensive analysis... This may take a few minutes."):
        try:
            # Show video
            st.video(video_file)

            # Check if video has audio
            probe_cmd = ['ffprobe', '-v', 'quiet', '-show_streams', '-select_streams', 'a', video_file]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)

            analysis_results = {}

            if not result.stdout.strip():
                st.warning("⚠️ Video has no audio track. Analysis will be limited.")
                analysis_results['emotion_analysis'] = None
                analysis_results['transcript'] = None
                analysis_results['answer_evaluation'] = None
                analysis_results['grammar_analysis'] = None

            else:
                # 1. Emotion Analysis
                if emotion_analyzer:
                    st.subheader("🎭 Emotion Analysis Results")
                    with st.spinner("Analyzing emotions..."):
                        emotions = emotion_analyzer.analyze(video_file)
                        analysis_results['emotion_analysis'] = emotions

                    display_emotion_results(emotions)
                else:
                    st.info("ℹ️ Emotion analysis not available (model files missing)")
                    analysis_results['emotion_analysis'] = None

                # 2. Transcription
                transcript = None
                if transcription:
                    st.subheader("📝 Transcription")
                    with st.spinner("Transcribing audio..."):
                        transcript = transcription.transcribe_video(video_file)
                        analysis_results['transcript'] = transcript

                    st.text_area("Interview Transcript:", transcript, height=200, key="current_transcript")
                else:
                    st.info("ℹ️ Transcription not available")
                    analysis_results['transcript'] = None
                
                # 3. Grammar Analysis
                if grammar_checker and transcript and transcript.strip():
                    word_count = len(transcript.split())
                    if word_count >= 5:  # Minimum words for analysis
                        st.subheader("📝 Grammar & Communication Analysis")
                        with st.spinner("Analyzing grammar and communication quality..."):
                            try:
                                grammar_analysis = grammar_checker.check_grammar(transcript)
                                analysis_results['grammar_analysis'] = grammar_analysis
                                
                                display_grammar_results(grammar_analysis)
                                
                            except Exception as e:
                                st.error(f"❌ Error during grammar analysis: {str(e)}")
                                analysis_results['grammar_analysis'] = {"error": str(e)}
                    else:
                        st.info(f"ℹ️ Grammar analysis requires at least 5 words (found {word_count})")
                        analysis_results['grammar_analysis'] = None
                else:
                    if not transcript:
                        st.info("ℹ️ Grammar analysis not available (no transcript)")
                    else:
                        st.info("ℹ️ Grammar analysis not enabled")
                    analysis_results['grammar_analysis'] = None
                
                # 4. Answer Evaluation
                if evaluator and transcript and transcript.strip():
                    st.subheader("🤖 AI Answer Evaluation")
                    with st.spinner("Evaluating answer using AI..."):
                        try:
                            evaluation = evaluator.evaluate_question_answer(question, transcript)
                            analysis_results['answer_evaluation'] = evaluation

                            display_evaluation_results(evaluation, question_type, context="analysis")

                        except Exception as e:
                            st.error(f"❌ Error during answer evaluation: {str(e)}")
                            analysis_results['answer_evaluation'] = {"error": str(e)}
                else:
                    if not transcript or not transcript.strip():
                        st.warning("⚠️ No transcript available for answer evaluation.")
                    else:
                        st.info("ℹ️ Answer evaluation not available.")
                    analysis_results['answer_evaluation'] = None

            # Save results
            save_analysis_results(video_file, question, question_type, analysis_results)

            return analysis_results

        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            return None
from components.pdf_report_generator import PDFReportGenerator

def generate_and_download_pdf(analysis_results, question, question_type, question_idx):
    """Generate PDF report and provide download link"""
    try:
        # Initialize PDF generator
        pdf_generator = PDFReportGenerator()
        
        # Add question index to results
        analysis_results['question_index'] = question_idx
        
        # Generate PDF
        pdf_path = pdf_generator.generate_report(
            analysis_results, 
            question, 
            question_type,
            candidate_id="CANDIDATE"
        )
        
        # Provide download link in Streamlit
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.success("📄 PDF Report Generated Successfully!")
            
            # Create download button
            filename = os.path.basename(pdf_path)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                key=f"download_pdf_{question_idx}"
            )
            
            # Show file info
            st.info(f"Report saved as: {filename}")
            
        else:
            st.error("❌ Failed to generate PDF report")
            
    except Exception as e:
        st.error(f"❌ Error generating PDF: {str(e)}")
def display_emotion_results(emotions):
    """Display emotion analysis results"""
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Dominant Emotion", emotions['dominant_emotion'])
        st.metric("Confidence", f"{emotions['avg_confidence']:.3f}")

    with col2:
        st.metric("Total Segments", emotions['total_segments'])

    # Emotion distribution
    if emotions['emotion_distribution']:
        st.subheader("📊 Emotion Distribution")
        for emotion, count in emotions['emotion_distribution'].items():
            percentage = (count / emotions['total_segments']) * 100
            st.progress(percentage/100)
            st.write(f"**{emotion}**: {count} segments ({percentage:.1f}%)")

def display_grammar_results(grammar_analysis, use_expanders=True):
    """Display grammar analysis results - GRAMMAR ONLY (no spelling or capitalization)"""
    if not grammar_analysis or grammar_analysis.get('analysis_type') == 'empty':
        st.info("ℹ️ No text available for grammar analysis")
        return
    
    analysis_type = grammar_analysis.get('analysis_type', 'unknown')
    ai_used = grammar_analysis.get('ai_used', False)
    
    # Header with analysis type indicator and speech context note
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📝 Grammar Analysis")
        st.caption("🎤 *Analyzed for spoken language context - proper names, capitalization, and natural speech patterns are considered normal*")
    with col2:
        if ai_used:
            st.success("🤖 AI Enhanced")
        else:
            st.info("⚡ Speech-Aware")

    # Main score display - GRAMMAR ONLY
    grammar_score = grammar_analysis.get('grammar_score', 0)
    st.metric("Grammar Score", f"{grammar_score}/100")

    # Overall assessment
    if grammar_score >= 85:
        st.success(f"🌟 Excellent grammar! Score: {grammar_score}/100")
    elif grammar_score >= 70:
        st.info(f"👍 Good grammar with minor areas for improvement. Score: {grammar_score}/100")
    elif grammar_score >= 50:
        st.warning(f"📝 Grammar needs attention. Score: {grammar_score}/100")
    else:
        st.error(f"❌ Grammar requires significant improvement. Score: {grammar_score}/100")

    # AI-powered insights (if available) - GRAMMAR ONLY
    if ai_used and grammar_analysis.get('key_strengths'):
        if use_expanders:
            with st.expander("🌟 Grammar Strengths", expanded=False):
                for strength in grammar_analysis['key_strengths']:
                    st.write(f"✅ {strength}")
        else:
            st.write("**🌟 Grammar Strengths:**")
            for strength in grammar_analysis['key_strengths']:
                st.write(f"✅ {strength}")

    if ai_used and grammar_analysis.get('key_issues'):
        if use_expanders:
            with st.expander("🔍 Grammar Issues to Address", expanded=False):
                for issue in grammar_analysis['key_issues']:
                    st.write(f"📝 {issue}")
        else:
            st.write("**🔍 Grammar Issues to Address:**")
            for issue in grammar_analysis['key_issues']:
                st.write(f"📝 {issue}")

    if ai_used and grammar_analysis.get('specific_suggestions'):
        if use_expanders:
            with st.expander("💡 Grammar Improvement Suggestions", expanded=False):
                for i, suggestion in enumerate(grammar_analysis['specific_suggestions'], 1):
                    st.write(f"{i}. {suggestion}")
        else:
            st.write("**💡 Grammar Improvement Suggestions:**")
            for i, suggestion in enumerate(grammar_analysis['specific_suggestions'], 1):
                st.write(f"{i}. {suggestion}")

    # Filter and display relevant grammar errors
    if grammar_analysis.get('local_errors'):
        # Filter out capitalization and other speech-irrelevant errors
        filtered_errors = []
        for error in grammar_analysis['local_errors']:
            error_message = error.get('message', '').lower()
            
            # Skip capitalization and other speech-irrelevant issues
            skip_patterns = [
                'uppercase letter',
                'capital letter',
                'capitalization',
                'does not start with an uppercase',
                'should be capitalized',
                'proper noun',
                'sentence case'
            ]
            
            # Check if this error should be skipped
            should_skip = any(pattern in error_message for pattern in skip_patterns)
            
            if not should_skip:
                filtered_errors.append(error)
        
        error_count = len(filtered_errors)
        
        if error_count > 0:
            if use_expanders:
                with st.expander(f"📋 Speech-Relevant Grammar Issues ({error_count})", expanded=False):
                    st.caption("Note: Capitalization and formatting issues are ignored for speech analysis")
                    
                    for i, error in enumerate(filtered_errors[:8]):
                        severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        emoji = severity_emoji.get(error.get('severity', 'low'), '🔵')
                        
                        st.markdown(f"""
                        <div style="
                            padding: 8px;
                            border-radius: 4px;
                            background: #f8f9fa;
                            border-left: 3px solid #666666;
                            margin: 4px 0;
                        ">
                            {emoji} <strong style="color: #000000;">Issue {i+1}:</strong> <span style="color: #000000;">{error['message']}</span><br>
                            <strong style="color: #000000;">Text:</strong> <span style="color: #000000;">"{error.get('error_text', 'N/A')}"</span><br>
                            {f'<strong style="color: #000000;">Suggestions:</strong> <span style="color: #000000;">{", ".join(error["suggestions"][:2])}</span>' if error.get('suggestions') else ""}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.write(f"**📋 Speech-Relevant Grammar Issues ({error_count}):**")
                st.caption("Note: Capitalization and formatting issues are ignored for speech analysis")
                
                for i, error in enumerate(filtered_errors[:8]):
                    severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    emoji = severity_emoji.get(error.get('severity', 'low'), '🔵')
                    
                    st.markdown(f"""
                    <div style="
                        padding: 8px;
                        border-radius: 4px;
                        background: #f8f9fa;
                        border-left: 3px solid #666666;
                        margin: 4px 0;
                    ">
                        {emoji} <strong style="color: #000000;">Issue {i+1}:</strong> <span style="color: #000000;">{error['message']}</span><br>
                        <strong style="color: #000000;">Text:</strong> <span style="color: #000000;">"{error.get('error_text', 'N/A')}"</span><br>
                        {f'<strong style="color: #000000;">Suggestions:</strong> <span style="color: #000000;">{", ".join(error["suggestions"][:2])}</span>' if error.get('suggestions') else ""}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ No speech-relevant grammar issues found!")

    # Grammar assessment (if available)
    if ai_used and grammar_analysis.get('interview_assessment'):
        st.info(f"🎯 **Grammar Assessment:** {grammar_analysis['interview_assessment']}")

    # Local-only suggestions (if no AI analysis)
    elif grammar_analysis.get('suggestions'):
        if use_expanders:
            with st.expander("💡 Grammar Suggestions", expanded=False):
                for suggestion in grammar_analysis['suggestions']:
                    st.write(f"• {suggestion}")
        else:
            st.write("**💡 Grammar Suggestions:**")
            for suggestion in grammar_analysis['suggestions']:
                st.write(f"• {suggestion}")

def display_evaluation_results(evaluation, question_type, context="main"):
    """
    Display answer evaluation results using Streamlit expanders for details.
    Fixed version to avoid session state conflicts.
    """
    # 1) Show top-level metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        final_score = evaluation.get('final_combined_score', 0)
        st.metric("Final Score", f"{final_score}/100")
    with col2:
        st.metric("Question Type", question_type)
    with col3:
        rubric_score = evaluation.get('rubric_score', 0)
        st.metric("Rubric Score", f"{rubric_score}/100")

    # 2) Get the rubric breakdown
    breakdown = evaluation.get('rubric_breakdown', {})
    scores_list = breakdown.get('scores', [])
    if not scores_list:
        return

    st.subheader("📊 Detailed Evaluation Breakdown")

    # 3) If in summary context, render each criterion as plain styled markdown
    if str(context).startswith("summary"):
        for i, criterion in enumerate(scores_list):
            # Styled heading
            st.markdown(
                f"""
                <div style="
                    padding: 12px;
                    border-radius: 8px;
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    margin-bottom: 8px;
                ">
                    <h4 style="margin: 0; font-size: 16px; color: #333;">
                        📋 {criterion['name']}: {criterion['score']}/100
                    </h4>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Explanation block
            st.markdown(
                f"""
                <div style="
                    padding: 12px;
                    border-radius: 6px;
                    background: #ffffff;
                    border-left: 4px solid #f0f2f5;
                    margin-bottom: 16px;
                ">
                    <p style="margin: 0; color: #555; line-height: 1.5;">
                        💬 <strong>Explanation:</strong> {criterion['explanation']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        # 4) For other contexts, use st.expander (no session state conflicts)
        for i, criterion in enumerate(scores_list):
            # Create unique expander labels
            expander_label = f"📋 {criterion['name']}: {criterion['score']}/100"
            
            with st.expander(expander_label, expanded=False):
                st.markdown(
                    f"""
                    <div style="
                        padding: 15px;
                        border-radius: 8px;
                        background: #f8f9fa;
                        border-left: 4px solid #667eea;
                        margin: 8px 0;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
                    ">
                        <p style="margin: 0; color: #333; line-height: 1.6;">
                            💬 <strong>Explanation:</strong> {criterion['explanation']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

def save_analysis_results(video_file, question, question_type, analysis_results):
    """Save analysis results to file"""
    try:
        evaluation_dir = Config.EVALUATION_DIR
        os.makedirs(evaluation_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_basename = os.path.basename(video_file).split('.')[0]

        results_data = {
            "timestamp": timestamp,
            "video_file": video_file,
            "question": question,
            "question_type": question_type,
            "emotion_analysis": analysis_results.get('emotion_analysis'),
            "transcript": analysis_results.get('transcript'),
            "grammar_analysis": analysis_results.get('grammar_analysis'),
            "answer_evaluation": analysis_results.get('answer_evaluation'),
            "aggregate_evaluation": analysis_results.get('aggregate_evaluation')
        }

        results_file = os.path.join(evaluation_dir, f"{video_basename}_analysis_{timestamp}.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        # Generate PDF report
        st.subheader("📊 Generate PDF Report")
        if st.button("🔄 Generate PDF Report", key="generate_pdf"):
            with st.spinner("📄 Generating PDF report..."):
                question_idx = st.session_state.get('current_question_idx', 1) + 1
                generate_and_download_pdf(analysis_results, question, question_type, question_idx)
        st.success(f"✅ Results saved to {results_file}")

    except Exception as e:
        st.error(f"❌ Error saving results: {str(e)}")

def show_complete_results():
    """Show complete interview results summary with aggregate scoring"""
    st.header("📊 Complete Interview Results Summary")

    # Top row with back button and PDF generation
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("⬅️ Back to Interview"):
            st.session_state.show_results = False
            st.rerun()
    
    with col2:
        # PDF Generation Button
        if st.button("📄 Generate Complete PDF Report", type="primary"):
            if st.session_state.analysis_results:
                with st.spinner("📄 Generating comprehensive PDF report..."):
                    generate_complete_interview_pdf()
            else:
                st.warning("No completed analyses found for PDF generation.")

    # If there are no analyses at all:
    if not st.session_state.analysis_results:
        st.warning("No completed analyses found.")
        return

    # ——————————————————————————————
    # 1) Overall statistics at the top
    total_questions = len(st.session_state.selected_questions)
    completed = len(st.session_state.completed_questions)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Questions", total_questions)
    with col2:
        st.metric("Completed", completed)
    with col3:
        completion_rate = (completed / total_questions) * 100 if total_questions > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")

    st.markdown("---")

    # ——————————————————————————————
    # 2) Calculate overall aggregate score across all questions
    all_aggregate_scores = []
    all_component_scores = {'emotion': [], 'grammar': [], 'answer': []}
    
    for idx, results in st.session_state.analysis_results.items():
        if results['results'].get('aggregate_evaluation'):
            agg_data = results['results']['aggregate_evaluation']
            all_aggregate_scores.append(agg_data['aggregate_score'])
            
            # Collect component scores
            breakdown = agg_data.get('breakdown', {})
            for component, score in breakdown.items():
                if component in all_component_scores:
                    all_component_scores[component].append(score)

    # Display overall performance
    if all_aggregate_scores:
        overall_avg = sum(all_aggregate_scores) / len(all_aggregate_scores)
        
        st.subheader("🏆 Overall Interview Performance")
        
        # Create overall aggregate display
        overall_aggregate = {
            'aggregate_score': round(overall_avg, 1),
            'breakdown': {comp: round(sum(scores)/len(scores), 1) if scores else 0 
                         for comp, scores in all_component_scores.items() if scores},
            'weights_used': {'emotion': 20, 'grammar': 25, 'answer': 55},
            'components_available': [comp for comp, scores in all_component_scores.items() if scores]
        }
        
        display_aggregate_results(overall_aggregate)
        st.markdown("---")

    # Original statistics (fallback for individual scores)
    scores = []
    grammar_scores = []
    
    for idx, results in st.session_state.analysis_results.items():
        eval_block = results['results'].get('answer_evaluation')
        if eval_block:
            scores.append(eval_block.get('final_combined_score', 0))
        
        # Grammar scores
        if results['results'].get('grammar_analysis'):
            grammar_score = results['results']['grammar_analysis'].get('grammar_score', 0)
            grammar_scores.append(grammar_score)

    # Show individual component averages if no aggregate available
    if not all_aggregate_scores:
        if scores:
            avg_score = sum(scores) / len(scores)
            st.subheader(f"🎯 Overall Performance: {avg_score:.1f}/100")
            if avg_score >= 80:
                st.success("🌟 Excellent performance!")
            elif avg_score >= 60:
                st.info("👍 Good performance!")
            else:
                st.warning("📈 Room for improvement!")

        if grammar_scores:
            avg_grammar = sum(grammar_scores) / len(grammar_scores)
            st.subheader(f"📝 Overall Grammar Performance: {avg_grammar:.1f}/100")
            
            if avg_grammar >= 85:
                st.success("🌟 Excellent grammar and communication!")
            elif avg_grammar >= 70:
                st.info("👍 Good grammar with minor areas for improvement!")
            elif avg_grammar >= 50:
                st.warning("📝 Grammar needs attention - focus on clarity and correctness!")
            else:
                st.error("❌ Grammar requires significant improvement!")

        st.markdown("---")

    # ——————————————————————————————
    # 3) Detailed results per question, each inside its own expander
    st.subheader("📝 Detailed Results by Question")

    # Sort keys so questions appear in order (0,1,2,…)
    for idx in sorted(st.session_state.analysis_results.keys()):
        results_data = st.session_state.analysis_results[idx]
        question = results_data['question']
        question_type = results_data['question_type']
        analysis = results_data['results']

        # Build a "preview" for the label (first 80 chars of the question)
        preview_text = question[:80] + ("..." if len(question) > 80 else "")

        # Because each label string is unique, we can safely omit `key=`.
        expander_label = f"📝 Question {idx + 1}: {question_type} — {preview_text}"
        with st.expander(expander_label, expanded=False):
            # Add individual PDF generation button for each question
            col1, col2 = st.columns([6, 1])
            with col2:
                if st.button("📄 PDF", key=f"pdf_q_{idx}", help="Generate PDF for this question"):
                    with st.spinner(f"Generating PDF for Question {idx + 1}..."):
                        generate_and_download_pdf(analysis, question, question_type, idx + 1)
            
            # ——————————————————–
            # 3.a) Show the full question text inside a styled container
            st.markdown(f"""
                <div style="
                    padding: 15px;
                    border-radius: 8px;
                    background: #f0f2f5;
                    border-left: 5px solid {'#1f77b4' if question_type == 'Technical' else '#ff7f0e'};
                    margin-bottom: 10px;
                ">
                    <p style="margin: 0; font-size: 16px; line-height: 1.5;">
                        <strong>Question {idx + 1} ({question_type}):</strong> {question}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Show aggregate results first if available
            if analysis.get('aggregate_evaluation'):
                display_aggregate_results(analysis['aggregate_evaluation'])
                st.markdown("---")

            # ——————————————————–
            # 3.b) Emotion Analysis (if available)
            if analysis.get('emotion_analysis'):
                st.subheader("🎭 Emotion Analysis Results")
                display_emotion_results(analysis['emotion_analysis'])
            else:
                st.info("ℹ️ Emotion analysis not available.")

            # ——————————————————–
            # 3.c) Transcript (if available)
            if analysis.get('transcript'):
                st.subheader("📝 Transcript")
                st.text_area(
                    label="Interview Transcript:",
                    value=analysis['transcript'],
                    height=200,
                    key=f"transcript_summary_{idx}"
                )
            else:
                st.info("ℹ️ Transcript not available.")

            # ——————————————————–
            # 3.d) Grammar Analysis (FIXED: use_expanders=False to avoid nesting)
            if analysis.get('grammar_analysis'):
                st.subheader("📝 Grammar & Communication Analysis")
                display_grammar_results(analysis['grammar_analysis'], use_expanders=False)
            else:
                st.info("ℹ️ Grammar analysis not available.")

            # ——————————————————–
            # 3.e) AI Answer Evaluation (if available)
            if analysis.get('answer_evaluation'):
                st.subheader("🤖 AI Answer Evaluation")
                # Pass a distinct context string so that any internal keys in
                # display_evaluation_results() remain unique per question.
                display_evaluation_results(
                    evaluation=analysis['answer_evaluation'],
                    question_type=question_type,
                    context=f"summary_{idx}"
                )
            else:
                st.info("ℹ️ Answer evaluation not available.")

            # Small spacer at the bottom
            st.markdown("<br>", unsafe_allow_html=True)

def generate_complete_interview_pdf():
    """Generate a comprehensive PDF report for all completed questions"""
    try:
        from components.pdf_report_generator import PDFReportGenerator
        
        # Initialize PDF generator
        pdf_generator = PDFReportGenerator()
        
        # Prepare comprehensive data
        all_results = st.session_state.analysis_results
        interview_summary = {
            'total_questions': len(st.session_state.selected_questions),
            'completed_questions': len(st.session_state.completed_questions),
            'completion_rate': (len(st.session_state.completed_questions) / len(st.session_state.selected_questions)) * 100,
            'questions_data': []
        }
        
        # Calculate overall statistics
        all_aggregate_scores = []
        all_component_scores = {'emotion': [], 'grammar': [], 'answer': []}
        
        for idx in sorted(all_results.keys()):
            results_data = all_results[idx]
            question = results_data['question']
            question_type = results_data['question_type']
            analysis = results_data['results']
            
            # Add to questions data
            interview_summary['questions_data'].append({
                'question_number': idx + 1,
                'question': question,
                'question_type': question_type,
                'analysis': analysis
            })
            
            # Collect aggregate scores
            if analysis.get('aggregate_evaluation'):
                agg_data = analysis['aggregate_evaluation']
                all_aggregate_scores.append(agg_data['aggregate_score'])
                
                breakdown = agg_data.get('breakdown', {})
                for component, score in breakdown.items():
                    if component in all_component_scores:
                        all_component_scores[component].append(score)
        
        # Calculate overall performance
        if all_aggregate_scores:
            overall_avg = sum(all_aggregate_scores) / len(all_aggregate_scores)
            interview_summary['overall_aggregate'] = {
                'aggregate_score': round(overall_avg, 1),
                'breakdown': {comp: round(sum(scores)/len(scores), 1) if scores else 0 
                             for comp, scores in all_component_scores.items() if scores},
                'weights_used': {'emotion': 20, 'grammar': 25, 'answer': 55},
                'components_available': [comp for comp, scores in all_component_scores.items() if scores]
            }
        
        # Generate comprehensive PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        candidate_id = f"CANDIDATE_{timestamp}"
        
        # Create a summary PDF (you'll need to implement this method in PDFReportGenerator)
        pdf_path = pdf_generator.generate_complete_interview_report(
            interview_summary,
            candidate_id=candidate_id
        )
        
        # Provide download link
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.success("📄 Complete Interview PDF Report Generated Successfully!")
            
            # Create download button
            filename = os.path.basename(pdf_path)
            st.download_button(
                label="📥 Download Complete Interview Report",
                data=pdf_bytes,
                file_name=f"Complete_Interview_Report_{timestamp}.pdf",
                mime="application/pdf",
                key="download_complete_pdf"
            )
            
            # Show summary info
            st.info(f"📊 Report includes {len(interview_summary['questions_data'])} questions with comprehensive analysis")
            
        else:
            st.error("❌ Failed to generate complete PDF report")
            
    except ImportError:
        st.error("❌ PDF generator not available. Please ensure pdf_report_generator.py is properly configured.")
    except Exception as e:
        st.error(f"❌ Error generating complete PDF: {str(e)}")

def main():
    # Configure page
    st.set_page_config(
        page_title="AI Interview System",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Create directories
    Config.create_directories()

    # Check file availability
    model_files_available = Config.verify_model_files()
    evaluation_files_available = Config.verify_evaluation_files()

    # Show missing files info if needed
    if not model_files_available or not evaluation_files_available:
        with st.expander("⚠️ Missing Files Information", expanded=False):
            show_missing_files_info()

    # Create sidebar
    create_sidebar()

    # Main content area
    with st.container():
        create_main_content()


if __name__ == "__main__":
    main()