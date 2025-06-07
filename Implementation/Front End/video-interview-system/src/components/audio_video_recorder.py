# import cv2
# import streamlit as st
# import os
# import threading
# import time
# import numpy as np
# import sounddevice as sd
# import wave
# from datetime import datetime
# from moviepy.editor import VideoFileClip, AudioFileClip

# class AudioVideoRecorder:
#     def __init__(self):
#         self.recording = False
#         self.cap = None
#         self.output_path = None
#         self.preview_active = False
#         self.audio_frames = []
#         self.video_frames = []
#         self.sample_rate = 16000
#         self.video_thread = None
#         self.audio_thread = None
        
#     def start_preview(self):
#         """Start camera preview without recording"""
#         try:
#             if self.cap is None:
#                 self.cap = cv2.VideoCapture(0)
                
#             if not self.cap.isOpened():
#                 st.error("❌ Cannot access camera. Please check camera permissions.")
#                 return False
            
#             # Set camera properties
#             self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#             self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#             self.cap.set(cv2.CAP_PROP_FPS, 20)
            
#             self.preview_active = True
#             return True
            
#         except Exception as e:
#             st.error(f"❌ Error starting preview: {e}")
#             return False
    
#     def get_frame(self):
#         """Get current frame from camera"""
#         if self.cap and self.cap.isOpened():
#             ret, frame = self.cap.read()
#             if ret:
#                 return frame
#         return None
    
#     def stop_preview(self):
#         """Stop camera preview"""
#         self.preview_active = False
#         if self.cap and not self.recording:
#             self.cap.release()
#             self.cap = None
    
#     def start_recording(self, duration=60):
#         """Start recording video and audio"""
#         try:
#             # Generate output paths
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             os.makedirs("data/recordings", exist_ok=True)
            
#             self.video_path = f"data/recordings/temp_video_{timestamp}.mp4"
#             self.audio_path = f"data/recordings/temp_audio_{timestamp}.wav"
#             self.output_path = f"data/recordings/interview_{timestamp}.mp4"
            
#             # Initialize camera if not already done
#             if self.cap is None:
#                 self.cap = cv2.VideoCapture(0)
            
#             if not self.cap.isOpened():
#                 st.error("❌ Cannot access camera.")
#                 return None
            
#             # Reset recording data
#             self.audio_frames = []
#             self.recording = True
            
#             # Start video recording thread
#             self.video_thread = threading.Thread(target=self._record_video, args=(duration,))
#             self.video_thread.daemon = True
#             self.video_thread.start()
            
#             # Start audio recording thread
#             self.audio_thread = threading.Thread(target=self._record_audio, args=(duration,))
#             self.audio_thread.daemon = True
#             self.audio_thread.start()
            
#             return self.output_path
            
#         except Exception as e:
#             st.error(f"❌ Error starting recording: {e}")
#             return None
    
#     def _record_video(self, duration):
#         """Record video frames"""
#         try:
#             fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#             out = cv2.VideoWriter(self.video_path, fourcc, 20.0, (640, 480))
            
#             start_time = time.time()
#             frame_count = 0
            
#             while self.recording and (time.time() - start_time) < duration:
#                 ret, frame = self.cap.read()
#                 if ret:
#                     out.write(frame)
#                     frame_count += 1
#                 time.sleep(0.05)  # ~20 FPS
            
#             out.release()
#             print(f"Video: Recorded {frame_count} frames")
            
#         except Exception as e:
#             print(f"Video recording error: {e}")
    
#     def _record_audio(self, duration):
#         """Record audio"""
#         try:
#             def audio_callback(indata, frames, time, status):
#                 if self.recording:
#                     self.audio_frames.append(indata.copy())
            
#             with sd.InputStream(samplerate=self.sample_rate, 
#                               channels=1, 
#                               callback=audio_callback):
#                 time.sleep(duration)
            
#             # Save audio to file
#             if self.audio_frames:
#                 audio_data = np.concatenate(self.audio_frames, axis=0)
                
#                 with wave.open(self.audio_path, 'wb') as wf:
#                     wf.setnchannels(1)
#                     wf.setsampwidth(2)
#                     wf.setframerate(self.sample_rate)
#                     wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                
#                 print(f"Audio: Saved {len(self.audio_frames)} chunks")
            
#         except Exception as e:
#             print(f"Audio recording error: {e}")
    
#     def stop_recording(self):
#         """Stop recording and combine audio/video"""
#         self.recording = False
        
#         # Wait for threads to finish
#         if self.video_thread and self.video_thread.is_alive():
#             self.video_thread.join(timeout=5)
#         if self.audio_thread and self.audio_thread.is_alive():
#             self.audio_thread.join(timeout=5)
        
#         # Combine audio and video
#         try:
#             if os.path.exists(self.video_path) and os.path.exists(self.audio_path):
#                 self._combine_av()
                
#                 # Clean up temp files
#                 if os.path.exists(self.video_path):
#                     os.remove(self.video_path)
#                 if os.path.exists(self.audio_path):
#                     os.remove(self.audio_path)
                
#                 return self.output_path if os.path.exists(self.output_path) else None
#             else:
#                 print("Missing video or audio file")
#                 return None
                
#         except Exception as e:
#             print(f"Error combining files: {e}")
#             return None
    
#     def _combine_av(self):
#         """Combine video and audio using moviepy"""
#         try:
#             print("Combining audio and video...")
            
#             video_clip = VideoFileClip(self.video_path)
#             audio_clip = AudioFileClip(self.audio_path)
            
#             # Make sure audio and video have same duration
#             min_duration = min(video_clip.duration, audio_clip.duration)
#             video_clip = video_clip.subclip(0, min_duration)
#             audio_clip = audio_clip.subclip(0, min_duration)
            
#             # Combine
#             final_clip = video_clip.set_audio(audio_clip)
#             final_clip.write_videofile(self.output_path, 
#                                      codec='libx264', 
#                                      audio_codec='aac',
#                                      verbose=False,
#                                      logger=None)
            
#             # Clean up
#             video_clip.close()
#             audio_clip.close()
#             final_clip.close()
            
#             print(f"Combined video saved to: {self.output_path}")
            
#         except Exception as e:
#             print(f"Error combining audio/video: {e}")
#             raise
    
#     def release(self):
#         """Release all resources"""
#         self.recording = False
#         self.preview_active = False
        
#         if self.cap:
#             self.cap.release()
#         self.cap = None


import cv2
import streamlit as st
import os
import threading
import time
import numpy as np
import sounddevice as sd
import wave
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip

class AudioVideoRecorder:
    def __init__(self):
        self.recording = False
        self.cap = None
        self.output_path = None
        self.preview_active = False
        self.audio_frames = []
        self.video_frames = []
        self.sample_rate = 16000
        self.video_thread = None
        self.audio_thread = None
        # Question-specific tracking
        self.current_question_id = None
        self.question_recordings = {}  # Store recordings per question
        
    def start_preview(self):
        """Start camera preview without recording"""
        try:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                
            if not self.cap.isOpened():
                st.error("❌ Cannot access camera. Please check camera permissions.")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 20)
            
            self.preview_active = True
            return True
            
        except Exception as e:
            st.error(f"❌ Error starting preview: {e}")
            return False
    
    def get_frame(self):
        """Get current frame from camera"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def stop_preview(self):
        """Stop camera preview"""
        self.preview_active = False
        if self.cap and not self.recording:
            self.cap.release()
            self.cap = None
    
    def start_recording(self, duration=60, question_id=None):
        """Start recording video and audio for a specific question"""
        try:
            # Set current question ID
            self.current_question_id = question_id or 0
            
            # Generate question-specific output paths
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("data/recordings", exist_ok=True)
            
            # Include question ID in filename
            question_suffix = f"_q{self.current_question_id}" if self.current_question_id is not None else ""
            
            self.video_path = f"data/recordings/temp_video{question_suffix}_{timestamp}.mp4"
            self.audio_path = f"data/recordings/temp_audio{question_suffix}_{timestamp}.wav"
            self.output_path = f"data/recordings/interview{question_suffix}_{timestamp}.mp4"
            
            # Initialize camera if not already done
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                st.error("❌ Cannot access camera.")
                return None
            
            # Reset recording data
            self.audio_frames = []
            self.recording = True
            
            # Start video recording thread
            self.video_thread = threading.Thread(target=self._record_video, args=(duration,))
            self.video_thread.daemon = True
            self.video_thread.start()
            
            # Start audio recording thread
            self.audio_thread = threading.Thread(target=self._record_audio, args=(duration,))
            self.audio_thread.daemon = True
            self.audio_thread.start()
            
            return self.output_path
            
        except Exception as e:
            st.error(f"❌ Error starting recording: {e}")
            return None
    
    def _record_video(self, duration):
        """Record video frames"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.video_path, fourcc, 20.0, (640, 480))
            
            start_time = time.time()
            frame_count = 0
            
            while self.recording and (time.time() - start_time) < duration:
                ret, frame = self.cap.read()
                if ret:
                    out.write(frame)
                    frame_count += 1
                time.sleep(0.05)  # ~20 FPS
            
            out.release()
            print(f"Video: Recorded {frame_count} frames for question {self.current_question_id}")
            
        except Exception as e:
            print(f"Video recording error: {e}")
    
    def _record_audio(self, duration):
        """Record audio"""
        try:
            def audio_callback(indata, frames, time, status):
                if self.recording:
                    self.audio_frames.append(indata.copy())
            
            with sd.InputStream(samplerate=self.sample_rate, 
                              channels=1, 
                              callback=audio_callback):
                start_time = time.time()
                while self.recording and (time.time() - start_time) < duration:
                    time.sleep(0.1)
            
            # Save audio to file
            if self.audio_frames:
                audio_data = np.concatenate(self.audio_frames, axis=0)
                
                with wave.open(self.audio_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                
                print(f"Audio: Saved {len(self.audio_frames)} chunks for question {self.current_question_id}")
            
        except Exception as e:
            print(f"Audio recording error: {e}")
    
    def stop_recording(self):
        """Stop recording and combine audio/video"""
        self.recording = False
        
        # Wait for threads to finish
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=5)
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=5)
        
        # Combine audio and video
        try:
            if os.path.exists(self.video_path) and os.path.exists(self.audio_path):
                self._combine_av()
                
                # Store the recording for this question
                if self.current_question_id is not None and os.path.exists(self.output_path):
                    self.question_recordings[self.current_question_id] = {
                        'file_path': self.output_path,
                        'timestamp': datetime.now(),
                        'duration': self._get_video_duration(self.output_path)
                    }
                
                # Clean up temp files
                if os.path.exists(self.video_path):
                    os.remove(self.video_path)
                if os.path.exists(self.audio_path):
                    os.remove(self.audio_path)
                
                return self.output_path if os.path.exists(self.output_path) else None
            else:
                print("Missing video or audio file")
                return None
                
        except Exception as e:
            print(f"Error combining files: {e}")
            return None
    
    def _combine_av(self):
        """Combine video and audio using moviepy"""
        try:
            print(f"Combining audio and video for question {self.current_question_id}...")
            
            video_clip = VideoFileClip(self.video_path)
            audio_clip = AudioFileClip(self.audio_path)
            
            # Make sure audio and video have same duration
            min_duration = min(video_clip.duration, audio_clip.duration)
            video_clip = video_clip.subclip(0, min_duration)
            audio_clip = audio_clip.subclip(0, min_duration)
            
            # Combine
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(self.output_path, 
                                     codec='libx264', 
                                     audio_codec='aac',
                                     verbose=False,
                                     logger=None)
            
            # Clean up
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            
            print(f"Combined video saved to: {self.output_path}")
            
        except Exception as e:
            print(f"Error combining audio/video: {e}")
            raise
    
    def _get_video_duration(self, video_path):
        """Get video duration in seconds"""
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except:
            return 0
    
    def get_question_recording(self, question_id):
        """Get recording file path for a specific question"""
        if question_id in self.question_recordings:
            recording_info = self.question_recordings[question_id]
            if os.path.exists(recording_info['file_path']):
                return recording_info['file_path']
        return None
    
    def has_question_recording(self, question_id):
        """Check if a specific question has been recorded"""
        recording_path = self.get_question_recording(question_id)
        return recording_path is not None and os.path.exists(recording_path)
    
    def get_all_recordings(self):
        """Get all question recordings"""
        valid_recordings = {}
        for question_id, recording_info in self.question_recordings.items():
            if os.path.exists(recording_info['file_path']):
                valid_recordings[question_id] = recording_info
        return valid_recordings
    
    def delete_question_recording(self, question_id):
        """Delete recording for a specific question"""
        if question_id in self.question_recordings:
            recording_info = self.question_recordings[question_id]
            file_path = recording_info['file_path']
            
            # Delete the file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted recording for question {question_id}: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            
            # Remove from tracking
            del self.question_recordings[question_id]
            return True
        return False
    
    def clear_all_recordings(self):
        """Clear all question recordings"""
        for question_id in list(self.question_recordings.keys()):
            self.delete_question_recording(question_id)
        self.question_recordings.clear()
    def get_recording_status(self, question_id):
        """Get recording status for a specific question"""
        if self.has_question_recording(question_id):
            recording_info = self.question_recordings[question_id]
            return {
                'recorded': True,
                'file_path': recording_info['file_path'],
                'timestamp': recording_info['timestamp'],
                'duration': recording_info.get('duration', 0),
                'file_size': os.path.getsize(recording_info['file_path']) if os.path.exists(recording_info['file_path']) else 0
            }
        else:
            return {
                'recorded': False,
                'file_path': None,
                'timestamp': None,
                'duration': 0,
                'file_size': 0
            }
    
    def is_currently_recording(self):
        """Check if currently recording"""
        return self.recording
    
    def get_current_recording_question(self):
        """Get the question ID currently being recorded"""
        if self.recording:
            return self.current_question_id
        return None
    
    def release(self):
        """Release all resources"""
        self.recording = False
        self.preview_active = False
        
        if self.cap:
            self.cap.release()
        self.cap = None
        
        # Wait for threads to finish
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2)
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2)