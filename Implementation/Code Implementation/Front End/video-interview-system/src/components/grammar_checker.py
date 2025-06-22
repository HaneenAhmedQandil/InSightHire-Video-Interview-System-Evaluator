# # # import language_tool_python
# # # import openai
# # # import json
# # # import re
# # # import time
# # # from typing import Dict, List, Optional
# # # import streamlit as st
# # # from config.settings import Config

# # # class HybridGrammarChecker:
# # #     def __init__(self):
# # #         """Initialize hybrid grammar checker with both local and AI capabilities"""
# # #         # Initialize LanguageTool (always available)
# # #         try:
# # #             self.language_tool = language_tool_python.LanguageTool('en-US')
# # #             self.local_available = True
# # #         except Exception as e:
# # #             print(f"Warning: LanguageTool initialization failed: {e}")
# # #             self.language_tool = None
# # #             self.local_available = False
        
# # #         # Initialize OpenAI client (optional)
# # #         self.ai_available = False
# # #         if Config.is_openai_available():
# # #             try:
# # #                 self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
# # #                 # Test the connection
# # #                 self._test_openai_connection()
# # #                 self.ai_available = True
# # #             except Exception as e:
# # #                 print(f"Warning: OpenAI initialization failed: {e}")
# # #                 self.openai_client = None
    
# # #     def _test_openai_connection(self):
# # #         """Test OpenAI API connection"""
# # #         try:
# # #             response = self.openai_client.chat.completions.create(
# # #                 model=Config.OPENAI_MODEL,
# # #                 messages=[{"role": "user", "content": "Test"}],
# # #                 max_tokens=1
# # #             )
# # #             return True
# # #         except Exception as e:
# # #             print(f"OpenAI connection test failed: {e}")
# # #             return False
    
# # #     def check_grammar(self, text: str, force_ai: bool = False) -> Dict:
# # #         """
# # #         Comprehensive grammar check using hybrid approach
        
# # #         Args:
# # #             text: Text to analyze
# # #             force_ai: Force AI analysis regardless of conditions
            
# # #         Returns:
# # #             Detailed grammar analysis results
# # #         """
# # #         if not text or not text.strip():
# # #             return self._empty_result()
        
# # #         # Clean and prepare text
# # #         cleaned_text = self._clean_text(text)
# # #         word_count = len(cleaned_text.split())
        
# # #         if word_count < 5:  # Too short for meaningful analysis
# # #             return self._minimal_result(cleaned_text, word_count)
        
# # #         # Step 1: Local grammar check (LanguageTool)
# # #         local_results = self._check_with_language_tool(cleaned_text)
        
# # #         # Step 2: Decide if AI analysis is needed
# # #         use_ai = force_ai or self._should_use_ai(cleaned_text, local_results, word_count)
        
# # #         # Step 3: Enhanced AI analysis if conditions are met
# # #         if use_ai and self.ai_available:
# # #             try:
# # #                 ai_results = self._check_with_openai(cleaned_text, local_results)
# # #                 return self._merge_results(local_results, ai_results, cleaned_text)
# # #             except Exception as e:
# # #                 st.warning(f"AI analysis failed, using local results: {str(e)}")
# # #                 return self._finalize_local_results(local_results, cleaned_text)
        
# # #         return self._finalize_local_results(local_results, cleaned_text)
    
# # #     def _clean_text(self, text: str) -> str:
# # #         """Clean and normalize text for analysis"""
# # #         # Remove extra whitespace
# # #         text = re.sub(r'\s+', ' ', text.strip())
        
# # #         # Remove common speech filler words
# # #         fillers = [r'\buh+\b', r'\bum+\b', r'\ber+\b', r'\blike\b(?=\s+\w)', r'\byou know\b']
# # #         for filler in fillers:
# # #             text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
# # #         # Clean up punctuation spacing
# # #         text = re.sub(r'\s+([.!?])', r'\1', text)
# # #         text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
# # #         return text.strip()
    
# # #     def _check_with_language_tool(self, text: str) -> Dict:
# # #         """Perform grammar check using LanguageTool"""
# # #         if not self.local_available:
# # #             return {'errors': [], 'error_count': 0, 'available': False}
        
# # #         try:
# # #             matches = self.language_tool.check(text)
# # #             errors = []
            
# # #             for match in matches:
# # #                 error = {
# # #                     'category': match.category,
# # #                     'rule_id': match.ruleId,
# # #                     'message': match.message,
# # #                     'offset': match.offset,
# # #                     'length': match.errorLength,
# # #                     'context': match.context,
# # #                     'suggestions': match.replacements[:3] if match.replacements else [],
# # #                     'error_text': text[match.offset:match.offset + match.errorLength],
# # #                     'severity': self._categorize_error_severity(match.category)
# # #                 }
# # #                 errors.append(error)
            
# # #             return {
# # #                 'errors': errors,
# # #                 'error_count': len(errors),
# # #                 'corrected_text': self.language_tool.correct(text),
# # #                 'available': True
# # #             }
            
# # #         except Exception as e:
# # #             print(f"LanguageTool error: {e}")
# # #             return {'errors': [], 'error_count': 0, 'available': False}
    
# # #     def _categorize_error_severity(self, category: str) -> str:
# # #         """Categorize error severity"""
# # #         high_severity = ['GRAMMAR', 'TYPOS']
# # #         medium_severity = ['STYLE', 'REDUNDANCY']
        
# # #         if category in high_severity:
# # #             return 'high'
# # #         elif category in medium_severity:
# # #             return 'medium'
# # #         else:
# # #             return 'low'
    
# # #     def _should_use_ai(self, text: str, local_results: Dict, word_count: int) -> bool:
# # #         """Intelligent decision on when to use AI analysis"""
# # #         if not Config.GRAMMAR_AI_AUTO_TRIGGER:
# # #             return False
        
# # #         # Conditions for AI analysis
# # #         conditions = [
# # #             word_count >= Config.GRAMMAR_AI_THRESHOLD,  # Sufficient text length
# # #             local_results.get('error_count', 0) / word_count > Config.AI_TRIGGER_ERROR_RATE,  # High error rate
# # #             word_count > 50,  # Longer responses get AI analysis
# # #         ]
        
# # #         return any(conditions)
    
# # #     def _check_with_openai(self, text: str, local_results: Dict) -> Dict:
# # #         """Enhanced grammar and communication analysis using OpenAI"""
# # #         error_count = local_results.get('error_count', 0)
# # #         word_count = len(text.split())
        
# # #         prompt = f"""
# # # As an expert English language assessor evaluating interview responses, analyze this text for professional communication quality.

# # # TEXT TO ANALYZE: "{text}"

# # # CONTEXT:
# # # - This is from a job interview response
# # # - Local grammar tool found {error_count} potential issues in {word_count} words
# # # - Focus on professional communication standards

# # # Provide analysis in this exact JSON format:
# # # {{
# # #     "grammar_score": <0-100 integer>,
# # #     "professionalism_score": <0-100 integer>,
# # #     "clarity_score": <0-100 integer>,
# # #     "coherence_score": <0-100 integer>,
# # #     "key_strengths": ["strength1", "strength2"],
# # #     "key_issues": ["issue1", "issue2"],
# # #     "specific_suggestions": ["actionable suggestion1", "actionable suggestion2"],
# # #     "interview_assessment": "brief assessment of interview readiness",
# # #     "overall_impression": "positive/neutral/needs_improvement"
# # # }}

# # # Focus on:
# # # 1. Grammar and syntax correctness
# # # 2. Professional tone and vocabulary
# # # 3. Clarity of communication
# # # 4. Logical flow and coherence
# # # 5. Interview appropriateness

# # # Be constructive and specific in feedback.
# # # """

# # #         try:
# # #             response = self.openai_client.chat.completions.create(
# # #                 model=Config.OPENAI_MODEL,
# # #                 messages=[{"role": "user", "content": prompt}],
# # #                 temperature=0.1,
# # #                 max_tokens=800
# # #             )
            
# # #             content = response.choices[0].message.content.strip()
            
# # #             # Try to parse JSON, with fallback
# # #             try:
# # #                 ai_analysis = json.loads(content)
# # #                 return ai_analysis
# # #             except json.JSONDecodeError:
# # #                 # Fallback parsing if JSON is malformed
# # #                 return self._parse_ai_response_fallback(content)
                
# # #         except Exception as e:
# # #             print(f"OpenAI API error: {e}")
# # #             raise e
    
# # #     def _parse_ai_response_fallback(self, content: str) -> Dict:
# # #         """Fallback parser for non-JSON AI responses"""
# # #         return {
# # #             "grammar_score": 75,
# # #             "professionalism_score": 75,
# # #             "clarity_score": 75,
# # #             "coherence_score": 75,
# # #             "key_strengths": ["Analysis completed"],
# # #             "key_issues": ["Could not parse detailed feedback"],
# # #             "specific_suggestions": ["Review response format"],
# # #             "interview_assessment": "AI analysis parsing error occurred",
# # #             "overall_impression": "neutral"
# # #         }
    
# # #     def _merge_results(self, local_results: Dict, ai_results: Dict, text: str) -> Dict:
# # #         """Merge local and AI analysis results"""
# # #         word_count = len(text.split())
# # #         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
        
# # #         # Calculate comprehensive scores
# # #         grammar_score = self._calculate_final_grammar_score(local_results, ai_results, word_count)
        
# # #         return {
# # #             # Core metrics
# # #             'grammar_score': grammar_score,
# # #             'professionalism_score': ai_results.get('professionalism_score', 75),
# # #             'clarity_score': ai_results.get('clarity_score', 75),
# # #             'coherence_score': ai_results.get('coherence_score', 75),
            
# # #             # Detailed analysis
# # #             'local_errors': local_results.get('errors', []),
# # #             'error_count': local_results.get('error_count', 0),
# # #             'word_count': word_count,
# # #             'sentence_count': sentence_count,
            
# # #             # AI insights
# # #             'key_strengths': ai_results.get('key_strengths', []),
# # #             'key_issues': ai_results.get('key_issues', []),
# # #             'specific_suggestions': ai_results.get('specific_suggestions', []),
# # #             'interview_assessment': ai_results.get('interview_assessment', ''),
# # #             'overall_impression': ai_results.get('overall_impression', 'neutral'),
            
# # #             # Additional data
# # #             'corrected_text': local_results.get('corrected_text', text),
# # #             'original_text': text,
# # #             'analysis_type': 'hybrid',
# # #             'ai_used': True
# # #         }
    
# # #     def _finalize_local_results(self, local_results: Dict, text: str) -> Dict:
# # #         """Finalize results using only local analysis"""
# # #         word_count = len(text.split())
# # #         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
# # #         error_count = local_results.get('error_count', 0)
        
# # #         # Calculate scores based on local analysis
# # #         grammar_score = self._calculate_local_grammar_score(error_count, word_count)
# # #         readability_score = self._calculate_readability_score(text, word_count, sentence_count)
        
# # #         return {
# # #             # Core metrics
# # #             'grammar_score': grammar_score,
# # #             'readability_score': readability_score,
# # #             'professionalism_score': min(grammar_score + 5, 100),  # Estimate
# # #             'clarity_score': readability_score,
            
# # #             # Detailed analysis
# # #             'local_errors': local_results.get('errors', []),
# # #             'error_count': error_count,
# # #             'word_count': word_count,
# # #             'sentence_count': sentence_count,
            
# # #             # Generated insights
# # #             'suggestions': self._generate_local_suggestions(local_results, grammar_score),
# # #             'overall_assessment': self._generate_local_assessment(grammar_score, readability_score, error_count),
            
# # #             # Additional data
# # #             'corrected_text': local_results.get('corrected_text', text),
# # #             'original_text': text,
# # #             'analysis_type': 'local_only',
# # #             'ai_used': False
# # #         }
    
# # #     def _calculate_final_grammar_score(self, local_results: Dict, ai_results: Dict, word_count: int) -> float:
# # #         """Calculate final grammar score combining local and AI analysis"""
# # #         # Weight local error-based score and AI assessment
# # #         local_score = self._calculate_local_grammar_score(local_results.get('error_count', 0), word_count)
# # #         ai_score = ai_results.get('grammar_score', local_score)
        
# # #         # Weighted average (favor AI slightly for final score)
# # #         final_score = (local_score * 0.4) + (ai_score * 0.6)
# # #         return round(final_score, 1)
    
# # #     def _calculate_local_grammar_score(self, error_count: int, word_count: int) -> float:
# # #         """Calculate grammar score based on error rate"""
# # #         if word_count == 0:
# # #             return 0
        
# # #         error_rate = error_count / word_count
# # #         # More forgiving scoring for interview context
# # #         penalty = min(error_rate * 200, 50)  # Max 50 point penalty
# # #         score = max(100 - penalty, 20)  # Minimum score of 20
        
# # #         return round(score, 1)
    
# # #     def _calculate_readability_score(self, text: str, word_count: int, sentence_count: int) -> float:
# # #         """Calculate readability score"""
# # #         if sentence_count == 0 or word_count == 0:
# # #             return 0
        
# # #         avg_sentence_length = word_count / sentence_count
        
# # #         # Optimal range for interview responses: 10-20 words per sentence
# # #         if 10 <= avg_sentence_length <= 20:
# # #             sentence_score = 100
# # #         else:
# # #             deviation = abs(avg_sentence_length - 15)
# # #             sentence_score = max(60, 100 - (deviation * 3))
        
# # #         return round(sentence_score, 1)
    
# # #     def _generate_local_suggestions(self, local_results: Dict, grammar_score: float) -> List[str]:
# # #         """Generate suggestions based on local analysis"""
# # #         suggestions = []
# # #         errors = local_results.get('errors', [])
        
# # #         # Grammar-specific suggestions
# # #         if grammar_score < 70:
# # #             suggestions.append("Focus on basic grammar rules and sentence structure")
        
# # #         # Error category-based suggestions
# # #         error_categories = [error.get('category', '') for error in errors]
# # #         if 'GRAMMAR' in error_categories:
# # #             suggestions.append("Double-check verb tenses and subject-verb agreement")
# # #         if 'STYLE' in error_categories:
# # #             suggestions.append("Consider improving sentence flow and word choice")
# # #         if 'TYPOS' in error_categories:
# # #             suggestions.append("Proofread carefully to catch spelling errors")
        
# # #         return suggestions[:4]  # Limit suggestions
    
# # #     def _generate_local_assessment(self, grammar_score: float, readability_score: float, error_count: int) -> str:
# # #         """Generate overall assessment based on local analysis"""
# # #         avg_score = (grammar_score + readability_score) / 2
        
# # #         if avg_score >= 85:
# # #             return f"Excellent language quality! Grammar: {grammar_score}/100, Readability: {readability_score}/100"
# # #         elif avg_score >= 70:
# # #             return f"Good communication with minor issues. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
# # #         elif avg_score >= 50:
# # #             return f"Adequate communication with room for improvement. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
# # #         else:
# # #             return f"Communication needs significant improvement. Focus on grammar and clarity. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
    
# # #     def _empty_result(self) -> Dict:
# # #         """Return empty result for no text"""
# # #         return {
# # #             'grammar_score': 0,
# # #             'error_count': 0,
# # #             'word_count': 0,
# # #             'overall_assessment': "No text provided for analysis",
# # #             'analysis_type': 'empty',
# # #             'ai_used': False
# # #         }
    
# # #     def _minimal_result(self, text: str, word_count: int) -> Dict:
# # #         """Return minimal result for very short text"""
# # #         return {
# # #             'grammar_score': 85,  # Assume good for very short responses
# # #             'error_count': 0,
# # #             'word_count': word_count,
# # #             'original_text': text,
# # #             'overall_assessment': f"Response too short ({word_count} words) for detailed analysis",
# # #             'analysis_type': 'minimal',
# # #             'ai_used': False
# # #         }

# # #     def get_analysis_summary(self) -> Dict:
# # #         """Get summary of checker capabilities"""
# # #         return {
# # #             'local_available': self.local_available,
# # #             'ai_available': self.ai_available,
# # #             'hybrid_mode': self.local_available and self.ai_available,
# # #             'recommended_min_words': Config.GRAMMAR_AI_THRESHOLD
# # #         }

# # import language_tool_python
# # import openai
# # import json
# # import re
# # import time
# # from typing import Dict, List, Optional
# # import streamlit as st
# # from config.settings import Config

# # class HybridGrammarChecker:
# #     def __init__(self):
# #         """Initialize hybrid grammar checker with speech-aware filtering"""
# #         # Initialize LanguageTool (always available)
# #         try:
# #             self.language_tool = language_tool_python.LanguageTool('en-US')
# #             self.local_available = True
# #         except Exception as e:
# #             print(f"Warning: LanguageTool initialization failed: {e}")
# #             self.language_tool = None
# #             self.local_available = False
        
# #         # Initialize OpenAI client (optional)
# #         self.ai_available = False
# #         if Config.is_openai_available():
# #             try:
# #                 self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
# #                 # Test the connection
# #                 self._test_openai_connection()
# #                 self.ai_available = True
# #             except Exception as e:
# #                 print(f"Warning: OpenAI initialization failed: {e}")
# #                 self.openai_client = None
        
# #         # Speech-specific error filters
# #         self.speech_filters = {
# #             'proper_names': True,           # Ignore proper name spelling
# #             'casual_punctuation': True,    # Relax punctuation rules
# #             'contractions': True,          # Allow informal contractions
# #             'filler_words': True,          # Handle um, uh, etc.
# #             'repetition': True,            # Allow natural repetition
# #             'incomplete_sentences': True    # Allow sentence fragments
# #         }
    
# #     def _test_openai_connection(self):
# #         """Test OpenAI API connection"""
# #         try:
# #             response = self.openai_client.chat.completions.create(
# #                 model=Config.OPENAI_MODEL,
# #                 messages=[{"role": "user", "content": "Test"}],
# #                 max_tokens=1
# #             )
# #             return True
# #         except Exception as e:
# #             print(f"OpenAI connection test failed: {e}")
# #             return False
    
# #     def check_grammar(self, text: str, force_ai: bool = False) -> Dict:
# #         """
# #         Comprehensive grammar check using hybrid approach
        
# #         Args:
# #             text: Text to analyze
# #             force_ai: Force AI analysis regardless of conditions
            
# #         Returns:
# #             Detailed grammar analysis results
# #         """
# #         if not text or not text.strip():
# #             return self._empty_result()
        
# #         # Clean and prepare text
# #         cleaned_text = self._clean_text(text)
# #         word_count = len(cleaned_text.split())
        
# #         if word_count < 5:  # Too short for meaningful analysis
# #             return self._minimal_result(cleaned_text, word_count)
        
# #         # Step 1: Local grammar check (LanguageTool)
# #         local_results = self._check_with_language_tool(cleaned_text)
        
# #         # Step 2: Decide if AI analysis is needed
# #         use_ai = force_ai or self._should_use_ai(cleaned_text, local_results, word_count)
        
# #         # Step 3: Enhanced AI analysis if conditions are met
# #         if use_ai and self.ai_available:
# #             try:
# #                 ai_results = self._check_with_openai(cleaned_text, local_results)
# #                 return self._merge_results(local_results, ai_results, cleaned_text)
# #             except Exception as e:
# #                 st.warning(f"AI analysis failed, using local results: {str(e)}")
# #                 return self._finalize_local_results(local_results, cleaned_text)
        
# #         return self._finalize_local_results(local_results, cleaned_text)
    
# #     def _clean_text(self, text: str) -> str:
# #         """Clean and normalize text for analysis"""
# #         # Remove extra whitespace
# #         text = re.sub(r'\s+', ' ', text.strip())
        
# #         # Remove common speech filler words
# #         fillers = [r'\buh+\b', r'\bum+\b', r'\ber+\b', r'\blike\b(?=\s+\w)', r'\byou know\b']
# #         for filler in fillers:
# #             text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
# #         # Clean up punctuation spacing
# #         text = re.sub(r'\s+([.!?])', r'\1', text)
# #         text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
# #         return text.strip()
    
# #     def _should_use_ai(self, text: str, local_results: Dict, word_count: int) -> bool:
# #         """Intelligent decision on when to use AI analysis"""
# #         if not Config.GRAMMAR_AI_AUTO_TRIGGER:
# #             return False
        
# #         # Get error count safely
# #         error_count = local_results.get('error_count', 0)
        
# #         # Conditions for AI analysis
# #         conditions = [
# #             word_count >= getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),  # Sufficient text length
# #             error_count / word_count > getattr(Config, 'AI_TRIGGER_ERROR_RATE', 0.08) if word_count > 0 else False,  # High error rate
# #             word_count > 50,  # Longer responses get AI analysis
# #         ]
        
# #         return any(conditions)
    
# #     def _check_with_language_tool(self, text: str) -> Dict:
# #         """Perform speech-aware grammar check using LanguageTool"""
# #         if not self.local_available:
# #             return {'errors': [], 'error_count': 0, 'available': False}
        
# #         try:
# #             matches = self.language_tool.check(text)
# #             errors = []
            
# #             for match in matches:
# #                 # Filter out speech-inappropriate errors
# #                 if self._should_ignore_error(match, text):
# #                     continue
                
# #                 error = {
# #                     'category': match.category,
# #                     'rule_id': match.ruleId,
# #                     'message': match.message,
# #                     'offset': match.offset,
# #                     'length': match.errorLength,
# #                     'context': match.context,
# #                     'suggestions': match.replacements[:3] if match.replacements else [],
# #                     'error_text': text[match.offset:match.offset + match.errorLength],
# #                     'severity': self._categorize_error_severity_for_speech(match.category, match.ruleId)
# #                 }
# #                 errors.append(error)
            
# #             return {
# #                 'errors': errors,
# #                 'error_count': len(errors),
# #                 'corrected_text': self._speech_aware_correction(text, errors),
# #                 'available': True
# #             }
            
# #         except Exception as e:
# #             print(f"LanguageTool error: {e}")
# #             return {'errors': [], 'error_count': 0, 'available': False}
    
# #     def _should_ignore_error(self, match, text: str) -> bool:
# #         """Determine if an error should be ignored for speech analysis"""
# #         rule_id = match.ruleId
# #         category = match.category
# #         error_text = text[match.offset:match.offset + match.errorLength].strip()
# #         message = match.message.lower()
        
# #         # 1. Ignore proper name spelling errors
# #         if self._is_proper_name_error(match, error_text):
# #             return True
        
# #         # 2. Ignore casual punctuation rules for speech
# #         if self._is_casual_punctuation_error(rule_id, message):
# #             return True
        
# #         # 3. Ignore overly formal grammar rules
# #         if self._is_overly_formal_rule(rule_id, message):
# #             return True
        
# #         # 4. Ignore common speech patterns
# #         if self._is_natural_speech_pattern(error_text, message):
# #             return True
        
# #         # 5. Ignore transcription artifacts
# #         if self._is_transcription_artifact(error_text, message):
# #             return True
        
# #         return False
    
# #     def _is_proper_name_error(self, match, error_text: str) -> bool:
# #         """Check if error is likely a proper name spelling issue"""
# #         message = match.message.lower()
        
# #         # Common indicators of proper name errors
# #         proper_name_indicators = [
# #             'possible spelling mistake',
# #             'spelling mistake found',
# #             'use a different word'
# #         ]
        
# #         # If it's a spelling error and the word is capitalized (likely a name)
# #         if any(indicator in message for indicator in proper_name_indicators):
# #             if error_text and error_text[0].isupper():
# #                 # Additional check: if suggestions are completely different words
# #                 # (like "Haneen" -> "Hansen, Heineken"), it's likely a name
# #                 suggestions = match.replacements[:3] if match.replacements else []
# #                 if suggestions:
# #                     # If all suggestions are very different from original, likely a proper name
# #                     similarity_scores = []
# #                     for suggestion in suggestions:
# #                         # Simple similarity check
# #                         common_chars = set(error_text.lower()) & set(suggestion.lower())
# #                         similarity = len(common_chars) / max(len(error_text), len(suggestion))
# #                         similarity_scores.append(similarity)
                    
# #                     # If all suggestions have low similarity, likely a proper name
# #                     if all(score < 0.5 for score in similarity_scores):
# #                         return True
        
# #         return False
    
# #     def _is_casual_punctuation_error(self, rule_id: str, message: str) -> bool:
# #         """Check if error is about casual punctuation acceptable in speech"""
# #         casual_punctuation_rules = [
# #             'COMMA_COMPOUND_SENTENCE',      # Comma before 'and' in compound sentences
# #             'OXFORD_COMMA',                 # Oxford comma usage
# #             'COMMA_PARENTHETICAL',          # Commas around parenthetical phrases
# #             'SEMICOLON_COMPOUND',           # Semicolon usage
# #             'EN_QUOTES',                    # Quote mark consistency
# #             'ELLIPSIS',                     # Ellipsis usage
# #         ]
        
# #         casual_messages = [
# #             "comma before 'and'",
# #             "use a comma before",
# #             "comma after",
# #             "semicolon instead",
# #             "quotation marks",
# #             "ellipsis"
# #         ]
        
# #         return (rule_id in casual_punctuation_rules or 
# #                 any(msg in message for msg in casual_messages))
    
# #     def _is_overly_formal_rule(self, rule_id: str, message: str) -> bool:
# #         """Check if error is about overly formal grammar rules"""
# #         formal_rules = [
# #             'SENTENCE_FRAGMENT',            # Allow fragments in speech
# #             'INFORMAL_CONTRACTIONS',        # Allow contractions
# #             'COLLOQUIAL_WORD',             # Allow colloquial language
# #             'PASSIVE_VOICE',               # Don't enforce active voice
# #             'WORDINESS',                   # Allow some redundancy in speech
# #         ]
        
# #         formal_messages = [
# #             'sentence fragment',
# #             'avoid using',
# #             'too informal',
# #             'passive voice',
# #             'wordy',
# #             'redundant'
# #         ]
        
# #         return (rule_id in formal_rules or 
# #                 any(msg in message for msg in formal_messages))
    
# #     def _is_natural_speech_pattern(self, error_text: str, message: str) -> bool:
# #         """Check if error represents natural speech patterns"""
# #         # Common speech patterns that shouldn't be flagged
# #         natural_patterns = [
# #             'um', 'uh', 'er', 'ah',        # Filler words
# #             'like', 'you know', 'so',      # Common speech connectors
# #             'well', 'actually', 'basically' # Discourse markers
# #         ]
        
# #         # Repetition patterns (common in speech)
# #         if any(pattern in error_text.lower() for pattern in natural_patterns):
# #             return True
        
# #         # Check for natural repetition
# #         words = error_text.lower().split()
# #         if len(words) >= 2 and words[0] == words[1]:  # Word repetition
# #             return True
        
# #         return False
    
# #     def _is_transcription_artifact(self, error_text: str, message: str) -> bool:
# #         """Check if error is likely a transcription artifact"""
# #         transcription_artifacts = [
# #             'single letter errors',         # OCR/ASR single character mistakes
# #             'missing space',                # Word concatenation
# #             'extra space',                  # Word separation
# #             'capitalization'                # Inconsistent caps from ASR
# #         ]
        
# #         # Very short errors (1-2 characters) are often transcription issues
# #         if len(error_text.strip()) <= 2:
# #             return True
        
# #         return any(artifact in message for artifact in transcription_artifacts)
    
# #     def _categorize_error_severity_for_speech(self, category: str, rule_id: str) -> str:
# #         """Categorize error severity specifically for speech context"""
# #         # More lenient severity for speech
# #         high_severity = ['GRAMMAR']  # Only major grammar issues
# #         medium_severity = ['TYPOS', 'STYLE']
        
# #         # Reduce severity for speech-common issues
# #         speech_reduced_severity = [
# #             'COMMA_COMPOUND_SENTENCE',
# #             'OXFORD_COMMA',
# #             'SENTENCE_FRAGMENT'
# #         ]
        
# #         if rule_id in speech_reduced_severity:
# #             return 'low'
# #         elif category in high_severity:
# #             return 'medium'  # Reduce from high to medium
# #         elif category in medium_severity:
# #             return 'low'     # Reduce from medium to low
# #         else:
# #             return 'low'
    
# #     def _speech_aware_correction(self, text: str, errors: List[Dict]) -> str:
# #         """Apply only appropriate corrections for speech context"""
# #         # For speech, only apply corrections for:
# #         # 1. Clear grammatical errors (verb tense, subject-verb agreement)
# #         # 2. Major spelling errors (not proper names)
# #         # 3. Obvious typos
        
# #         corrected = text
# #         high_confidence_rules = [
# #             'MORFOLOGIK_RULE',  # Clear spelling errors
# #             'AGREEMENT_SENT_START',  # Subject-verb agreement
# #             'ENGLISH_WORD_REPEAT_RULE'  # Word repetition
# #         ]
        
# #         # Only apply corrections for high-confidence, speech-appropriate rules
# #         try:
# #             if self.local_available:
# #                 # Get all matches again
# #                 matches = self.language_tool.check(text)
                
# #                 # Filter to only speech-appropriate corrections
# #                 for match in reversed(matches):  # Reverse to maintain offsets
# #                     if (match.ruleId in high_confidence_rules and 
# #                         not self._should_ignore_error(match, text) and
# #                         match.replacements):
                        
# #                         # Apply the correction
# #                         start = match.offset
# #                         end = match.offset + match.errorLength
# #                         corrected = corrected[:start] + match.replacements[0] + corrected[end:]
        
# #         except Exception:
# #             return text  # Return original if correction fails
        
# #         return corrected
    
# #     def _check_with_azure_openai(self, text: str, local_results: Dict) -> Dict:
# #         """Enhanced grammar and communication analysis using Azure OpenAI"""
# #         from langchain_core.messages import HumanMessage
        
# #         error_count = local_results.get('error_count', 0)
# #         word_count = len(text.split())
        
# #         prompt = f"""
# # As an expert English language assessor evaluating interview responses, analyze this text for professional communication quality.

# # TEXT TO ANALYZE: "{text}"

# # CONTEXT:
# # - This is from a job interview response (spoken language)
# # - Local grammar tool found {error_count} potential issues in {word_count} words
# # - Focus on professional communication standards for spoken language
# # - Ignore proper names and natural speech patterns

# # Provide analysis in this exact JSON format:
# # {{
# #     "grammar_score": <0-100 integer>,
# #     "professionalism_score": <0-100 integer>,
# #     "clarity_score": <0-100 integer>,
# #     "coherence_score": <0-100 integer>,
# #     "key_strengths": ["strength1", "strength2"],
# #     "key_issues": ["issue1", "issue2"],
# #     "specific_suggestions": ["actionable suggestion1", "actionable suggestion2"],
# #     "interview_assessment": "brief assessment of interview readiness",
# #     "overall_impression": "positive/neutral/needs_improvement"
# # }}

# # Focus on:
# # 1. Grammar and syntax correctness (for spoken language)
# # 2. Professional tone and vocabulary
# # 3. Clarity of communication
# # 4. Logical flow and coherence
# # 5. Interview appropriateness

# # Be constructive and specific in feedback. Remember this is spoken language, not formal writing.
# # """

# #         try:
# #             message = HumanMessage(content=prompt)
# #             response = self.azure_llm.invoke([message])
# #             content = response.content.strip()
            
# #             # Try to parse JSON, with fallback
# #             try:
# #                 ai_analysis = json.loads(content)
# #                 return ai_analysis
# #             except json.JSONDecodeError:
# #                 # Fallback parsing if JSON is malformed
# #                 return self._parse_ai_response_fallback(content)
                
# #         except Exception as e:
# #             print(f"Azure OpenAI API error: {e}")
# #             raise e
    
# #     def _parse_ai_response_fallback(self, content: str) -> Dict:
# #         """Fallback parser for non-JSON AI responses"""
# #         return {
# #             "grammar_score": 75,
# #             "professionalism_score": 75,
# #             "clarity_score": 75,
# #             "coherence_score": 75,
# #             "key_strengths": ["Analysis completed"],
# #             "key_issues": ["Could not parse detailed feedback"],
# #             "specific_suggestions": ["Review response format"],
# #             "interview_assessment": "AI analysis parsing error occurred",
# #             "overall_impression": "neutral"
# #         }
    
# #     def _merge_results(self, local_results: Dict, ai_results: Dict, text: str) -> Dict:
# #         """Merge local and AI analysis results"""
# #         word_count = len(text.split())
# #         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
        
# #         # Calculate comprehensive scores
# #         grammar_score = self._calculate_final_grammar_score(local_results, ai_results, word_count)
        
# #         return {
# #             # Core metrics
# #             'grammar_score': grammar_score,
# #             'professionalism_score': ai_results.get('professionalism_score', 75),
# #             'clarity_score': ai_results.get('clarity_score', 75),
# #             'coherence_score': ai_results.get('coherence_score', 75),
            
# #             # Detailed analysis
# #             'local_errors': local_results.get('errors', []),
# #             'error_count': local_results.get('error_count', 0),
# #             'word_count': word_count,
# #             'sentence_count': sentence_count,
            
# #             # AI insights
# #             'key_strengths': ai_results.get('key_strengths', []),
# #             'key_issues': ai_results.get('key_issues', []),
# #             'specific_suggestions': ai_results.get('specific_suggestions', []),
# #             'interview_assessment': ai_results.get('interview_assessment', ''),
# #             'overall_impression': ai_results.get('overall_impression', 'neutral'),
            
# #             # Additional data
# #             'corrected_text': local_results.get('corrected_text', text),
# #             'original_text': text,
# #             'analysis_type': 'hybrid',
# #             'ai_used': True
# #         }
    
# #     def _finalize_local_results(self, local_results: Dict, text: str) -> Dict:
# #         """Finalize results using only local analysis"""
# #         word_count = len(text.split())
# #         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
# #         error_count = local_results.get('error_count', 0)
        
# #         # Calculate scores based on local analysis
# #         grammar_score = self._calculate_local_grammar_score(error_count, word_count)
# #         readability_score = self._calculate_readability_score(text, word_count, sentence_count)
        
# #         return {
# #             # Core metrics
# #             'grammar_score': grammar_score,
# #             'readability_score': readability_score,
# #             'professionalism_score': min(grammar_score + 5, 100),  # Estimate
# #             'clarity_score': readability_score,
            
# #             # Detailed analysis
# #             'local_errors': local_results.get('errors', []),
# #             'error_count': error_count,
# #             'word_count': word_count,
# #             'sentence_count': sentence_count,
            
# #             # Generated insights
# #             'suggestions': self._generate_local_suggestions(local_results, grammar_score),
# #             'overall_assessment': self._generate_local_assessment(grammar_score, readability_score, error_count),
            
# #             # Additional data
# #             'corrected_text': local_results.get('corrected_text', text),
# #             'original_text': text,
# #             'analysis_type': 'local_only',
# #             'ai_used': False
# #         }
    
# #     def _calculate_final_grammar_score(self, local_results: Dict, ai_results: Dict, word_count: int) -> float:
# #         """Calculate final grammar score combining local and AI analysis"""
# #         # Weight local error-based score and AI assessment
# #         local_score = self._calculate_local_grammar_score(local_results.get('error_count', 0), word_count)
# #         ai_score = ai_results.get('grammar_score', local_score)
        
# #         # Weighted average (favor AI slightly for final score)
# #         final_score = (local_score * 0.4) + (ai_score * 0.6)
# #         return round(final_score, 1)
    
# #     def _calculate_local_grammar_score(self, error_count: int, word_count: int) -> float:
# #         """Calculate grammar score with speech-context adjustments"""
# #         if word_count == 0:
# #             return 0
        
# #         # More forgiving scoring for speech
# #         error_rate = error_count / word_count
        
# #         # Adjusted penalty calculation for speech context
# #         # Speech naturally has more variation, so be more lenient
# #         penalty = min(error_rate * 150, 40)  # Reduced max penalty from 50 to 40
# #         score = max(100 - penalty, 30)  # Higher minimum score (30 vs 20)
        
# #         return round(score, 1)
    
# #     def _calculate_readability_score(self, text: str, word_count: int, sentence_count: int) -> float:
# #         """Calculate readability score"""
# #         if sentence_count == 0 or word_count == 0:
# #             return 0
        
# #         avg_sentence_length = word_count / sentence_count
        
# #         # Optimal range for interview responses: 10-20 words per sentence
# #         if 10 <= avg_sentence_length <= 20:
# #             sentence_score = 100
# #         else:
# #             deviation = abs(avg_sentence_length - 15)
# #             sentence_score = max(60, 100 - (deviation * 3))
        
# #         return round(sentence_score, 1)
    
# #     def _generate_local_suggestions(self, local_results: Dict, grammar_score: float) -> List[str]:
# #         """Generate speech-appropriate suggestions"""
# #         suggestions = []
# #         errors = local_results.get('errors', [])
        
# #         # Speech-specific suggestions
# #         if grammar_score < 70:
# #             suggestions.append("Focus on clear sentence structure while speaking")
# #             suggestions.append("Practice expressing ideas in complete thoughts")
        
# #         # Error category-based suggestions for speech
# #         error_categories = [error.get('category', '') for error in errors]
# #         high_severity_errors = [error for error in errors if error.get('severity') == 'high']
        
# #         if 'GRAMMAR' in error_categories or high_severity_errors:
# #             suggestions.append("Pay attention to verb tenses and subject-verb agreement")
        
# #         if len(errors) > 5:  # Many errors
# #             suggestions.append("Practice speaking more slowly for clearer articulation")
        
# #         # Speech-specific advice
# #         suggestions.append("Remember: natural speech patterns are acceptable in interviews")
        
# #         return suggestions[:4]  # Limit suggestions
    
# #     def _generate_local_assessment(self, grammar_score: float, readability_score: float, error_count: int) -> str:
# #         """Generate overall assessment based on local analysis"""
# #         avg_score = (grammar_score + readability_score) / 2
        
# #         if avg_score >= 85:
# #             return f"Excellent language quality! Grammar: {grammar_score}/100, Readability: {readability_score}/100"
# #         elif avg_score >= 70:
# #             return f"Good communication with minor issues. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
# #         elif avg_score >= 50:
# #             return f"Adequate communication with room for improvement. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
# #         else:
# #             return f"Communication needs significant improvement. Focus on grammar and clarity. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
    
# #     def _empty_result(self) -> Dict:
# #         """Return empty result for no text"""
# #         return {
# #             'grammar_score': 0,
# #             'error_count': 0,
# #             'word_count': 0,
# #             'overall_assessment': "No text provided for analysis",
# #             'analysis_type': 'empty',
# #             'ai_used': False
# #         }
    
# #     def _minimal_result(self, text: str, word_count: int) -> Dict:
# #         """Return minimal result for very short text"""
# #         return {
# #             'grammar_score': 85,  # Assume good for very short responses
# #             'error_count': 0,
# #             'word_count': word_count,
# #             'original_text': text,
# #             'overall_assessment': f"Response too short ({word_count} words) for detailed analysis",
# #             'analysis_type': 'minimal',
# #             'ai_used': False
# #         }

# #     def get_analysis_summary(self) -> Dict:
# #         """Get summary of checker capabilities"""
# #         return {
# #             'local_available': self.local_available,
# #             'ai_available': self.ai_available,
# #             'hybrid_mode': self.local_available and self.ai_available,
# #             'recommended_min_words': getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30)
# #         }

# import language_tool_python
# from langchain_openai import AzureChatOpenAI
# from langchain_core.messages import HumanMessage
# import json
# import re
# import time
# from typing import Dict, List, Optional
# import streamlit as st
# from config.settings import Config

# class HybridGrammarChecker:
#     def __init__(self):
#         """Initialize hybrid grammar checker with speech-aware filtering"""
#         # Initialize LanguageTool (always available)
#         try:
#             self.language_tool = language_tool_python.LanguageTool('en-US')
#             self.local_available = True
#         except Exception as e:
#             print(f"Warning: LanguageTool initialization failed: {e}")
#             self.language_tool = None
#             self.local_available = False
        
#         # Initialize Azure OpenAI client (optional)
#         self.ai_available = False
#         if Config.is_azure_openai_available():
#             try:
#                 # Setup environment variables
#                 Config.setup_azure_openai_env()
                
#                 # Initialize Azure OpenAI client
#                 self.azure_llm = AzureChatOpenAI(
#                     openai_api_version=Config.AZURE_OPENAI_API_VERSION,
#                     azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
#                     temperature=0.1,
#                     max_tokens=800
#                 )
                
#                 # Test the connection
#                 if self._test_azure_openai_connection():
#                     self.ai_available = True
                    
#             except Exception as e:
#                 print(f"Warning: Azure OpenAI initialization failed: {e}")
#                 self.azure_llm = None
        
#         # Speech-specific error filters
#         self.speech_filters = {
#             'proper_names': True,           # Ignore proper name spelling
#             'casual_punctuation': True,    # Relax punctuation rules
#             'contractions': True,          # Allow informal contractions
#             'filler_words': True,          # Handle um, uh, etc.
#             'repetition': True,            # Allow natural repetition
#             'incomplete_sentences': True    # Allow sentence fragments
#         }
    
#     def _test_azure_openai_connection(self):
#         """Test Azure OpenAI connection"""
#         try:
#             message = HumanMessage(content="Test")
#             response = self.azure_llm.invoke([message])
#             return True
#         except Exception as e:
#             print(f"Azure OpenAI connection test failed: {e}")
#             return False
    
#     def check_grammar(self, text: str, force_ai: bool = False) -> Dict:
#         """
#         Comprehensive grammar check using hybrid approach
        
#         Args:
#             text: Text to analyze
#             force_ai: Force AI analysis regardless of conditions
            
#         Returns:
#             Detailed grammar analysis results
#         """
#         if not text or not text.strip():
#             return self._empty_result()
        
#         # Clean and prepare text
#         cleaned_text = self._clean_text(text)
#         word_count = len(cleaned_text.split())
        
#         if word_count < 5:  # Too short for meaningful analysis
#             return self._minimal_result(cleaned_text, word_count)
        
#         # Step 1: Local grammar check (LanguageTool)
#         local_results = self._check_with_language_tool(cleaned_text)
        
#         # Step 2: Decide if AI analysis is needed
#         use_ai = force_ai or self._should_use_ai(cleaned_text, local_results, word_count)
        
#         # Step 3: Enhanced AI analysis if conditions are met
#         if use_ai and self.ai_available:
#             try:
#                 ai_results = self._check_with_azure_openai(cleaned_text, local_results)
#                 return self._merge_results(local_results, ai_results, cleaned_text)
#             except Exception as e:
#                 st.warning(f"AI analysis failed, using local results: {str(e)}")
#                 return self._finalize_local_results(local_results, cleaned_text)
        
#         return self._finalize_local_results(local_results, cleaned_text)
    
#     def _clean_text(self, text: str) -> str:
#         """Clean and normalize text for analysis"""
#         # Remove extra whitespace
#         text = re.sub(r'\s+', ' ', text.strip())
        
#         # Remove common speech filler words
#         fillers = [r'\buh+\b', r'\bum+\b', r'\ber+\b', r'\blike\b(?=\s+\w)', r'\byou know\b']
#         for filler in fillers:
#             text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
#         # Clean up punctuation spacing
#         text = re.sub(r'\s+([.!?])', r'\1', text)
#         text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
#         return text.strip()
    
#     def _should_use_ai(self, text: str, local_results: Dict, word_count: int) -> bool:
#         """Intelligent decision on when to use AI analysis"""
#         if not getattr(Config, 'GRAMMAR_AI_AUTO_TRIGGER', True):
#             return False
        
#         # Get error count safely
#         error_count = local_results.get('error_count', 0)
        
#         # Conditions for AI analysis
#         conditions = [
#             word_count >= getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),  # Sufficient text length
#             error_count / word_count > getattr(Config, 'AI_TRIGGER_ERROR_RATE', 0.08) if word_count > 0 else False,  # High error rate
#             word_count > 50,  # Longer responses get AI analysis
#         ]
        
#         return any(conditions)
    
#     def _check_with_language_tool(self, text: str) -> Dict:
#         """Perform speech-aware grammar check using LanguageTool"""
#         if not self.local_available:
#             return {'errors': [], 'error_count': 0, 'available': False}
        
#         try:
#             matches = self.language_tool.check(text)
#             errors = []
            
#             for match in matches:
#                 # Filter out speech-inappropriate errors
#                 if self._should_ignore_error(match, text):
#                     continue
                
#                 error = {
#                     'category': match.category,
#                     'rule_id': match.ruleId,
#                     'message': match.message,
#                     'offset': match.offset,
#                     'length': match.errorLength,
#                     'context': match.context,
#                     'suggestions': match.replacements[:3] if match.replacements else [],
#                     'error_text': text[match.offset:match.offset + match.errorLength],
#                     'severity': self._categorize_error_severity_for_speech(match.category, match.ruleId)
#                 }
#                 errors.append(error)
            
#             return {
#                 'errors': errors,
#                 'error_count': len(errors),
#                 'corrected_text': self._speech_aware_correction(text, errors),
#                 'available': True
#             }
            
#         except Exception as e:
#             print(f"LanguageTool error: {e}")
#             return {'errors': [], 'error_count': 0, 'available': False}
    
#     def _should_ignore_error(self, match, text: str) -> bool:
#         """Determine if an error should be ignored for speech analysis"""
#         rule_id = match.ruleId
#         category = match.category
#         error_text = text[match.offset:match.offset + match.errorLength].strip()
#         message = match.message.lower()
        
#         # 1. Ignore proper name spelling errors
#         if self._is_proper_name_error(match, error_text):
#             return True
        
#         # 2. Ignore casual punctuation rules for speech
#         if self._is_casual_punctuation_error(rule_id, message):
#             return True
        
#         # 3. Ignore overly formal grammar rules
#         if self._is_overly_formal_rule(rule_id, message):
#             return True
        
#         # 4. Ignore common speech patterns
#         if self._is_natural_speech_pattern(error_text, message):
#             return True
        
#         # 5. Ignore transcription artifacts
#         if self._is_transcription_artifact(error_text, message):
#             return True
        
#         return False
    
#     def _is_proper_name_error(self, match, error_text: str) -> bool:
#         """Check if error is likely a proper name spelling issue"""
#         message = match.message.lower()
        
#         # Common indicators of proper name errors
#         proper_name_indicators = [
#             'possible spelling mistake',
#             'spelling mistake found',
#             'use a different word'
#         ]
        
#         # If it's a spelling error and the word is capitalized (likely a name)
#         if any(indicator in message for indicator in proper_name_indicators):
#             if error_text and error_text[0].isupper():
#                 # Additional check: if suggestions are completely different words
#                 # (like "Haneen" -> "Hansen, Heineken"), it's likely a name
#                 suggestions = match.replacements[:3] if match.replacements else []
#                 if suggestions:
#                     # If all suggestions are very different from original, likely a proper name
#                     similarity_scores = []
#                     for suggestion in suggestions:
#                         # Simple similarity check
#                         common_chars = set(error_text.lower()) & set(suggestion.lower())
#                         similarity = len(common_chars) / max(len(error_text), len(suggestion))
#                         similarity_scores.append(similarity)
                    
#                     # If all suggestions have low similarity, likely a proper name
#                     if all(score < 0.5 for score in similarity_scores):
#                         return True
        
#         return False
    
#     def _is_casual_punctuation_error(self, rule_id: str, message: str) -> bool:
#         """Check if error is about casual punctuation acceptable in speech"""
#         casual_punctuation_rules = [
#             'COMMA_COMPOUND_SENTENCE',      # Comma before 'and' in compound sentences
#             'OXFORD_COMMA',                 # Oxford comma usage
#             'COMMA_PARENTHETICAL',          # Commas around parenthetical phrases
#             'SEMICOLON_COMPOUND',           # Semicolon usage
#             'EN_QUOTES',                    # Quote mark consistency
#             'ELLIPSIS',                     # Ellipsis usage
#         ]
        
#         casual_messages = [
#             "comma before 'and'",
#             "use a comma before",
#             "comma after",
#             "semicolon instead",
#             "quotation marks",
#             "ellipsis"
#         ]
        
#         return (rule_id in casual_punctuation_rules or 
#                 any(msg in message for msg in casual_messages))
    
#     def _is_overly_formal_rule(self, rule_id: str, message: str) -> bool:
#         """Check if error is about overly formal grammar rules"""
#         formal_rules = [
#             'SENTENCE_FRAGMENT',            # Allow fragments in speech
#             'INFORMAL_CONTRACTIONS',        # Allow contractions
#             'COLLOQUIAL_WORD',             # Allow colloquial language
#             'PASSIVE_VOICE',               # Don't enforce active voice
#             'WORDINESS',                   # Allow some redundancy in speech
#         ]
        
#         formal_messages = [
#             'sentence fragment',
#             'avoid using',
#             'too informal',
#             'passive voice',
#             'wordy',
#             'redundant'
#         ]
        
#         return (rule_id in formal_rules or 
#                 any(msg in message for msg in formal_messages))
    
#     def _is_natural_speech_pattern(self, error_text: str, message: str) -> bool:
#         """Check if error represents natural speech patterns"""
#         # Common speech patterns that shouldn't be flagged
#         natural_patterns = [
#             'um', 'uh', 'er', 'ah',        # Filler words
#             'like', 'you know', 'so',      # Common speech connectors
#             'well', 'actually', 'basically' # Discourse markers
#         ]
        
#         # Repetition patterns (common in speech)
#         if any(pattern in error_text.lower() for pattern in natural_patterns):
#             return True
        
#         # Check for natural repetition
#         words = error_text.lower().split()
#         if len(words) >= 2 and words[0] == words[1]:  # Word repetition
#             return True
        
#         return False
    
#     def _is_transcription_artifact(self, error_text: str, message: str) -> bool:
#         """Check if error is likely a transcription artifact"""
#         transcription_artifacts = [
#             'single letter errors',         # OCR/ASR single character mistakes
#             'missing space',                # Word concatenation
#             'extra space',                  # Word separation
#             'capitalization'                # Inconsistent caps from ASR
#         ]
        
#         # Very short errors (1-2 characters) are often transcription issues
#         if len(error_text.strip()) <= 2:
#             return True
        
#         return any(artifact in message for artifact in transcription_artifacts)
    
#     def _categorize_error_severity_for_speech(self, category: str, rule_id: str) -> str:
#         """Categorize error severity specifically for speech context"""
#         # More lenient severity for speech
#         high_severity = ['GRAMMAR']  # Only major grammar issues
#         medium_severity = ['TYPOS', 'STYLE']
        
#         # Reduce severity for speech-common issues
#         speech_reduced_severity = [
#             'COMMA_COMPOUND_SENTENCE',
#             'OXFORD_COMMA',
#             'SENTENCE_FRAGMENT'
#         ]
        
#         if rule_id in speech_reduced_severity:
#             return 'low'
#         elif category in high_severity:
#             return 'medium'  # Reduce from high to medium
#         elif category in medium_severity:
#             return 'low'     # Reduce from medium to low
#         else:
#             return 'low'
    
#     def _speech_aware_correction(self, text: str, errors: List[Dict]) -> str:
#         """Apply only appropriate corrections for speech context"""
#         # For speech, only apply corrections for:
#         # 1. Clear grammatical errors (verb tense, subject-verb agreement)
#         # 2. Major spelling errors (not proper names)
#         # 3. Obvious typos
        
#         corrected = text
#         high_confidence_rules = [
#             'MORFOLOGIK_RULE',  # Clear spelling errors
#             'AGREEMENT_SENT_START',  # Subject-verb agreement
#             'ENGLISH_WORD_REPEAT_RULE'  # Word repetition
#         ]
        
#         # Only apply corrections for high-confidence, speech-appropriate rules
#         try:
#             if self.local_available:
#                 # Get all matches again
#                 matches = self.language_tool.check(text)
                
#                 # Filter to only speech-appropriate corrections
#                 for match in reversed(matches):  # Reverse to maintain offsets
#                     if (match.ruleId in high_confidence_rules and 
#                         not self._should_ignore_error(match, text) and
#                         match.replacements):
                        
#                         # Apply the correction
#                         start = match.offset
#                         end = match.offset + match.errorLength
#                         corrected = corrected[:start] + match.replacements[0] + corrected[end:]
        
#         except Exception:
#             return text  # Return original if correction fails
        
#         return corrected
    
#     def _check_with_azure_openai(self, text: str, local_results: Dict) -> Dict:
#         """Enhanced grammar and communication analysis using Azure OpenAI"""
#         error_count = local_results.get('error_count', 0)
#         word_count = len(text.split())
        
#         prompt = f"""
# As an expert English language assessor evaluating interview responses, analyze this text for professional communication quality.

# TEXT TO ANALYZE: "{text}"

# CONTEXT:
# - This is from a job interview response (spoken language)
# - Local grammar tool found {error_count} potential issues in {word_count} words
# - Focus on professional communication standards for spoken language
# - Ignore proper names and natural speech patterns

# Provide analysis in this exact JSON format:
# {{
#     "grammar_score": <0-100 integer>,
#     "professionalism_score": <0-100 integer>,
#     "clarity_score": <0-100 integer>,
#     "coherence_score": <0-100 integer>,
#     "key_strengths": ["strength1", "strength2"],
#     "key_issues": ["issue1", "issue2"],
#     "specific_suggestions": ["actionable suggestion1", "actionable suggestion2"],
#     "interview_assessment": "brief assessment of interview readiness",
#     "overall_impression": "positive/neutral/needs_improvement"
# }}

# Focus on:
# 1. Grammar and syntax correctness (for spoken language)
# 2. Professional tone and vocabulary
# 3. Clarity of communication
# 4. Logical flow and coherence
# 5. Interview appropriateness

# Be constructive and specific in feedback. Remember this is spoken language, not formal writing.
# """

#         try:
#             message = HumanMessage(content=prompt)
#             response = self.azure_llm.invoke([message])
#             content = response.content.strip()
            
#             # Try to parse JSON, with fallback
#             try:
#                 ai_analysis = json.loads(content)
#                 return ai_analysis
#             except json.JSONDecodeError:
#                 # Fallback parsing if JSON is malformed
#                 return self._parse_ai_response_fallback(content)
                
#         except Exception as e:
#             print(f"Azure OpenAI API error: {e}")
#             raise e
    
#     def _parse_ai_response_fallback(self, content: str) -> Dict:
#         """Fallback parser for non-JSON AI responses"""
#         return {
#             "grammar_score": 75,
#             "professionalism_score": 75,
#             "clarity_score": 75,
#             "coherence_score": 75,
#             "key_strengths": ["Analysis completed"],
#             "key_issues": ["Could not parse detailed feedback"],
#             "specific_suggestions": ["Review response format"],
#             "interview_assessment": "AI analysis parsing error occurred",
#             "overall_impression": "neutral"
#         }
    
#     def _merge_results(self, local_results: Dict, ai_results: Dict, text: str) -> Dict:
#         """Merge local and AI analysis results"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
        
#         # Calculate comprehensive scores
#         grammar_score = self._calculate_final_grammar_score(local_results, ai_results, word_count)
        
#         return {
#             # Core metrics
#             'grammar_score': grammar_score,
#             'professionalism_score': ai_results.get('professionalism_score', 75),
#             'clarity_score': ai_results.get('clarity_score', 75),
#             'coherence_score': ai_results.get('coherence_score', 75),
            
#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': local_results.get('error_count', 0),
#             'word_count': word_count,
#             'sentence_count': sentence_count,
            
#             # AI insights
#             'key_strengths': ai_results.get('key_strengths', []),
#             'key_issues': ai_results.get('key_issues', []),
#             'specific_suggestions': ai_results.get('specific_suggestions', []),
#             'interview_assessment': ai_results.get('interview_assessment', ''),
#             'overall_impression': ai_results.get('overall_impression', 'neutral'),
            
#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'hybrid',
#             'ai_used': True
#         }
    
#     def _finalize_local_results(self, local_results: Dict, text: str) -> Dict:
#         """Finalize results using only local analysis"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
#         error_count = local_results.get('error_count', 0)
        
#         # Calculate scores based on local analysis
#         grammar_score = self._calculate_local_grammar_score(error_count, word_count)
#         readability_score = self._calculate_readability_score(text, word_count, sentence_count)
        
#         return {
#             # Core metrics
#             'grammar_score': grammar_score,
#             'readability_score': readability_score,
#             'professionalism_score': min(grammar_score + 5, 100),  # Estimate
#             'clarity_score': readability_score,
            
#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': error_count,
#             'word_count': word_count,
#             'sentence_count': sentence_count,
            
#             # Generated insights
#             'suggestions': self._generate_local_suggestions(local_results, grammar_score),
#             'overall_assessment': self._generate_local_assessment(grammar_score, readability_score, error_count),
            
#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'local_only',
#             'ai_used': False
#         }
    
#     def _calculate_final_grammar_score(self, local_results: Dict, ai_results: Dict, word_count: int) -> float:
#         """Calculate final grammar score combining local and AI analysis"""
#         # Weight local error-based score and AI assessment
#         local_score = self._calculate_local_grammar_score(local_results.get('error_count', 0), word_count)
#         ai_score = ai_results.get('grammar_score', local_score)
        
#         # Weighted average (favor AI slightly for final score)
#         final_score = (local_score * 0.4) + (ai_score * 0.6)
#         return round(final_score, 1)
    
#     def _calculate_local_grammar_score(self, error_count: int, word_count: int) -> float:
#         """Calculate grammar score with speech-context adjustments"""
#         if word_count == 0:
#             return 0
        
#         # More forgiving scoring for speech
#         error_rate = error_count / word_count
        
#         # Adjusted penalty calculation for speech context
#         # Speech naturally has more variation, so be more lenient
#         penalty = min(error_rate * 150, 40)  # Reduced max penalty from 50 to 40
#         score = max(100 - penalty, 30)  # Higher minimum score (30 vs 20)
        
#         return round(score, 1)
    
#     def _calculate_readability_score(self, text: str, word_count: int, sentence_count: int) -> float:
#         """Calculate readability score"""
#         if sentence_count == 0 or word_count == 0:
#             return 0
        
#         avg_sentence_length = word_count / sentence_count
        
#         # Optimal range for interview responses: 10-20 words per sentence
#         if 10 <= avg_sentence_length <= 20:
#             sentence_score = 100
#         else:
#             deviation = abs(avg_sentence_length - 15)
#             sentence_score = max(60, 100 - (deviation * 3))
        
#         return round(sentence_score, 1)
    
#     def _generate_local_suggestions(self, local_results: Dict, grammar_score: float) -> List[str]:
#         """Generate speech-appropriate suggestions"""
#         suggestions = []
#         errors = local_results.get('errors', [])
        
#         # Speech-specific suggestions
#         if grammar_score < 70:
#             suggestions.append("Focus on clear sentence structure while speaking")
#             suggestions.append("Practice expressing ideas in complete thoughts")
        
#         # Error category-based suggestions for speech
#         error_categories = [error.get('category', '') for error in errors]
#         high_severity_errors = [error for error in errors if error.get('severity') == 'high']
        
#         if 'GRAMMAR' in error_categories or high_severity_errors:
#             suggestions.append("Pay attention to verb tenses and subject-verb agreement")
        
#         if len(errors) > 5:  # Many errors
#             suggestions.append("Practice speaking more slowly for clearer articulation")
        
#         # Speech-specific advice
#         suggestions.append("Remember: natural speech patterns are acceptable in interviews")
        
#         return suggestions[:4]  # Limit suggestions
    
#     def _generate_local_assessment(self, grammar_score: float, readability_score: float, error_count: int) -> str:
#         """Generate overall assessment based on local analysis"""
#         avg_score = (grammar_score + readability_score) / 2
        
#         if avg_score >= 85:
#             return f"Excellent language quality! Grammar: {grammar_score}/100, Readability: {readability_score}/100"
#         elif avg_score >= 70:
#             return f"Good communication with minor issues. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
#         elif avg_score >= 50:
#             return f"Adequate communication with room for improvement. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
#         else:
#             return f"Communication needs significant improvement. Focus on grammar and clarity. Grammar: {grammar_score}/100, Readability: {readability_score}/100"
    
#     def _empty_result(self) -> Dict:
#         """Return empty result for no text"""
#         return {
#             'grammar_score': 0,
#             'error_count': 0,
#             'word_count': 0,
#             'overall_assessment': "No text provided for analysis",
#             'analysis_type': 'empty',
#             'ai_used': False
#         }
    
#     def _minimal_result(self, text: str, word_count: int) -> Dict:
#         """Return minimal result for very short text"""
#         return {
#             'grammar_score': 85,  # Assume good for very short responses
#             'error_count': 0,
#             'word_count': word_count,
#             'original_text': text,
#             'overall_assessment': f"Response too short ({word_count} words) for detailed analysis",
#             'analysis_type': 'minimal',
#             'ai_used': False
#         }

#     def get_analysis_summary(self) -> Dict:
#         """Get summary of checker capabilities"""
#         return {
#             'local_available': self.local_available,
#             'ai_available': self.ai_available,
#             'hybrid_mode': self.local_available and self.ai_available,
#             'recommended_min_words': getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),
#             'ai_provider': 'Azure OpenAI' if self.ai_available else 'None'
#         }

# import language_tool_python
# from langchain_openai import AzureChatOpenAI
# from langchain_core.messages import HumanMessage
# import json
# import re
# import time
# from typing import Dict, List, Optional
# import streamlit as st
# from config.settings import Config

# def _extract_json_from_text(raw: str) -> Optional[str]:
#     """
#     Scan `raw` for the first balanced JSON object or array.
#     Returns the JSON substring (starting at '{' or '[' and ending at matching '}' or ']'),
#     or None if nothing parseable is found.
#     """
#     # Search for a “{” or “[” to begin
#     for start_idx, ch in enumerate(raw):
#         if ch not in ('{', '['):
#             continue
#         open_char = ch
#         close_char = '}' if ch == '{' else ']'
#         balance = 0
#         for end_idx in range(start_idx, len(raw)):
#             if raw[end_idx] == open_char:
#                 balance += 1
#             elif raw[end_idx] == close_char:
#                 balance -= 1
#                 if balance == 0:
#                     # We found a balanced chunk from start_idx..end_idx
#                     return raw[start_idx:end_idx+1]
#     return None


# class HybridGrammarChecker:
#     def _should_use_ai(self, text: str, local_results: Dict, word_count: int) -> bool:
#         """Intelligent decision on when to use AI analysis"""
#         if not getattr(Config, 'GRAMMAR_AI_AUTO_TRIGGER', True):
#             return False

#         # Get error count safely
#         error_count = local_results.get('error_count', 0)

#         # Conditions for AI analysis
#         conditions = [
#             word_count >= getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),  # Sufficient text length
#             error_count / word_count > getattr(Config, 'AI_TRIGGER_ERROR_RATE', 0.08) if word_count > 0 else False,  # High error rate
#             word_count > 50,  # Longer responses get AI analysis
#         ]

#         return any(conditions)

#     def _check_with_language_tool(self, text: str) -> Dict:
#         """Perform speech-aware grammar check using LanguageTool"""
#         if not self.local_available:
#             return {'errors': [], 'error_count': 0, 'available': False}

#         try:
#             matches = self.language_tool.check(text)
#             errors = []

#             for match in matches:
#                 # Filter out speech-inappropriate errors
#                 if self._should_ignore_error(match, text):
#                     continue

#                 error = {
#                     'category': match.category,
#                     'rule_id': match.ruleId,
#                     'message': match.message,
#                     'offset': match.offset,
#                     'length': match.errorLength,
#                     'context': match.context,
#                     'suggestions': match.replacements[:3] if match.replacements else [],
#                     'error_text': text[match.offset:match.offset + match.errorLength],
#                     'severity': self._categorize_error_severity_for_speech(match.category, match.ruleId)
#                 }
#                 errors.append(error)

#             return {
#                 'errors': errors,
#                 'error_count': len(errors),
#                 'corrected_text': self._speech_aware_correction(text, errors),
#                 'available': True
#             }

#         except Exception as e:
#             print(f"LanguageTool error: {e}")
#             return {'errors': [], 'error_count': 0, 'available': False}

#     def _should_ignore_error(self, match, text: str) -> bool:
#         """Determine if an error should be ignored for speech analysis"""
#         rule_id = match.ruleId
#         category = match.category
#         error_text = text[match.offset:match.offset + match.errorLength].strip()
#         message = match.message.lower()

#         # 1. Ignore proper name spelling errors
#         if self._is_proper_name_error(match, error_text):
#             return True

#         # 2. Ignore casual punctuation rules for speech
#         if self._is_casual_punctuation_error(rule_id, message):
#             return True

#         # 3. Ignore overly formal grammar rules
#         if self._is_overly_formal_rule(rule_id, message):
#             return True

#         # 4. Ignore common speech patterns
#         if self._is_natural_speech_pattern(error_text, message):
#             return True

#         # 5. Ignore transcription artifacts
#         if self._is_transcription_artifact(error_text, message):
#             return True

#         return False

#     def _is_proper_name_error(self, match, error_text: str) -> bool:
#         """Check if error is likely a proper name spelling issue"""
#         message = match.message.lower()

#         # Common indicators of proper name errors
#         proper_name_indicators = [
#             'possible spelling mistake',
#             'spelling mistake found',
#             'use a different word'
#         ]

#         # If it's a spelling error and the word is capitalized (likely a name)
#         if any(indicator in message for indicator in proper_name_indicators):
#             if error_text and error_text[0].isupper():
#                 # Additional check: if suggestions are completely different words
#                 # (like "Haneen" -> "Hansen, Heineken"), it's likely a name
#                 suggestions = match.replacements[:3] if match.replacements else []
#                 if suggestions:
#                     # If all suggestions have low similarity, likely a proper name
#                     similarity_scores = []
#                     for suggestion in suggestions:
#                         # Simple similarity check
#                         common_chars = set(error_text.lower()) & set(suggestion.lower())
#                         similarity = len(common_chars) / max(len(error_text), len(suggestion))
#                         similarity_scores.append(similarity)

#                     if all(score < 0.5 for score in similarity_scores):
#                         return True

#         return False

#     def _is_casual_punctuation_error(self, rule_id: str, message: str) -> bool:
#         """Check if error is about casual punctuation acceptable in speech"""
#         casual_punctuation_rules = [
#             'COMMA_COMPOUND_SENTENCE',      # Comma before 'and' in compound sentences
#             'OXFORD_COMMA',                 # Oxford comma usage
#             'COMMA_PARENTHETICAL',          # Commas around parenthetical phrases
#             'SEMICOLON_COMPOUND',           # Semicolon usage
#             'EN_QUOTES',                    # Quote mark consistency
#             'ELLIPSIS',                     # Ellipsis usage
#         ]

#         casual_messages = [
#             "comma before 'and'",
#             "use a comma before",
#             "comma after",
#             "semicolon instead",
#             "quotation marks",
#             "ellipsis"
#         ]

#         return (rule_id in casual_punctuation_rules or 
#                 any(msg in message for msg in casual_messages))

#     def _is_overly_formal_rule(self, rule_id: str, message: str) -> bool:
#         """Check if error is about overly formal grammar rules"""
#         formal_rules = [
#             'SENTENCE_FRAGMENT',            # Allow fragments in speech
#             'INFORMAL_CONTRACTIONS',        # Allow contractions
#             'COLLOQUIAL_WORD',             # Allow colloquial language
#             'PASSIVE_VOICE',               # Don't enforce active voice
#             'WORDINESS',                   # Allow some redundancy in speech
#         ]

#         formal_messages = [
#             'sentence fragment',
#             'avoid using',
#             'too informal',
#             'passive voice',
#             'wordy',
#             'redundant'
#         ]

#         return (rule_id in formal_rules or 
#                 any(msg in message for msg in formal_messages))

#     def _is_natural_speech_pattern(self, error_text: str, message: str) -> bool:
#         """Check if error represents natural speech patterns"""
#         # Common speech patterns that shouldn't be flagged
#         natural_patterns = [
#             'um', 'uh', 'er', 'ah',        # Filler words
#             'like', 'you know', 'so',      # Common speech connectors
#             'well', 'actually', 'basically' # Discourse markers
#         ]

#         # Repetition patterns (common in speech)
#         if any(pattern in error_text.lower() for pattern in natural_patterns):
#             return True

#         # Check for natural repetition
#         words = error_text.lower().split()
#         if len(words) >= 2 and words[0] == words[1]:  # Word repetition
#             return True

#         return False

#     def _is_transcription_artifact(self, error_text: str, message: str) -> bool:
#         """Check if error is likely a transcription artifact"""
#         transcription_artifacts = [
#             'single letter errors',         # OCR/ASR single character mistakes
#             'missing space',                # Word concatenation
#             'extra space',                  # Word separation
#             'capitalization'                # Inconsistent caps from ASR
#         ]

#         # Very short errors (1-2 characters) are often transcription issues
#         if len(error_text.strip()) <= 2:
#             return True

#         return any(artifact in message for artifact in transcription_artifacts)

#     def _categorize_error_severity_for_speech(self, category: str, rule_id: str) -> str:
#         """Categorize error severity specifically for speech context"""
#         # More lenient severity for speech
#         high_severity = ['GRAMMAR']  # Only major grammar issues
#         medium_severity = ['TYPOS', 'STYLE']

#         # Reduce severity for speech-common issues
#         speech_reduced_severity = [
#             'COMMA_COMPOUND_SENTENCE',
#             'OXFORD_COMMA',
#             'SENTENCE_FRAGMENT'
#         ]

#         if rule_id in speech_reduced_severity:
#             return 'low'
#         elif category in high_severity:
#             return 'medium'  # Reduce from high to medium
#         elif category in medium_severity:
#             return 'low'     # Reduce from medium to low
#         else:
#             return 'low'

#     def _speech_aware_correction(self, text: str, errors: List[Dict]) -> str:
#         """Apply only appropriate corrections for speech context"""
#         # For speech, only apply corrections for:
#         # 1. Clear grammatical errors (verb tense, subject-verb agreement)
#         # 2. Major spelling errors (not proper names)
#         # 3. Obvious typos

#         corrected = text
#         high_confidence_rules = [
#             'MORFOLOGIK_RULE',  # Clear spelling errors
#             'AGREEMENT_SENT_START',  # Subject-verb agreement
#             'ENGLISH_WORD_REPEAT_RULE'  # Word repetition
#         ]

#         # Only apply corrections for high-confidence, speech-appropriate rules
#         try:
#             if self.local_available:
#                 # Get all matches again
#                 matches = self.language_tool.check(text)

#                 # Filter to only speech-appropriate corrections
#                 for match in reversed(matches):  # Reverse to maintain offsets
#                     if (match.ruleId in high_confidence_rules and 
#                         not self._should_ignore_error(match, text) and
#                         match.replacements):

#                         # Apply the correction
#                         start = match.offset
#                         end = match.offset + match.errorLength
#                         corrected = corrected[:start] + match.replacements[0] + corrected[end:]

#         except Exception:
#             return text  # Return original if correction fails

#         return corrected

#     def _check_with_azure_openai(self, text: str, local_results: Dict) -> Dict:
#         """Enhanced grammar and spelling analysis using Azure OpenAI"""
#         error_count = local_results.get('error_count', 0)
#         word_count = len(text.split())

#         # Build a system‐style prompt that *only* returns JSON
#         prompt = f"""
# You are an expert English language assessor.  Respond *only* with valid JSON—no extra explanation, no markdown fences, no comments.

# Analyze this interview transcript for GRAMMAR and SPELLING.  Provide a JSON object with these exact keys and types:

# {{
#   "grammar_score": <integer 0–100>,
#   "spelling_score": <integer 0–100>,
#   "key_grammar_strengths": ["strength1", "strength2", ...],
#   "key_grammar_issues": ["issue1", "issue2", ...],
#   "specific_grammar_suggestions": ["suggestion1", ...],
#   "grammar_assessment": "<brief assessment as string>"
# }}

# TEXT TO ANALYZE: "{text}"

# CONTEXT:
# - Local grammar tool flagged {error_count} issues in {word_count} words.
# - Focus on verb tenses, subject‐verb agreement, sentence structure, spelling (excluding proper names), punctuation for clarity.
# - Do NOT output anything other than a single JSON object with those six keys.
# """

#         try:
#             # Wrap the prompt in a system message if your Azure client supports it.
#             sys_msg = HumanMessage(role="system", content="You must reply in JSON only.")
#             user_msg = HumanMessage(role="user", content=prompt)
#             response = self.azure_llm.invoke([sys_msg, user_msg])
#             raw_content = response.content.strip()

#             # DEBUG: Print or log the raw response content ONCE
#             print("⟳ Azure raw response:", raw_content)

#             # Attempt to extract the JSON substring
#             json_substr = _extract_json_from_text(raw_content)
#             if not json_substr:
#                 raise ValueError("No JSON object found in LLM response.")

#             # Parse it
#             ai_analysis = json.loads(json_substr)
#             return ai_analysis

#         except Exception as e:
#             print(f"Azure parsing/extraction error: {e}\n→ Raw:\n{raw_content}")
#             # Fallback to your existing fallback logic
#             return self._parse_ai_response_fallback(raw_content)

#     def _parse_ai_response_fallback(self, raw: str) -> Dict:
#         """
#         Fallback parser when we cannot extract valid JSON from the LLM.
#         We'll return a very basic placeholder so the UI still shows something.
#         """
#         print("⚠️ Fallback used. Raw LLM content was:")
#         print(raw)
#         return {
#             "grammar_score": 75,
#             "spelling_score": 75,
#             "key_grammar_strengths": ["Grammar analysis completed"],
#             "key_grammar_issues": ["Could not parse detailed feedback"],
#             "specific_grammar_suggestions": ["Review grammar and spelling"],
#             "grammar_assessment": "AI analysis parsing error occurred"
#         }

#     def _merge_results(self, local_results: Dict, ai_results: Dict, text: str) -> Dict:
#         """Merge local and AI analysis results"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))

#         # Calculate comprehensive scores
#         grammar_score = self._calculate_final_grammar_score(local_results, ai_results, word_count)

#         return {
#             # Core metrics - FOCUSED ON GRAMMAR AND SPELLING ONLY
#             'grammar_score': grammar_score,
#             'spelling_score': ai_results.get('spelling_score', grammar_score),

#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': local_results.get('error_count', 0),
#             'word_count': word_count,
#             'sentence_count': sentence_count,

#             # AI insights - GRAMMAR FOCUSED
#             'key_strengths': ai_results.get('key_grammar_strengths', []),
#             'key_issues': ai_results.get('key_grammar_issues', []),
#             'specific_suggestions': ai_results.get('specific_grammar_suggestions', []),
#             'interview_assessment': ai_results.get('grammar_assessment', ''),

#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'hybrid',
#             'ai_used': True
#         }

#     def _finalize_local_results(self, local_results: Dict, text: str) -> Dict:
#         """Finalize results using only local analysis"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
#         error_count = local_results.get('error_count', 0)

#         # Calculate scores based on local analysis
#         grammar_score = self._calculate_local_grammar_score(error_count, word_count)

#         return {
#             # Core metrics - FOCUSED ON GRAMMAR AND SPELLING ONLY
#             'grammar_score': grammar_score,
#             'spelling_score': grammar_score,  # Use same score for local analysis

#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': error_count,
#             'word_count': word_count,
#             'sentence_count': sentence_count,

#             # Generated insights
#             'suggestions': self._generate_local_suggestions(local_results, grammar_score),
#             'overall_assessment': self._generate_local_assessment(grammar_score, error_count),

#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'local_only',
#             'ai_used': False
#         }

#     def _calculate_final_grammar_score(self, local_results: Dict, ai_results: Dict, word_count: int) -> float:
#         """Calculate final grammar score combining local and AI analysis"""
#         # Weight local error-based score and AI assessment
#         local_score = self._calculate_local_grammar_score(local_results.get('error_count', 0), word_count)
#         ai_score = ai_results.get('grammar_score', local_score)

#         # Weighted average (favor AI slightly for final score)
#         final_score = (local_score * 0.4) + (ai_score * 0.6)
#         return round(final_score, 1)

#     def _calculate_local_grammar_score(self, error_count: int, word_count: int) -> float:
#         """Calculate grammar score with speech-context adjustments"""
#         if word_count == 0:
#             return 0

#         # More forgiving scoring for speech
#         error_rate = error_count / word_count

#         # Adjusted penalty calculation for speech context
#         # Speech naturally has more variation, so be more lenient
#         penalty = min(error_rate * 150, 40)  # Reduced max penalty from 50 to 40
#         score = max(100 - penalty, 30)  # Higher minimum score (30 vs 20)

#         return round(score, 1)

#     def _generate_local_suggestions(self, local_results: Dict, grammar_score: float) -> List[str]:
#         """Generate speech-appropriate grammar suggestions"""
#         suggestions = []
#         errors = local_results.get('errors', [])

#         # Grammar-specific suggestions
#         if grammar_score < 70:
#             suggestions.append("Focus on clear sentence structure while speaking")
#             suggestions.append("Practice expressing ideas in complete thoughts")

#         # Error category-based suggestions for speech
#         error_categories = [error.get('category', '') for error in errors]
#         high_severity_errors = [error for error in errors if error.get('severity') == 'high']

#         if 'GRAMMAR' in error_categories or high_severity_errors:
#             suggestions.append("Pay attention to verb tenses and subject-verb agreement")

#         if 'TYPOS' in error_categories:
#             suggestions.append("Check spelling of technical terms")

#         if len(errors) > 5:  # Many errors
#             suggestions.append("Practice speaking more slowly for clearer articulation")

#         return suggestions[:4]  # Limit suggestions

#     def _generate_local_assessment(self, grammar_score: float, error_count: int) -> str:
#         """Generate overall assessment based on local analysis"""
#         if grammar_score >= 85:
#             return f"Excellent grammar and spelling! Score: {grammar_score}/100"
#         elif grammar_score >= 70:
#             return f"Good grammar with minor issues. Score: {grammar_score}/100"
#         elif grammar_score >= 50:
#             return f"Adequate grammar with room for improvement. Score: {grammar_score}/100"
#         else:
#             return f"Grammar needs significant improvement. Focus on sentence structure and spelling. Score: {grammar_score}/100"

#     def _empty_result(self) -> Dict:
#         """Return empty result for no text"""
#         return {
#             'grammar_score': 0,
#             'spelling_score': 0,
#             'error_count': 0,
#             'word_count': 0,
#             'overall_assessment': "No text provided for analysis",
#             'analysis_type': 'empty',
#             'ai_used': False
#         }

#     def _minimal_result(self, text: str, word_count: int) -> Dict:
#         """Return minimal result for very short text"""
#         return {
#             'grammar_score': 85,  # Assume good for very short responses
#             'spelling_score': 85,
#             'error_count': 0,
#             'word_count': word_count,
#             'original_text': text,
#             'overall_assessment': f"Response too short ({word_count} words) for detailed analysis",
#             'analysis_type': 'minimal',
#             'ai_used': False
#         }

#     def get_analysis_summary(self) -> Dict:
#         """Get summary of checker capabilities"""
#         return {
#             'local_available': self.local_available,
#             'ai_available': self.ai_available,
#             'hybrid_mode': self.local_available and self.ai_available,
#             'recommended_min_words': getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),
#             'ai_provider': 'Azure OpenAI' if self.ai_available else 'None'
#         }

# import language_tool_python
# from langchain_openai import AzureChatOpenAI
# from langchain_core.messages import HumanMessage
# import json
# import re
# import time
# from typing import Dict, List, Optional
# import streamlit as st
# from config.settings import Config

# def _extract_json_from_text(raw: str) -> Optional[str]:
#     """
#     Scan `raw` for the first balanced JSON object or array.
#     Returns the JSON substring (starting at '{' or '[' and ending at matching '}' or ']'),
#     or None if nothing parseable is found.
#     """
#     # Search for a "{" or "[" to begin
#     for start_idx, ch in enumerate(raw):
#         if ch not in ('{', '['):
#             continue
#         open_char = ch
#         close_char = '}' if ch == '{' else ']'
#         balance = 0
#         for end_idx in range(start_idx, len(raw)):
#             if raw[end_idx] == open_char:
#                 balance += 1
#             elif raw[end_idx] == close_char:
#                 balance -= 1
#                 if balance == 0:
#                     # We found a balanced chunk from start_idx..end_idx
#                     return raw[start_idx:end_idx+1]
#     return None


# class HybridGrammarChecker:
#     def __init__(self):
#         """Initialize hybrid grammar checker focused ONLY on grammar (not spelling)"""
#         # Initialize LanguageTool (always available)
#         try:
#             self.language_tool = language_tool_python.LanguageTool('en-US')
#             self.local_available = True
#         except Exception as e:
#             print(f"Warning: LanguageTool initialization failed: {e}")
#             self.language_tool = None
#             self.local_available = False
        
#         # Initialize Azure OpenAI client (optional)
#         self.ai_available = False
#         if Config.is_azure_openai_available():
#             try:
#                 # Setup environment variables
#                 Config.setup_azure_openai_env()
                
#                 # Initialize Azure OpenAI client
#                 self.azure_llm = AzureChatOpenAI(
#                     openai_api_version=Config.AZURE_OPENAI_API_VERSION,
#                     azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
#                     temperature=0.1,
#                     max_tokens=600
#                 )
                
#                 # Test the connection
#                 if self._test_azure_openai_connection():
#                     self.ai_available = True
                    
#             except Exception as e:
#                 print(f"Warning: Azure OpenAI initialization failed: {e}")
#                 self.azure_llm = None
        
#         # Speech-specific error filters - focusing only on grammar
#         self.speech_filters = {
#             'casual_punctuation': True,    # Relax punctuation rules
#             'contractions': True,          # Allow informal contractions
#             'filler_words': True,          # Handle um, uh, etc.
#             'repetition': True,            # Allow natural repetition
#             'incomplete_sentences': True    # Allow sentence fragments
#         }
    
#     def _test_azure_openai_connection(self):
#         """Test Azure OpenAI connection"""
#         try:
#             message = HumanMessage(content="Test")
#             response = self.azure_llm.invoke([message])
#             return True
#         except Exception as e:
#             print(f"Azure OpenAI connection test failed: {e}")
#             return False
    
#     def check_grammar(self, text: str, force_ai: bool = False) -> Dict:
#         """
#         Grammar check using hybrid approach - GRAMMAR ONLY (no spelling)
        
#         Args:
#             text: Text to analyze
#             force_ai: Force AI analysis regardless of conditions
            
#         Returns:
#             Grammar analysis results (excluding spelling)
#         """
#         if not text or not text.strip():
#             return self._empty_result()
        
#         # Clean and prepare text
#         cleaned_text = self._clean_text(text)
#         word_count = len(cleaned_text.split())
        
#         if word_count < 5:  # Too short for meaningful analysis
#             return self._minimal_result(cleaned_text, word_count)
        
#         # Step 1: Local grammar check (LanguageTool) - filter out spelling errors
#         local_results = self._check_with_language_tool(cleaned_text)
        
#         # Step 2: Decide if AI analysis is needed
#         use_ai = force_ai or self._should_use_ai(cleaned_text, local_results, word_count)
        
#         # Step 3: Enhanced AI analysis if conditions are met
#         if use_ai and self.ai_available:
#             try:
#                 ai_results = self._check_with_azure_openai(cleaned_text, local_results)
#                 return self._merge_results(local_results, ai_results, cleaned_text)
#             except Exception as e:
#                 st.warning(f"AI analysis failed, using local results: {str(e)}")
#                 return self._finalize_local_results(local_results, cleaned_text)
        
#         return self._finalize_local_results(local_results, cleaned_text)
    
#     def _clean_text(self, text: str) -> str:
#         """Clean and normalize text for analysis"""
#         # Remove extra whitespace
#         text = re.sub(r'\s+', ' ', text.strip())
        
#         # Remove common speech filler words
#         fillers = [r'\buh+\b', r'\bum+\b', r'\ber+\b', r'\blike\b(?=\s+\w)', r'\byou know\b']
#         for filler in fillers:
#             text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
#         # Clean up punctuation spacing
#         text = re.sub(r'\s+([.!?])', r'\1', text)
#         text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
#         return text.strip()

#     def _should_use_ai(self, text: str, local_results: Dict, word_count: int) -> bool:
#         """Intelligent decision on when to use AI analysis"""
#         if not getattr(Config, 'GRAMMAR_AI_AUTO_TRIGGER', True):
#             return False

#         # Get error count safely
#         error_count = local_results.get('error_count', 0)

#         # Conditions for AI analysis
#         conditions = [
#             word_count >= getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),  # Sufficient text length
#             error_count / word_count > getattr(Config, 'AI_TRIGGER_ERROR_RATE', 0.08) if word_count > 0 else False,  # High error rate
#             word_count > 50,  # Longer responses get AI analysis
#         ]

#         return any(conditions)

#     def _check_with_language_tool(self, text: str) -> Dict:
#         """Perform speech-aware grammar check using LanguageTool - GRAMMAR ONLY"""
#         if not self.local_available:
#             return {'errors': [], 'error_count': 0, 'available': False}

#         try:
#             matches = self.language_tool.check(text)
#             errors = []

#             for match in matches:
#                 # SKIP ALL SPELLING ERRORS - Enhanced filtering
#                 if self._is_spelling_error(match):
#                     continue
                    
#                 # Filter out speech-inappropriate errors
#                 if self._should_ignore_error(match, text):
#                     continue

#                 error = {
#                     'category': match.category,
#                     'rule_id': match.ruleId,
#                     'message': match.message,
#                     'offset': match.offset,
#                     'length': match.errorLength,
#                     'context': match.context,
#                     'suggestions': match.replacements[:3] if match.replacements else [],
#                     'error_text': text[match.offset:match.offset + match.errorLength],
#                     'severity': self._categorize_error_severity_for_speech(match.category, match.ruleId)
#                 }
#                 errors.append(error)

#             return {
#                 'errors': errors,
#                 'error_count': len(errors),
#                 'corrected_text': self._speech_aware_correction(text, errors),
#                 'available': True
#             }

#         except Exception as e:
#             print(f"LanguageTool error: {e}")
#             return {'errors': [], 'error_count': 0, 'available': False}
    
#     def _is_spelling_error(self, match) -> bool:
#         """Check if the error is a spelling error that should be ignored - ENHANCED"""
#         # Categories that indicate spelling errors
#         spelling_categories = ['TYPOS']
        
#         # Rule IDs that are spelling-related - EXPANDED LIST
#         spelling_rule_ids = [
#             'MORFOLOGIK_RULE_EN_US',
#             'HUNSPELL_RULE',
#             'SPELLING_RULE',
#             'POSSIBLE_SPELLING_MISTAKE',
#             'MORFOLOGIK_RULE',
#             'SPELLER_RULE',
#             'DICTIONARY_RULE'
#         ]
        
#         # Messages that indicate spelling errors - EXPANDED LIST
#         spelling_messages = [
#             'possible spelling mistake',
#             'spelling mistake found',
#             'use a different word',
#             'did you mean',
#             'misspelled',
#             'not found in dictionary',
#             'unknown word',
#             'correct spelling',
#             'typo',
#             'misspelling'
#         ]
        
#         message_lower = match.message.lower()
        
#         # Check if it's a spelling error based on category, rule ID, or message
#         is_spelling = (match.category in spelling_categories or 
#                       match.ruleId in spelling_rule_ids or
#                       any(msg in message_lower for msg in spelling_messages))
        
#         # Additional check: if it's about proper names/capitalized words (often names)
#         if not is_spelling:
#             error_text = match.context[match.offset:match.offset + match.errorLength] if hasattr(match, 'context') else ""
#             if error_text and error_text[0].isupper() and any(msg in message_lower for msg in ['spelling', 'unknown']):
#                 is_spelling = True
        
#         return is_spelling

#     def _should_ignore_error(self, match, text: str) -> bool:
#         """Determine if an error should be ignored for speech analysis"""
#         rule_id = match.ruleId
#         category = match.category
#         error_text = text[match.offset:match.offset + match.errorLength].strip()
#         message = match.message.lower()

#         # 1. Ignore casual punctuation rules for speech
#         if self._is_casual_punctuation_error(rule_id, message):
#             return True

#         # 2. Ignore overly formal grammar rules
#         if self._is_overly_formal_rule(rule_id, message):
#             return True

#         # 3. Ignore common speech patterns
#         if self._is_natural_speech_pattern(error_text, message):
#             return True

#         # 4. Ignore transcription artifacts
#         if self._is_transcription_artifact(error_text, message):
#             return True

#         return False

#     def _is_casual_punctuation_error(self, rule_id: str, message: str) -> bool:
#         """Check if error is about casual punctuation acceptable in speech"""
#         casual_punctuation_rules = [
#             'COMMA_COMPOUND_SENTENCE',      # Comma before 'and' in compound sentences
#             'OXFORD_COMMA',                 # Oxford comma usage
#             'COMMA_PARENTHETICAL',          # Commas around parenthetical phrases
#             'SEMICOLON_COMPOUND',           # Semicolon usage
#             'EN_QUOTES',                    # Quote mark consistency
#             'ELLIPSIS',                     # Ellipsis usage
#         ]

#         casual_messages = [
#             "comma before 'and'",
#             "use a comma before",
#             "comma after",
#             "semicolon instead",
#             "quotation marks",
#             "ellipsis"
#         ]

#         return (rule_id in casual_punctuation_rules or 
#                 any(msg in message for msg in casual_messages))

#     def _is_overly_formal_rule(self, rule_id: str, message: str) -> bool:
#         """Check if error is about overly formal grammar rules"""
#         formal_rules = [
#             'SENTENCE_FRAGMENT',            # Allow fragments in speech
#             'INFORMAL_CONTRACTIONS',        # Allow contractions
#             'COLLOQUIAL_WORD',             # Allow colloquial language
#             'PASSIVE_VOICE',               # Don't enforce active voice
#             'WORDINESS',                   # Allow some redundancy in speech
#         ]

#         formal_messages = [
#             'sentence fragment',
#             'avoid using',
#             'too informal',
#             'passive voice',
#             'wordy',
#             'redundant'
#         ]

#         return (rule_id in formal_rules or 
#                 any(msg in message for msg in formal_messages))

#     def _is_natural_speech_pattern(self, error_text: str, message: str) -> bool:
#         """Check if error represents natural speech patterns"""
#         # Common speech patterns that shouldn't be flagged
#         natural_patterns = [
#             'um', 'uh', 'er', 'ah',        # Filler words
#             'like', 'you know', 'so',      # Common speech connectors
#             'well', 'actually', 'basically' # Discourse markers
#         ]

#         # Repetition patterns (common in speech)
#         if any(pattern in error_text.lower() for pattern in natural_patterns):
#             return True

#         # Check for natural repetition
#         words = error_text.lower().split()
#         if len(words) >= 2 and words[0] == words[1]:  # Word repetition
#             return True

#         return False

#     def _is_transcription_artifact(self, error_text: str, message: str) -> bool:
#         """Check if error is likely a transcription artifact"""
#         transcription_artifacts = [
#             'single letter errors',         # OCR/ASR single character mistakes
#             'missing space',                # Word concatenation
#             'extra space',                  # Word separation
#             'capitalization'                # Inconsistent caps from ASR
#         ]

#         # Very short errors (1-2 characters) are often transcription issues
#         if len(error_text.strip()) <= 2:
#             return True

#         return any(artifact in message for artifact in transcription_artifacts)

#     def _categorize_error_severity_for_speech(self, category: str, rule_id: str) -> str:
#         """Categorize error severity specifically for speech context - GRAMMAR ONLY"""
#         # More lenient severity for speech - ONLY GRAMMAR MATTERS
#         high_severity = ['GRAMMAR']  # Only major grammar issues
#         medium_severity = ['STYLE']  # Style issues (no spelling)

#         # Reduce severity for speech-common issues
#         speech_reduced_severity = [
#             'COMMA_COMPOUND_SENTENCE',
#             'OXFORD_COMMA',
#             'SENTENCE_FRAGMENT'
#         ]

#         if rule_id in speech_reduced_severity:
#             return 'low'
#         elif category in high_severity:
#             return 'medium'  # Reduce from high to medium
#         elif category in medium_severity:
#             return 'low'     # Reduce from medium to low
#         else:
#             return 'low'

#     def _speech_aware_correction(self, text: str, errors: List[Dict]) -> str:
#         """Apply only appropriate corrections for speech context - GRAMMAR ONLY"""
#         # For speech, only apply corrections for:
#         # 1. Clear grammatical errors (verb tense, subject-verb agreement)
#         # 2. Obvious grammatical mistakes (NOT spelling)

#         corrected = text
#         # REMOVED spelling-related rules, kept only grammar rules
#         high_confidence_rules = [
#             'AGREEMENT_SENT_START',      # Subject-verb agreement
#             'ENGLISH_WORD_REPEAT_RULE',  # Word repetition
#             'VERB_TENSE_AGREEMENT',      # Verb tense issues
#             'GRAMMAR_RULE'               # General grammar rules
#         ]

#         # Only apply corrections for high-confidence, speech-appropriate grammar rules
#         try:
#             if self.local_available:
#                 # Get all matches again
#                 matches = self.language_tool.check(text)

#                 # Filter to only speech-appropriate corrections
#                 for match in reversed(matches):  # Reverse to maintain offsets
#                     if (match.ruleId in high_confidence_rules and 
#                         not self._is_spelling_error(match) and  # Skip spelling
#                         not self._should_ignore_error(match, text) and
#                         match.replacements):

#                         # Apply the correction
#                         start = match.offset
#                         end = match.offset + match.errorLength
#                         corrected = corrected[:start] + match.replacements[0] + corrected[end:]

#         except Exception:
#             return text  # Return original if correction fails

#         return corrected

#     def _check_with_azure_openai(self, text: str, local_results: Dict) -> Dict:
#         """Enhanced grammar analysis using Azure OpenAI - GRAMMAR ONLY"""
#         error_count = local_results.get('error_count', 0)
#         word_count = len(text.split())

#         # Updated prompt to focus ONLY on grammar, completely ignore spelling
#         prompt = f"""
# You are an expert English grammar assessor. Respond *only* with valid JSON—no extra explanation, no markdown fences, no comments.

# Analyze this interview transcript for GRAMMAR ONLY (completely ignore spelling and word choice). Provide a JSON object with these exact keys:

# {{
#   "grammar_score": <integer 0–100>,
#   "key_grammar_strengths": ["strength1", "strength2", ...],
#   "key_grammar_issues": ["issue1", "issue2", ...],
#   "specific_grammar_suggestions": ["suggestion1", ...],
#   "grammar_assessment": "<brief assessment as string>"
# }}

# TEXT TO ANALYZE: "{text}"

# CONTEXT:
# - Local grammar tool flagged {error_count} grammar issues in {word_count} words.
# - Focus ONLY on: verb tenses, subject-verb agreement, sentence structure, punctuation for clarity, grammar rules.
# - COMPLETELY IGNORE: spelling errors, word choice, vocabulary, proper names.
# - This is spoken language from an interview - natural speech patterns are acceptable.
# - Do NOT output anything other than a single JSON object with those five keys.
# """

#         try:
#             message = HumanMessage(content=prompt)
#             response = self.azure_llm.invoke([message])
#             raw_content = response.content.strip()

#             # DEBUG: Print or log the raw response content ONCE
#             print("⟳ Azure raw response:", raw_content)

#             # Attempt to extract the JSON substring
#             json_substr = _extract_json_from_text(raw_content)
#             if not json_substr:
#                 raise ValueError("No JSON object found in LLM response.")

#             # Parse it
#             ai_analysis = json.loads(json_substr)
#             return ai_analysis

#         except Exception as e:
#             print(f"Azure parsing/extraction error: {e}\n→ Raw:\n{raw_content}")
#             # Fallback to your existing fallback logic
#             return self._parse_ai_response_fallback(raw_content)

#     def _parse_ai_response_fallback(self, raw: str) -> Dict:
#         """
#         Fallback parser when we cannot extract valid JSON from the LLM.
#         We'll return a very basic placeholder so the UI still shows something.
#         """
#         print("⚠️ Fallback used. Raw LLM content was:")
#         print(raw)
#         return {
#             "grammar_score": 75,
#             "key_grammar_strengths": ["Grammar analysis completed"],
#             "key_grammar_issues": ["Could not parse detailed feedback"],
#             "specific_grammar_suggestions": ["Review grammar structure"],
#             "grammar_assessment": "AI analysis parsing error occurred"
#         }

#     def _merge_results(self, local_results: Dict, ai_results: Dict, text: str) -> Dict:
#         """Merge local and AI analysis results - GRAMMAR ONLY"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))

#         # Calculate comprehensive scores
#         grammar_score = self._calculate_final_grammar_score(local_results, ai_results, word_count)

#         return {
#             # Core metrics - FOCUSED ON GRAMMAR ONLY
#             'grammar_score': grammar_score,

#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': local_results.get('error_count', 0),
#             'word_count': word_count,
#             'sentence_count': sentence_count,

#             # AI insights - GRAMMAR FOCUSED
#             'key_strengths': ai_results.get('key_grammar_strengths', []),
#             'key_issues': ai_results.get('key_grammar_issues', []),
#             'specific_suggestions': ai_results.get('specific_grammar_suggestions', []),
#             'interview_assessment': ai_results.get('grammar_assessment', ''),

#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'hybrid',
#             'ai_used': True
#         }

#     def _finalize_local_results(self, local_results: Dict, text: str) -> Dict:
#         """Finalize results using only local analysis - GRAMMAR ONLY"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
#         error_count = local_results.get('error_count', 0)

#         # Calculate scores based on local analysis
#         grammar_score = self._calculate_local_grammar_score(error_count, word_count)

#         return {
#             # Core metrics - FOCUSED ON GRAMMAR ONLY
#             'grammar_score': grammar_score,

#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': error_count,
#             'word_count': word_count,
#             'sentence_count': sentence_count,

#             # Generated insights
#             'suggestions': self._generate_local_suggestions(local_results, grammar_score),
#             'overall_assessment': self._generate_local_assessment(grammar_score, error_count),

#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'local_only',
#             'ai_used': False
#         }

#     def _calculate_final_grammar_score(self, local_results: Dict, ai_results: Dict, word_count: int) -> float:
#         """Calculate final grammar score combining local and AI analysis"""
#         # Weight local error-based score and AI assessment
#         local_score = self._calculate_local_grammar_score(local_results.get('error_count', 0), word_count)
#         ai_score = ai_results.get('grammar_score', local_score)

#         # Weighted average (favor AI slightly for final score)
#         final_score = (local_score * 0.4) + (ai_score * 0.6)
#         return round(final_score, 1)

#     def _calculate_local_grammar_score(self, error_count: int, word_count: int) -> float:
#         """Calculate grammar score with speech-context adjustments"""
#         if word_count == 0:
#             return 0

#         # More forgiving scoring for speech
#         error_rate = error_count / word_count

#         # Adjusted penalty calculation for speech context
#         # Speech naturally has more variation, so be more lenient
#         penalty = min(error_rate * 150, 40)  # Reduced max penalty from 50 to 40
#         score = max(100 - penalty, 30)  # Higher minimum score (30 vs 20)

#         return round(score, 1)

#     def _generate_local_suggestions(self, local_results: Dict, grammar_score: float) -> List[str]:
#         """Generate speech-appropriate grammar suggestions - GRAMMAR ONLY"""
#         suggestions = []
#         errors = local_results.get('errors', [])

#         # Grammar-specific suggestions only
#         if grammar_score < 70:
#             suggestions.append("Focus on clear sentence structure while speaking")
#             suggestions.append("Practice expressing ideas in complete thoughts")

#         # Error category-based suggestions for speech - GRAMMAR ONLY
#         error_categories = [error.get('category', '') for error in errors]
#         high_severity_errors = [error for error in errors if error.get('severity') == 'high']

#         if 'GRAMMAR' in error_categories or high_severity_errors:
#             suggestions.append("Pay attention to verb tenses and subject-verb agreement")

#         if len(errors) > 5:  # Many errors
#             suggestions.append("Practice speaking more slowly for clearer articulation")

#         return suggestions[:4]  # Limit suggestions

#     def _generate_local_assessment(self, grammar_score: float, error_count: int) -> str:
#         """Generate overall assessment based on local analysis - GRAMMAR ONLY"""
#         if grammar_score >= 85:
#             return f"Excellent grammar! Score: {grammar_score}/100"
#         elif grammar_score >= 70:
#             return f"Good grammar with minor issues. Score: {grammar_score}/100"
#         elif grammar_score >= 50:
#             return f"Adequate grammar with room for improvement. Score: {grammar_score}/100"
#         else:
#             return f"Grammar needs significant improvement. Focus on sentence structure. Score: {grammar_score}/100"

#     def _empty_result(self) -> Dict:
#         """Return empty result for no text"""
#         return {
#             'grammar_score': 0,
#             'error_count': 0,
#             'word_count': 0,
#             'overall_assessment': "No text provided for analysis",
#             'analysis_type': 'empty',
#             'ai_used': False
#         }

#     def _minimal_result(self, text: str, word_count: int) -> Dict:
#         """Return minimal result for very short text"""
#         return {
#             'grammar_score': 85,  # Assume good for very short responses
#             'error_count': 0,
#             'word_count': word_count,
#             'original_text': text,
#             'overall_assessment': f"Response too short ({word_count} words) for detailed analysis",
#             'analysis_type': 'minimal',
#             'ai_used': False
#         }

#     def get_analysis_summary(self) -> Dict:
#         """Get summary of checker capabilities"""
#         return {
#             'local_available': self.local_available,
#             'ai_available': self.ai_available,
#             'hybrid_mode': self.local_available and self.ai_available,
#             'recommended_min_words': getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),
#             'ai_provider': 'Azure OpenAI' if self.ai_available else 'None'
#         }
    

# import language_tool_python
# from langchain_openai import AzureChatOpenAI
# from langchain_core.messages import HumanMessage
# import json
# import re
# import time
# from typing import Dict, List, Optional
# import streamlit as st
# from config.settings import Config

# def _extract_json_from_text(raw: str) -> Optional[str]:
#     """
#     Scan `raw` for the first balanced JSON object or array.
#     Returns the JSON substring (starting at '{' or '[' and ending at matching '}' or ']'),
#     or None if nothing parseable is found.
#     """
#     # Search for a "{" or "[" to begin
#     for start_idx, ch in enumerate(raw):
#         if ch not in ('{', '['):
#             continue
#         open_char = ch
#         close_char = '}' if ch == '{' else ']'
#         balance = 0
#         for end_idx in range(start_idx, len(raw)):
#             if raw[end_idx] == open_char:
#                 balance += 1
#             elif raw[end_idx] == close_char:
#                 balance -= 1
#                 if balance == 0:
#                     # We found a balanced chunk from start_idx..end_idx
#                     return raw[start_idx:end_idx+1]
#     return None


# class HybridGrammarChecker:
#     def __init__(self):
#         """Initialize hybrid grammar checker focused ONLY on grammar (not spelling)"""
#         # Initialize LanguageTool (always available)
#         try:
#             self.language_tool = language_tool_python.LanguageTool('en-US')
#             self.local_available = True
#         except Exception as e:
#             print(f"Warning: LanguageTool initialization failed: {e}")
#             self.language_tool = None
#             self.local_available = False
        
#         # Initialize Azure OpenAI client (optional)
#         self.ai_available = False
#         if Config.is_azure_openai_available():
#             try:
#                 # Setup environment variables
#                 Config.setup_azure_openai_env()
                
#                 # Initialize Azure OpenAI client
#                 self.azure_llm = AzureChatOpenAI(
#                     openai_api_version=Config.AZURE_OPENAI_API_VERSION,
#                     azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
#                     temperature=0.1,
#                     max_tokens=600
#                 )
                
#                 # Test the connection
#                 if self._test_azure_openai_connection():
#                     self.ai_available = True
                    
#             except Exception as e:
#                 print(f"Warning: Azure OpenAI initialization failed: {e}")
#                 self.azure_llm = None
        
#         # Speech-specific error filters - focusing only on grammar
#         self.speech_filters = {
#             'casual_punctuation': True,    # Relax punctuation rules
#             'contractions': True,          # Allow informal contractions
#             'filler_words': True,          # Handle um, uh, etc.
#             'repetition': True,            # Allow natural repetition
#             'incomplete_sentences': True    # Allow sentence fragments
#         }
    
#     def _test_azure_openai_connection(self):
#         """Test Azure OpenAI connection"""
#         try:
#             message = HumanMessage(content="Test")
#             response = self.azure_llm.invoke([message])
#             return True
#         except Exception as e:
#             print(f"Azure OpenAI connection test failed: {e}")
#             return False
    
#     def check_grammar(self, text: str, force_ai: bool = False) -> Dict:
#         """
#         Grammar check using hybrid approach - GRAMMAR ONLY (no spelling)
        
#         Args:
#             text: Text to analyze
#             force_ai: Force AI analysis regardless of conditions
            
#         Returns:
#             Grammar analysis results (excluding spelling)
#         """
#         if not text or not text.strip():
#             return self._empty_result()
        
#         # Clean and prepare text
#         cleaned_text = self._clean_text(text)
#         word_count = len(cleaned_text.split())
        
#         if word_count < 5:  # Too short for meaningful analysis
#             return self._minimal_result(cleaned_text, word_count)
        
#         # Step 1: Local grammar check (LanguageTool) - filter out spelling errors
#         local_results = self._check_with_language_tool(cleaned_text)
        
#         # Step 2: Decide if AI analysis is needed
#         use_ai = force_ai or self._should_use_ai(cleaned_text, local_results, word_count)
        
#         # Step 3: Enhanced AI analysis if conditions are met
#         if use_ai and self.ai_available:
#             try:
#                 ai_results = self._check_with_azure_openai(cleaned_text, local_results)
#                 return self._merge_results(local_results, ai_results, cleaned_text)
#             except Exception as e:
#                 st.warning(f"AI analysis failed, using local results: {str(e)}")
#                 return self._finalize_local_results(local_results, cleaned_text)
        
#         return self._finalize_local_results(local_results, cleaned_text)
    
#     def _clean_text(self, text: str) -> str:
#         """Clean and normalize text for analysis"""
#         # Remove extra whitespace
#         text = re.sub(r'\s+', ' ', text.strip())
        
#         # Remove common speech filler words
#         fillers = [r'\buh+\b', r'\bum+\b', r'\ber+\b', r'\blike\b(?=\s+\w)', r'\byou know\b']
#         for filler in fillers:
#             text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
#         # Clean up punctuation spacing
#         text = re.sub(r'\s+([.!?])', r'\1', text)
#         text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
#         return text.strip()

#     def _should_use_ai(self, text: str, local_results: Dict, word_count: int) -> bool:
#         """Intelligent decision on when to use AI analysis"""
#         if not getattr(Config, 'GRAMMAR_AI_AUTO_TRIGGER', True):
#             return False

#         # Get error count safely
#         error_count = local_results.get('error_count', 0)

#         # Conditions for AI analysis
#         conditions = [
#             word_count >= getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),  # Sufficient text length
#             error_count / word_count > getattr(Config, 'AI_TRIGGER_ERROR_RATE', 0.08) if word_count > 0 else False,  # High error rate
#             word_count > 50,  # Longer responses get AI analysis
#         ]

#         return any(conditions)

#     def _check_with_language_tool(self, text: str) -> Dict:
#         """Perform speech-aware grammar check using LanguageTool - GRAMMAR ONLY"""
#         if not self.local_available:
#             return {'errors': [], 'error_count': 0, 'available': False}

#         try:
#             matches = self.language_tool.check(text)
#             errors = []

#             for match in matches:
#                 # SKIP ALL SPELLING ERRORS - Enhanced filtering
#                 if self._is_spelling_error(match):
#                     continue
                    
#                 # Filter out speech-inappropriate errors
#                 if self._should_ignore_error(match, text):
#                     continue

#                 error = {
#                     'category': match.category,
#                     'rule_id': match.ruleId,
#                     'message': match.message,
#                     'offset': match.offset,
#                     'length': match.errorLength,
#                     'context': match.context,
#                     'suggestions': match.replacements[:3] if match.replacements else [],
#                     'error_text': text[match.offset:match.offset + match.errorLength],
#                     'severity': self._categorize_error_severity_for_speech(match.category, match.ruleId)
#                 }
#                 errors.append(error)

#             return {
#                 'errors': errors,
#                 'error_count': len(errors),
#                 'corrected_text': self._speech_aware_correction(text, errors),
#                 'available': True
#             }

#         except Exception as e:
#             print(f"LanguageTool error: {e}")
#             return {'errors': [], 'error_count': 0, 'available': False}
    
#     def _is_spelling_error(self, match) -> bool:
#         """Check if the error is a spelling error that should be ignored - ENHANCED"""
#         # Categories that indicate spelling errors
#         spelling_categories = ['TYPOS']
        
#         # Rule IDs that are spelling-related - EXPANDED LIST
#         spelling_rule_ids = [
#             'MORFOLOGIK_RULE_EN_US',
#             'HUNSPELL_RULE',
#             'SPELLING_RULE',
#             'POSSIBLE_SPELLING_MISTAKE',
#             'MORFOLOGIK_RULE',
#             'SPELLER_RULE',
#             'DICTIONARY_RULE'
#         ]
        
#         # Messages that indicate spelling errors - EXPANDED LIST
#         spelling_messages = [
#             'possible spelling mistake',
#             'spelling mistake found',
#             'use a different word',
#             'did you mean',
#             'misspelled',
#             'not found in dictionary',
#             'unknown word',
#             'correct spelling',
#             'typo',
#             'misspelling'
#         ]
        
#         message_lower = match.message.lower()
        
#         # Check if it's a spelling error based on category, rule ID, or message
#         is_spelling = (match.category in spelling_categories or 
#                       match.ruleId in spelling_rule_ids or
#                       any(msg in message_lower for msg in spelling_messages))
        
#         # Additional check: if it's about proper names/capitalized words (often names)
#         if not is_spelling:
#             error_text = match.context[match.offset:match.offset + match.errorLength] if hasattr(match, 'context') else ""
#             if error_text and error_text[0].isupper() and any(msg in message_lower for msg in ['spelling', 'unknown']):
#                 is_spelling = True
        
#         return is_spelling

#     def _should_ignore_error(self, match, text: str) -> bool:
#         """Determine if an error should be ignored for speech analysis"""
#         rule_id = match.ruleId
#         category = match.category
#         error_text = text[match.offset:match.offset + match.errorLength].strip()
#         message = match.message.lower()

#         # 1. Ignore casual punctuation rules for speech
#         if self._is_casual_punctuation_error(rule_id, message):
#             return True

#         # 2. Ignore overly formal grammar rules
#         if self._is_overly_formal_rule(rule_id, message):
#             return True

#         # 3. Ignore common speech patterns
#         if self._is_natural_speech_pattern(error_text, message):
#             return True

#         # 4. Ignore transcription artifacts
#         if self._is_transcription_artifact(error_text, message):
#             return True

#         return False

#     def _is_casual_punctuation_error(self, rule_id: str, message: str) -> bool:
#         """Check if error is about casual punctuation acceptable in speech"""
#         casual_punctuation_rules = [
#             'COMMA_COMPOUND_SENTENCE',      # Comma before 'and' in compound sentences
#             'OXFORD_COMMA',                 # Oxford comma usage
#             'COMMA_PARENTHETICAL',          # Commas around parenthetical phrases
#             'SEMICOLON_COMPOUND',           # Semicolon usage
#             'EN_QUOTES',                    # Quote mark consistency
#             'ELLIPSIS',                     # Ellipsis usage
#         ]

#         casual_messages = [
#             "comma before 'and'",
#             "use a comma before",
#             "comma after",
#             "semicolon instead",
#             "quotation marks",
#             "ellipsis"
#         ]

#         return (rule_id in casual_punctuation_rules or 
#                 any(msg in message for msg in casual_messages))

#     def _is_overly_formal_rule(self, rule_id: str, message: str) -> bool:
#         """Check if error is about overly formal grammar rules"""
#         formal_rules = [
#             'SENTENCE_FRAGMENT',            # Allow fragments in speech
#             'INFORMAL_CONTRACTIONS',        # Allow contractions
#             'COLLOQUIAL_WORD',             # Allow colloquial language
#             'PASSIVE_VOICE',               # Don't enforce active voice
#             'WORDINESS',                   # Allow some redundancy in speech
#         ]

#         formal_messages = [
#             'sentence fragment',
#             'avoid using',
#             'too informal',
#             'passive voice',
#             'wordy',
#             'redundant'
#         ]

#         return (rule_id in formal_rules or 
#                 any(msg in message for msg in formal_messages))

#     def _is_natural_speech_pattern(self, error_text: str, message: str) -> bool:
#         """Check if error represents natural speech patterns"""
#         # Common speech patterns that shouldn't be flagged
#         natural_patterns = [
#             'um', 'uh', 'er', 'ah',        # Filler words
#             'like', 'you know', 'so',      # Common speech connectors
#             'well', 'actually', 'basically' # Discourse markers
#         ]

#         # Repetition patterns (common in speech)
#         if any(pattern in error_text.lower() for pattern in natural_patterns):
#             return True

#         # Check for natural repetition
#         words = error_text.lower().split()
#         if len(words) >= 2 and words[0] == words[1]:  # Word repetition
#             return True

#         return False

#     def _is_transcription_artifact(self, error_text: str, message: str) -> bool:
#         """Check if error is likely a transcription artifact"""
#         transcription_artifacts = [
#             'single letter errors',         # OCR/ASR single character mistakes
#             'missing space',                # Word concatenation
#             'extra space',                  # Word separation
#             'capitalization'                # Inconsistent caps from ASR
#         ]

#         # Very short errors (1-2 characters) are often transcription issues
#         if len(error_text.strip()) <= 2:
#             return True

#         return any(artifact in message for artifact in transcription_artifacts)

#     def _categorize_error_severity_for_speech(self, category: str, rule_id: str) -> str:
#         """Categorize error severity specifically for speech context - GRAMMAR ONLY"""
#         # More lenient severity for speech - ONLY GRAMMAR MATTERS
#         high_severity = ['GRAMMAR']  # Only major grammar issues
#         medium_severity = ['STYLE']  # Style issues (no spelling)

#         # Reduce severity for speech-common issues
#         speech_reduced_severity = [
#             'COMMA_COMPOUND_SENTENCE',
#             'OXFORD_COMMA',
#             'SENTENCE_FRAGMENT'
#         ]

#         if rule_id in speech_reduced_severity:
#             return 'low'
#         elif category in high_severity:
#             return 'medium'  # Reduce from high to medium
#         elif category in medium_severity:
#             return 'low'     # Reduce from medium to low
#         else:
#             return 'low'

#     def _speech_aware_correction(self, text: str, errors: List[Dict]) -> str:
#         """Apply only appropriate corrections for speech context - GRAMMAR ONLY"""
#         # For speech, only apply corrections for:
#         # 1. Clear grammatical errors (verb tense, subject-verb agreement)
#         # 2. Obvious grammatical mistakes (NOT spelling)

#         corrected = text
#         # REMOVED spelling-related rules, kept only grammar rules
#         high_confidence_rules = [
#             'AGREEMENT_SENT_START',      # Subject-verb agreement
#             'ENGLISH_WORD_REPEAT_RULE',  # Word repetition
#             'VERB_TENSE_AGREEMENT',      # Verb tense issues
#             'GRAMMAR_RULE'               # General grammar rules
#         ]

#         # Only apply corrections for high-confidence, speech-appropriate grammar rules
#         try:
#             if self.local_available:
#                 # Get all matches again
#                 matches = self.language_tool.check(text)

#                 # Filter to only speech-appropriate corrections
#                 for match in reversed(matches):  # Reverse to maintain offsets
#                     if (match.ruleId in high_confidence_rules and 
#                         not self._is_spelling_error(match) and  # Skip spelling
#                         not self._should_ignore_error(match, text) and
#                         match.replacements):

#                         # Apply the correction
#                         start = match.offset
#                         end = match.offset + match.errorLength
#                         corrected = corrected[:start] + match.replacements[0] + corrected[end:]

#         except Exception:
#             return text  # Return original if correction fails

#         return corrected

#     def _check_with_azure_openai(self, text: str, local_results: Dict) -> Dict:
#         """Enhanced grammar analysis using Azure OpenAI - GRAMMAR ONLY"""
#         error_count = local_results.get('error_count', 0)
#         word_count = len(text.split())

#         # Updated prompt to focus ONLY on grammar, completely ignore spelling
#         prompt = f"""
# You are an expert English grammar assessor. Respond *only* with valid JSON—no extra explanation, no markdown fences, no comments.

# Analyze this interview transcript for GRAMMAR ONLY (completely ignore spelling and word choice). Provide a JSON object with these exact keys:

# {{
#   "grammar_score": <integer 0–100>,
#   "key_grammar_strengths": ["strength1", "strength2", ...],
#   "key_grammar_issues": ["issue1", "issue2", ...],
#   "specific_grammar_suggestions": ["suggestion1", ...],
#   "grammar_assessment": "<brief assessment as string>"
# }}

# TEXT TO ANALYZE: "{text}"

# CONTEXT:
# - Local grammar tool flagged {error_count} grammar issues in {word_count} words.
# - Focus ONLY on: verb tenses, subject-verb agreement, sentence structure, punctuation for clarity, grammar rules.
# - COMPLETELY IGNORE: spelling errors, word choice, vocabulary, proper names.
# - This is spoken language from an interview - natural speech patterns are acceptable.
# - Do NOT output anything other than a single JSON object with those five keys.
# """

#         try:
#             message = HumanMessage(content=prompt)
#             response = self.azure_llm.invoke([message])
#             raw_content = response.content.strip()

#             # Extract JSON
#             json_substr = _extract_json_from_text(raw_content)
#             if not json_substr:
#                 raise ValueError("No JSON object found in LLM response.")

#             # Parse it
#             ai_analysis = json.loads(json_substr)
#             return ai_analysis

#         except Exception as e:
#             print(f"Azure parsing/extraction error: {e}")
#             return self._parse_ai_response_fallback(raw_content if 'raw_content' in locals() else "")

#     def _parse_ai_response_fallback(self, raw: str) -> Dict:
#         """Fallback parser when we cannot extract valid JSON from the LLM."""
#         return {
#             "grammar_score": 75,
#             "key_grammar_strengths": ["Grammar analysis completed"],
#             "key_grammar_issues": ["Could not parse detailed feedback"],
#             "specific_grammar_suggestions": ["Review grammar structure"],
#             "grammar_assessment": "AI analysis parsing error occurred"
#         }

#     def _merge_results(self, local_results: Dict, ai_results: Dict, text: str) -> Dict:
#         """Merge local and AI analysis results - GRAMMAR ONLY"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))

#         # Calculate comprehensive scores
#         grammar_score = self._calculate_final_grammar_score(local_results, ai_results, word_count)

#         return {
#             # Core metrics - FOCUSED ON GRAMMAR ONLY
#             'grammar_score': grammar_score,

#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': local_results.get('error_count', 0),
#             'word_count': word_count,
#             'sentence_count': sentence_count,

#             # AI insights - GRAMMAR FOCUSED
#             'key_strengths': ai_results.get('key_grammar_strengths', []),
#             'key_issues': ai_results.get('key_grammar_issues', []),
#             'specific_suggestions': ai_results.get('specific_grammar_suggestions', []),
#             'interview_assessment': ai_results.get('grammar_assessment', ''),

#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'hybrid',
#             'ai_used': True
#         }

#     def _finalize_local_results(self, local_results: Dict, text: str) -> Dict:
#         """Finalize results using only local analysis - GRAMMAR ONLY"""
#         word_count = len(text.split())
#         sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
#         error_count = local_results.get('error_count', 0)

#         # Calculate scores based on local analysis
#         grammar_score = self._calculate_local_grammar_score(error_count, word_count)

#         return {
#             # Core metrics - FOCUSED ON GRAMMAR ONLY
#             'grammar_score': grammar_score,

#             # Detailed analysis
#             'local_errors': local_results.get('errors', []),
#             'error_count': error_count,
#             'word_count': word_count,
#             'sentence_count': sentence_count,

#             # Generated insights
#             'suggestions': self._generate_local_suggestions(local_results, grammar_score),
#             'overall_assessment': self._generate_local_assessment(grammar_score, error_count),

#             # Additional data
#             'corrected_text': local_results.get('corrected_text', text),
#             'original_text': text,
#             'analysis_type': 'local_only',
#             'ai_used': False
#         }

#     def _calculate_final_grammar_score(self, local_results: Dict, ai_results: Dict, word_count: int) -> float:
#         """Calculate final grammar score combining local and AI analysis"""
#         # Weight local error-based score and AI assessment
#         local_score = self._calculate_local_grammar_score(local_results.get('error_count', 0), word_count)
#         ai_score = ai_results.get('grammar_score', local_score)

#         # Weighted average (favor AI slightly for final score)
#         final_score = (local_score * 0.4) + (ai_score * 0.6)
#         return round(final_score, 1)

#     def _calculate_local_grammar_score(self, error_count: int, word_count: int) -> float:
#         """Calculate grammar score with speech-context adjustments"""
#         if word_count == 0:
#             return 0

#         # More forgiving scoring for speech
#         error_rate = error_count / word_count

#         # Adjusted penalty calculation for speech context
#         # Speech naturally has more variation, so be more lenient
#         penalty = min(error_rate * 150, 40)  # Reduced max penalty from 50 to 40
#         score = max(100 - penalty, 30)  # Higher minimum score (30 vs 20)

#         return round(score, 1)

#     def _generate_local_suggestions(self, local_results: Dict, grammar_score: float) -> List[str]:
#         """Generate speech-appropriate grammar suggestions - GRAMMAR ONLY"""
#         suggestions = []
#         errors = local_results.get('errors', [])

#         # Grammar-specific suggestions only
#         if grammar_score < 70:
#             suggestions.append("Focus on clear sentence structure while speaking")
#             suggestions.append("Practice expressing ideas in complete thoughts")

#         # Error category-based suggestions for speech - GRAMMAR ONLY
#         error_categories = [error.get('category', '') for error in errors]
#         high_severity_errors = [error for error in errors if error.get('severity') == 'high']

#         if 'GRAMMAR' in error_categories or high_severity_errors:
#             suggestions.append("Pay attention to verb tenses and subject-verb agreement")

#         if len(errors) > 5:  # Many errors
#             suggestions.append("Practice speaking more slowly for clearer articulation")

#         return suggestions[:4]  # Limit suggestions

#     def _generate_local_assessment(self, grammar_score: float, error_count: int) -> str:
#         """Generate overall assessment based on local analysis - GRAMMAR ONLY"""
#         if grammar_score >= 85:
#             return f"Excellent grammar! Score: {grammar_score}/100"
#         elif grammar_score >= 70:
#             return f"Good grammar with minor issues. Score: {grammar_score}/100"
#         elif grammar_score >= 50:
#             return f"Adequate grammar with room for improvement. Score: {grammar_score}/100"
#         else:
#             return f"Grammar needs significant improvement. Focus on sentence structure. Score: {grammar_score}/100"

#     def _empty_result(self) -> Dict:
#         """Return empty result for no text"""
#         return {
#             'grammar_score': 0,
#             'error_count': 0,
#             'word_count': 0,
#             'overall_assessment': "No text provided for analysis",
#             'analysis_type': 'empty',
#             'ai_used': False
#         }

#     def _minimal_result(self, text: str, word_count: int) -> Dict:
#         """Return minimal result for very short text"""
#         return {
#             'grammar_score': 85,  # Assume good for very short responses
#             'error_count': 0,
#             'word_count': word_count,
#             'original_text': text,
#             'overall_assessment': f"Response too short ({word_count} words) for detailed analysis",
#             'analysis_type': 'minimal',
#             'ai_used': False
#         }

#     def get_analysis_summary(self) -> Dict:
#         """Get summary of checker capabilities"""
#         return {
#             'local_available': self.local_available,
#             'ai_available': self.ai_available,
#             'hybrid_mode': self.local_available and self.ai_available,
#             'recommended_min_words': getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),
#             'ai_provider': 'Azure OpenAI' if self.ai_available else 'None'
#         }

import language_tool_python
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
import json
import re
import time
from typing import Dict, List, Optional, Tuple
import streamlit as st
from config.settings import Config

def _extract_json_from_text(raw: str) -> Optional[str]:
    """
    Scan `raw` for the first balanced JSON object or array.
    Returns the JSON substring (starting at '{' or '[' and ending at matching '}' or ']'),
    or None if nothing parseable is found.
    """
    # Search for a "{" or "[" to begin
    for start_idx, ch in enumerate(raw):
        if ch not in ('{', '['):
            continue
        open_char = ch
        close_char = '}' if ch == '{' else ']'
        balance = 0
        for end_idx in range(start_idx, len(raw)):
            if raw[end_idx] == open_char:
                balance += 1
            elif raw[end_idx] == close_char:
                balance -= 1
                if balance == 0:
                    # We found a balanced chunk from start_idx..end_idx
                    return raw[start_idx:end_idx+1]
    return None


class HybridGrammarChecker:
    def __init__(self):
        """Initialize hybrid grammar checker focused ONLY on grammar (not spelling)"""
        # Initialize LanguageTool (always available)
        try:
            self.language_tool = language_tool_python.LanguageTool('en-US')
            self.local_available = True
        except Exception as e:
            print(f"Warning: LanguageTool initialization failed: {e}")
            self.language_tool = None
            self.local_available = False
        
        # Initialize Azure OpenAI client (optional)
        self.ai_available = False
        if Config.is_azure_openai_available():
            try:
                # Setup environment variables
                Config.setup_azure_openai_env()
                
                # Initialize Azure OpenAI client
                self.azure_llm = AzureChatOpenAI(
                    openai_api_version=Config.AZURE_OPENAI_API_VERSION,
                    azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
                    temperature=0.1,
                    max_tokens=600
                )
                
                # Test the connection
                if self._test_azure_openai_connection():
                    self.ai_available = True
                    
            except Exception as e:
                print(f"Warning: Azure OpenAI initialization failed: {e}")
                self.azure_llm = None
        
        # Speech-specific error filters - focusing only on grammar
        self.speech_filters = {
            'casual_punctuation': True,    # Relax punctuation rules
            'contractions': True,          # Allow informal contractions
            'filler_words': True,          # Handle um, uh, etc.
            'repetition': True,            # Allow natural repetition
            'incomplete_sentences': True    # Allow sentence fragments
        }
    
    def _test_azure_openai_connection(self):
        """Test Azure OpenAI connection"""
        try:
            message = HumanMessage(content="Test")
            response = self.azure_llm.invoke([message])
            return True
        except Exception as e:
            print(f"Azure OpenAI connection test failed: {e}")
            return False
    
    def check_grammar(self, text: str, force_ai: bool = False) -> Dict:
        """
        Grammar check using hybrid approach - GRAMMAR ONLY with filler word penalty
        
        Args:
            text: Text to analyze
            force_ai: Force AI analysis regardless of conditions
            
        Returns:
            Grammar analysis results with filler word penalty
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # Clean and prepare text, get filler count
        cleaned_text, filler_count = self._clean_text(text)
        word_count = len(cleaned_text.split())
        original_word_count = len(text.split())
        
        if word_count < 5:  # Too short for meaningful analysis
            return self._minimal_result(cleaned_text, word_count, filler_count)
        
        # Step 1: Local grammar check (LanguageTool) - filter out spelling errors
        local_results = self._check_with_language_tool(cleaned_text)
        
        # Add filler word information to local results
        local_results['filler_count'] = filler_count
        local_results['original_word_count'] = original_word_count
        
        # Step 2: Decide if AI analysis is needed
        use_ai = force_ai or self._should_use_ai(cleaned_text, local_results, word_count)
        
        # Step 3: Enhanced AI analysis if conditions are met
        if use_ai and self.ai_available:
            try:
                ai_results = self._check_with_azure_openai(cleaned_text, local_results)
                return self._merge_results(local_results, ai_results, cleaned_text, text)
            except Exception as e:
                st.warning(f"AI analysis failed, using local results: {str(e)}")
                return self._finalize_local_results(local_results, cleaned_text, text)
        
        return self._finalize_local_results(local_results, cleaned_text, text)
    
    def _clean_text(self, text: str) -> Tuple[str, int]:
        """Clean and normalize text for analysis, return cleaned text and filler count"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Count and remove common speech filler words
        fillers = [
            r'\buh+\b', r'\bum+\b', r'\bumm+\b', r'\buhhh+\b', r'\ber+\b', 
            r'\blike\b(?=\s+\w)', r'\byou know\b', r'\bwell\b(?=\s+\w)', 
            r'\bso\b(?=\s+\w)', r'\bactually\b(?=\s+\w)', r'\bbasically\b(?=\s+\w)',
            r'\bhm+\b', r'\bhmm+\b', r'\bah+\b', r'\boh+\b'
        ]
        
        filler_count = 0
        for filler in fillers:
            matches = re.findall(filler, text, flags=re.IGNORECASE)
            filler_count += len(matches)
            text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
        # Clean up punctuation spacing
        text = re.sub(r'\s+([.!?])', r'\1', text)
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        return text.strip(), filler_count

    def _should_use_ai(self, text: str, local_results: Dict, word_count: int) -> bool:
        """Intelligent decision on when to use AI analysis"""
        if not getattr(Config, 'GRAMMAR_AI_AUTO_TRIGGER', True):
            return False

        # Get error count safely
        error_count = local_results.get('error_count', 0)

        # Conditions for AI analysis
        conditions = [
            word_count >= getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),  # Sufficient text length
            error_count / word_count > getattr(Config, 'AI_TRIGGER_ERROR_RATE', 0.08) if word_count > 0 else False,  # High error rate
            word_count > 50,  # Longer responses get AI analysis
        ]

        return any(conditions)

    def _check_with_language_tool(self, text: str) -> Dict:
        """Perform speech-aware grammar check using LanguageTool - GRAMMAR ONLY"""
        if not self.local_available:
            return {'errors': [], 'error_count': 0, 'available': False}

        try:
            matches = self.language_tool.check(text)
            errors = []

            for match in matches:
                # SKIP ALL SPELLING ERRORS - Enhanced filtering
                if self._is_spelling_error(match):
                    continue
                    
                # Filter out speech-inappropriate errors
                if self._should_ignore_error(match, text):
                    continue

                error = {
                    'category': match.category,
                    'rule_id': match.ruleId,
                    'message': match.message,
                    'offset': match.offset,
                    'length': match.errorLength,
                    'context': match.context,
                    'suggestions': match.replacements[:3] if match.replacements else [],
                    'error_text': text[match.offset:match.offset + match.errorLength],
                    'severity': self._categorize_error_severity_for_speech(match.category, match.ruleId)
                }
                errors.append(error)

            return {
                'errors': errors,
                'error_count': len(errors),
                'corrected_text': self._speech_aware_correction(text, errors),
                'available': True
            }

        except Exception as e:
            print(f"LanguageTool error: {e}")
            return {'errors': [], 'error_count': 0, 'available': False}
    
    def _is_spelling_error(self, match) -> bool:
        """Check if the error is a spelling error that should be ignored - ENHANCED"""
        # Categories that indicate spelling errors
        spelling_categories = ['TYPOS']
        
        # Rule IDs that are spelling-related - EXPANDED LIST
        spelling_rule_ids = [
            'MORFOLOGIK_RULE_EN_US',
            'HUNSPELL_RULE',
            'SPELLING_RULE',
            'POSSIBLE_SPELLING_MISTAKE',
            'MORFOLOGIK_RULE',
            'SPELLER_RULE',
            'DICTIONARY_RULE'
        ]
        
        # Messages that indicate spelling errors - EXPANDED LIST
        spelling_messages = [
            'possible spelling mistake',
            'spelling mistake found',
            'use a different word',
            'did you mean',
            'misspelled',
            'not found in dictionary',
            'unknown word',
            'correct spelling',
            'typo',
            'misspelling'
        ]
        
        message_lower = match.message.lower()
        
        # Check if it's a spelling error based on category, rule ID, or message
        is_spelling = (match.category in spelling_categories or 
                      match.ruleId in spelling_rule_ids or
                      any(msg in message_lower for msg in spelling_messages))
        
        # Additional check: if it's about proper names/capitalized words (often names)
        if not is_spelling:
            error_text = match.context[match.offset:match.offset + match.errorLength] if hasattr(match, 'context') else ""
            if error_text and error_text[0].isupper() and any(msg in message_lower for msg in ['spelling', 'unknown']):
                is_spelling = True
        
        return is_spelling

    def _should_ignore_error(self, match, text: str) -> bool:
        """Determine if an error should be ignored for speech analysis"""
        rule_id = match.ruleId
        category = match.category
        error_text = text[match.offset:match.offset + match.errorLength].strip()
        message = match.message.lower()

        # 1. Ignore casual punctuation rules for speech
        if self._is_casual_punctuation_error(rule_id, message):
            return True

        # 2. Ignore overly formal grammar rules
        if self._is_overly_formal_rule(rule_id, message):
            return True

        # 3. Ignore common speech patterns
        if self._is_natural_speech_pattern(error_text, message):
            return True

        # 4. Ignore transcription artifacts
        if self._is_transcription_artifact(error_text, message):
            return True

        return False

    def _is_casual_punctuation_error(self, rule_id: str, message: str) -> bool:
        """Check if error is about casual punctuation acceptable in speech"""
        casual_punctuation_rules = [
            'COMMA_COMPOUND_SENTENCE',      # Comma before 'and' in compound sentences
            'OXFORD_COMMA',                 # Oxford comma usage
            'COMMA_PARENTHETICAL',          # Commas around parenthetical phrases
            'SEMICOLON_COMPOUND',           # Semicolon usage
            'EN_QUOTES',                    # Quote mark consistency
            'ELLIPSIS',                     # Ellipsis usage
        ]

        casual_messages = [
            "comma before 'and'",
            "use a comma before",
            "comma after",
            "semicolon instead",
            "quotation marks",
            "ellipsis"
        ]

        return (rule_id in casual_punctuation_rules or 
                any(msg in message for msg in casual_messages))

    def _is_overly_formal_rule(self, rule_id: str, message: str) -> bool:
        """Check if error is about overly formal grammar rules"""
        formal_rules = [
            'SENTENCE_FRAGMENT',            # Allow fragments in speech
            'INFORMAL_CONTRACTIONS',        # Allow contractions
            'COLLOQUIAL_WORD',             # Allow colloquial language
            'PASSIVE_VOICE',               # Don't enforce active voice
            'WORDINESS',                   # Allow some redundancy in speech
        ]

        formal_messages = [
            'sentence fragment',
            'avoid using',
            'too informal',
            'passive voice',
            'wordy',
            'redundant'
        ]

        return (rule_id in formal_rules or 
                any(msg in message for msg in formal_messages))

    def _is_natural_speech_pattern(self, error_text: str, message: str) -> bool:
        """Check if error represents natural speech patterns"""
        # Common speech patterns that shouldn't be flagged
        natural_patterns = [
            'um', 'uh', 'er', 'ah',        # Filler words
            'like', 'you know', 'so',      # Common speech connectors
            'well', 'actually', 'basically' # Discourse markers
        ]

        # Repetition patterns (common in speech)
        if any(pattern in error_text.lower() for pattern in natural_patterns):
            return True

        # Check for natural repetition
        words = error_text.lower().split()
        if len(words) >= 2 and words[0] == words[1]:  # Word repetition
            return True

        return False

    def _is_transcription_artifact(self, error_text: str, message: str) -> bool:
        """Check if error is likely a transcription artifact"""
        transcription_artifacts = [
            'single letter errors',         # OCR/ASR single character mistakes
            'missing space',                # Word concatenation
            'extra space',                  # Word separation
            'capitalization'                # Inconsistent caps from ASR
        ]

        # Very short errors (1-2 characters) are often transcription issues
        if len(error_text.strip()) <= 2:
            return True

        return any(artifact in message for artifact in transcription_artifacts)

    def _categorize_error_severity_for_speech(self, category: str, rule_id: str) -> str:
        """Categorize error severity specifically for speech context - GRAMMAR ONLY"""
        # More lenient severity for speech - ONLY GRAMMAR MATTERS
        high_severity = ['GRAMMAR']  # Only major grammar issues
        medium_severity = ['STYLE']  # Style issues (no spelling)

        # Reduce severity for speech-common issues
        speech_reduced_severity = [
            'COMMA_COMPOUND_SENTENCE',
            'OXFORD_COMMA',
            'SENTENCE_FRAGMENT'
        ]

        if rule_id in speech_reduced_severity:
            return 'low'
        elif category in high_severity:
            return 'medium'  # Reduce from high to medium
        elif category in medium_severity:
            return 'low'     # Reduce from medium to low
        else:
            return 'low'

    def _speech_aware_correction(self, text: str, errors: List[Dict]) -> str:
        """Apply only appropriate corrections for speech context - GRAMMAR ONLY"""
        # For speech, only apply corrections for:
        # 1. Clear grammatical errors (verb tense, subject-verb agreement)
        # 2. Obvious grammatical mistakes (NOT spelling)

        corrected = text
        # REMOVED spelling-related rules, kept only grammar rules
        high_confidence_rules = [
            'AGREEMENT_SENT_START',      # Subject-verb agreement
            'ENGLISH_WORD_REPEAT_RULE',  # Word repetition
            'VERB_TENSE_AGREEMENT',      # Verb tense issues
            'GRAMMAR_RULE'               # General grammar rules
        ]

        # Only apply corrections for high-confidence, speech-appropriate grammar rules
        try:
            if self.local_available:
                # Get all matches again
                matches = self.language_tool.check(text)

                # Filter to only speech-appropriate corrections
                for match in reversed(matches):  # Reverse to maintain offsets
                    if (match.ruleId in high_confidence_rules and 
                        not self._is_spelling_error(match) and  # Skip spelling
                        not self._should_ignore_error(match, text) and
                        match.replacements):

                        # Apply the correction
                        start = match.offset
                        end = match.offset + match.errorLength
                        corrected = corrected[:start] + match.replacements[0] + corrected[end:]

        except Exception:
            return text  # Return original if correction fails

        return corrected

    def _check_with_azure_openai(self, text: str, local_results: Dict) -> Dict:
        """Enhanced grammar analysis using Azure OpenAI - GRAMMAR ONLY"""
        error_count = local_results.get('error_count', 0)
        word_count = len(text.split())
        filler_count = local_results.get('filler_count', 0)

        # Updated prompt to focus ONLY on grammar, completely ignore spelling
        prompt = f"""
You are an expert English grammar assessor. Respond *only* with valid JSON—no extra explanation, no markdown fences, no comments.

Analyze this interview transcript for GRAMMAR ONLY (completely ignore spelling and word choice). Provide a JSON object with these exact keys:

{{
  "grammar_score": <integer 0–100>,
  "key_grammar_strengths": ["strength1", "strength2", ...],
  "key_grammar_issues": ["issue1", "issue2", ...],
  "specific_grammar_suggestions": ["suggestion1", ...],
  "grammar_assessment": "<brief assessment as string>"
}}

TEXT TO ANALYZE: "{text}"

CONTEXT:
- Local grammar tool flagged {error_count} grammar issues in {word_count} words.
- {filler_count} filler words were detected and removed from the original text.
- Focus ONLY on: verb tenses, subject-verb agreement, sentence structure, punctuation for clarity, grammar rules.
- COMPLETELY IGNORE: spelling errors, word choice, vocabulary, proper names.
- This is spoken language from an interview - natural speech patterns are acceptable.
- Consider the filler word count when assessing overall communication quality.
- Do NOT output anything other than a single JSON object with those five keys.
"""

        try:
            message = HumanMessage(content=prompt)
            response = self.azure_llm.invoke([message])
            raw_content = response.content.strip()

            # Extract JSON
            json_substr = _extract_json_from_text(raw_content)
            if not json_substr:
                raise ValueError("No JSON object found in LLM response.")

            # Parse it
            ai_analysis = json.loads(json_substr)
            return ai_analysis

        except Exception as e:
            print(f"Azure parsing/extraction error: {e}")
            return self._parse_ai_response_fallback(raw_content if 'raw_content' in locals() else "")

    def _parse_ai_response_fallback(self, raw: str) -> Dict:
        """Fallback parser when we cannot extract valid JSON from the LLM."""
        return {
            "grammar_score": 75,
            "key_grammar_strengths": ["Grammar analysis completed"],
            "key_grammar_issues": ["Could not parse detailed feedback"],
            "specific_grammar_suggestions": ["Review grammar structure"],
            "grammar_assessment": "AI analysis parsing error occurred"
        }

    def _merge_results(self, local_results: Dict, ai_results: Dict, text: str, original_text: str) -> Dict:
        """Merge local and AI analysis results - GRAMMAR ONLY with filler analysis"""
        word_count = len(text.split())
        sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
        filler_count = local_results.get('filler_count', 0)
        original_word_count = local_results.get('original_word_count', word_count)

        # Calculate comprehensive scores with filler penalty
        grammar_score = self._calculate_final_grammar_score(local_results, ai_results, word_count)

        return {
            # Core metrics - FOCUSED ON GRAMMAR ONLY
            'grammar_score': grammar_score,

            # Detailed analysis
            'local_errors': local_results.get('errors', []),
            'error_count': local_results.get('error_count', 0),
            'filler_count': filler_count,
            'filler_rate': round((filler_count / original_word_count * 100), 1) if original_word_count > 0 else 0,
            'word_count': word_count,
            'original_word_count': original_word_count,
            'sentence_count': sentence_count,

            # AI insights - GRAMMAR FOCUSED
            'key_strengths': ai_results.get('key_grammar_strengths', []),
            'key_issues': ai_results.get('key_grammar_issues', []),
            'specific_suggestions': ai_results.get('specific_grammar_suggestions', []),
            'interview_assessment': ai_results.get('grammar_assessment', ''),

            # Additional data
            'corrected_text': local_results.get('corrected_text', text),
            'original_text': original_text,
            'cleaned_text': text,
            'analysis_type': 'hybrid',
            'ai_used': True
        }

    def _finalize_local_results(self, local_results: Dict, text: str, original_text: str) -> Dict:
        """Finalize results using only local analysis - GRAMMAR ONLY with filler penalty"""
        word_count = len(text.split())
        sentence_count = max(1, len([s for s in text.split('.') if s.strip()]))
        error_count = local_results.get('error_count', 0)
        filler_count = local_results.get('filler_count', 0)
        original_word_count = local_results.get('original_word_count', word_count)

        # Calculate scores based on local analysis with filler penalty
        grammar_score = self._calculate_local_grammar_score(error_count, word_count, filler_count, original_word_count)

        return {
            # Core metrics - FOCUSED ON GRAMMAR ONLY
            'grammar_score': grammar_score,

            # Detailed analysis
            'local_errors': local_results.get('errors', []),
            'error_count': error_count,
            'filler_count': filler_count,
            'filler_rate': round((filler_count / original_word_count * 100), 1) if original_word_count > 0 else 0,
            'word_count': word_count,
            'original_word_count': original_word_count,
            'sentence_count': sentence_count,

            # Generated insights
            'suggestions': self._generate_local_suggestions(local_results, grammar_score, filler_count),
            'overall_assessment': self._generate_local_assessment(grammar_score, error_count, filler_count),

            # Additional data
            'corrected_text': local_results.get('corrected_text', text),
            'original_text': original_text,
            'cleaned_text': text,
            'analysis_type': 'local_only',
            'ai_used': False
        }

    def _calculate_final_grammar_score(self, local_results: Dict, ai_results: Dict, word_count: int) -> float:
        """Calculate final grammar score combining local and AI analysis with filler penalty"""
        filler_count = local_results.get('filler_count', 0)
        original_word_count = local_results.get('original_word_count', word_count)
        
        # Weight local error-based score and AI assessment
        local_score = self._calculate_local_grammar_score(
            local_results.get('error_count', 0), 
            word_count, 
            filler_count, 
            original_word_count
        )
        ai_score = ai_results.get('grammar_score', local_score)
        
        # Apply filler penalty to AI score as well
        if original_word_count > 0:
            filler_rate = filler_count / original_word_count
            filler_penalty = min(filler_rate * 100, 20)
            ai_score = max(ai_score - filler_penalty, 10)

        # Weighted average (favor AI slightly for final score)
        final_score = (local_score * 0.4) + (ai_score * 0.6)
        return round(final_score, 1)

    def _calculate_local_grammar_score(self, error_count: int, word_count: int, filler_count: int = 0, original_word_count: int = None) -> float:
        """Calculate grammar score with speech-context adjustments and filler penalty"""
        if word_count == 0:
            return 0

        # Calculate filler word penalty
        if original_word_count and original_word_count > 0:
            filler_rate = filler_count / original_word_count
            # Penalty: 1 point per 1% filler words (max 20 points penalty)
            filler_penalty = min(filler_rate * 100, 20)
        else:
            filler_penalty = 0

        # More forgiving scoring for speech
        error_rate = error_count / word_count

        # Adjusted penalty calculation for speech context
        grammar_penalty = min(error_rate * 150, 40)  # Max 40 points for grammar errors
        
        # Total penalty = grammar errors + filler words
        total_penalty = grammar_penalty + filler_penalty
        score = max(100 - total_penalty, 10)  # Minimum score of 10

        return round(score, 1)

    def _generate_local_suggestions(self, local_results: Dict, grammar_score: float, filler_count: int = 0) -> List[str]:
        """Generate speech-appropriate grammar suggestions - GRAMMAR ONLY with filler feedback"""
        suggestions = []
        errors = local_results.get('errors', [])
        
        # Filler word specific suggestions
        if filler_count > 0:
            if filler_count >= 5:
                suggestions.append(f"Reduce filler words (found {filler_count}): practice pausing instead of saying 'um', 'uh', 'like'")
            elif filler_count >= 2:
                suggestions.append("Minimize filler words for more professional speech")

        # Grammar-specific suggestions only
        if grammar_score < 70:
            suggestions.append("Focus on clear sentence structure while speaking")
            suggestions.append("Practice expressing ideas in complete thoughts")

        # Error category-based suggestions for speech - GRAMMAR ONLY
        error_categories = [error.get('category', '') for error in errors]
        high_severity_errors = [error for error in errors if error.get('severity') == 'high']

        if 'GRAMMAR' in error_categories or high_severity_errors:
            suggestions.append("Pay attention to verb tenses and subject-verb agreement")

        if len(errors) > 5:  # Many errors
            suggestions.append("Practice speaking more slowly for clearer articulation")

        return suggestions[:4]  # Limit suggestions

    def _generate_local_assessment(self, grammar_score: float, error_count: int, filler_count: int = 0) -> str:
        """Generate overall assessment based on local analysis - GRAMMAR ONLY with filler assessment"""
        filler_note = ""
        if filler_count > 0:
            filler_note = f" (includes {filler_count} filler words)"
        
        if grammar_score >= 85:
            return f"Excellent grammar! Score: {grammar_score}/100{filler_note}"
        elif grammar_score >= 70:
            return f"Good grammar with minor issues. Score: {grammar_score}/100{filler_note}"
        elif grammar_score >= 50:
            return f"Adequate grammar with room for improvement. Score: {grammar_score}/100{filler_note}"
        else:
            return f"Grammar needs significant improvement. Focus on sentence structure and reducing filler words. Score: {grammar_score}/100{filler_note}"

    def _empty_result(self) -> Dict:
        """Return empty result for no text"""
        return {
            'grammar_score': 0,
            'error_count': 0,
            'filler_count': 0,
            'filler_rate': 0,
            'word_count': 0,
            'original_word_count': 0,
            'overall_assessment': "No text provided for analysis",
            'analysis_type': 'empty',
            'ai_used': False
        }

    def _minimal_result(self, text: str, word_count: int, filler_count: int = 0) -> Dict:
        """Return minimal result for very short text"""
        return {
            'grammar_score': 85,  # Assume good for very short responses
            'error_count': 0,
            'filler_count': filler_count,
            'filler_rate': 0,
            'word_count': word_count,
            'original_word_count': word_count,
            'original_text': text,
            'overall_assessment': f"Response too short ({word_count} words) for detailed analysis",
            'analysis_type': 'minimal',
            'ai_used': False
        }

    def get_analysis_summary(self) -> Dict:
        """Get summary of checker capabilities"""
        return {
            'local_available': self.local_available,
            'ai_available': self.ai_available,
            'hybrid_mode': self.local_available and self.ai_available,
            'recommended_min_words': getattr(Config, 'GRAMMAR_AI_THRESHOLD', 30),
            'ai_provider': 'Azure OpenAI' if self.ai_available else 'None'
        }