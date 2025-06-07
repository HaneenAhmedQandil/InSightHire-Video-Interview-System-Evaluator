import cv2
import streamlit as st
import os
import threading
import time
from datetime import datetime

class SimpleVideoRecorder:
    def __init__(self):
        self.recording = False
        self.cap = None
        self.out = None
        self.output_path = None
        self.record_thread = None
        self.preview_active = False
        
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
        
    def start_recording(self, duration=60):
        """Start recording from webcam"""
        try:
            # Generate output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("data/recordings", exist_ok=True)
            self.output_path = f"data/recordings/interview_{timestamp}.mp4"
            
            # Initialize camera if not already done
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                st.error("❌ Cannot access camera. Please check camera permissions.")
                return None
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 20)
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.out = cv2.VideoWriter(self.output_path, fourcc, 20.0, (640, 480))
            
            self.recording = True
            
            # Start recording in background thread
            self.record_thread = threading.Thread(target=self._record_frames, args=(duration,))
            self.record_thread.daemon = True
            self.record_thread.start()
            
            return self.output_path
            
        except Exception as e:
            st.error(f"❌ Error starting recording: {e}")
            return None
    
    def _record_frames(self, duration):
        """Record frames in background thread"""
        start_time = time.time()
        frame_count = 0
        
        while self.recording and (time.time() - start_time) < duration:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
                frame_count += 1
            time.sleep(0.05)  # ~20 FPS
        
        print(f"Recorded {frame_count} frames")
        # Don't call stop_recording from within the thread
        self._cleanup()
    
    def _cleanup(self):
        """Internal cleanup method"""
        self.recording = False
        if self.out:
            self.out.release()
            self.out = None
    
    def stop_recording(self):
        """Stop recording and clean up"""
        self.recording = False
        
        # Wait for thread to finish if it's not the current thread
        if self.record_thread and self.record_thread.is_alive() and threading.current_thread() != self.record_thread:
            self.record_thread.join(timeout=2)
        
        # Clean up resources
        if self.out:
            self.out.release()
            self.out = None
        
        return self.output_path if self.output_path and os.path.exists(self.output_path) else None
    
    def release(self):
        """Release all resources"""
        self.recording = False
        self.preview_active = False
        
        if self.out:
            self.out.release()
        if self.cap:
            self.cap.release()
        
        self.out = None
        self.cap = None