# Video Interview System

This project is a video interview system designed to facilitate the recording of candidates' responses to interview questions, analyze their emotions, and transcribe their audio. The system leverages various components to ensure a smooth and efficient interview process.

## Features

- **Video Recording**: Candidates can record their responses to predefined questions.
- **Emotion Analysis**: The system analyzes the emotions expressed by candidates during their responses.
- **Audio Transcription**: The audio from the video recordings is transcribed into text for further review.

## Project Structure

```
video-interview-system
├── src
│   ├── app.py                  # Main entry point for the Streamlit application
│   ├── components               # Contains components for video recording, emotion analysis, and transcription
│   │   ├── video_recorder.py    # Handles video recording functionality
│   │   ├── emotion_analyzer.py   # Implements emotion analysis logic
│   │   └── transcription.py       # Manages audio transcription
│   ├── utils                    # Utility functions for video and audio processing
│   │   ├── video_processing.py    # Video processing utilities
│   │   └── audio_processing.py    # Audio processing utilities
│   └── models                   # Contains models for emotion classification
│       └── emotion_model.py      # Logic for loading and preprocessing the emotion model
├── data
│   ├── recordings               # Directory for storing recorded video files
│   └── transcripts              # Directory for storing generated transcripts
├── config
│   └── settings.py             # Configuration settings for the application
├── requirements.txt            # Lists dependencies required for the project
└── README.md                   # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd video-interview-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `config/settings.py` as needed.

4. Run the application:
   ```
   streamlit run src/app.py
   ```

## Usage Guidelines

- Upon running the application, candidates will be prompted to answer three predefined questions.
- The system will record the video, analyze emotions, and transcribe the audio automatically.
- Recorded videos and transcripts will be saved in the respective directories for review.

## Acknowledgments

This project utilizes various libraries and models for video processing, emotion analysis, and transcription. Special thanks to the contributors of these libraries for their invaluable work.