
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
import os
import json
from datetime import datetime
import tempfile

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.HexColor('#A23B72'),
            alignment=TA_LEFT
        ))
        
        # Score style (used for smaller score lines)
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=16,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#F18F01')
        ))
        
        # Large score style (used as a base for big boxed scores)
        self.styles.add(ParagraphStyle(
            name='LargeScore',
            parent=self.styles['Normal'],
            fontSize=28,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#C73E1D')
        ))
    
    def get_score_color(self, score):
        """Get color based on score range"""
        if score >= 80:
            return colors.HexColor('#2E8B57')  # Green
        elif score >= 60:
            return colors.HexColor('#FF8C00')  # Orange
        else:
            return colors.HexColor('#DC143C')  # Red
    
    def create_emotion_chart(self, emotion_data, temp_dir, question_num=None):
        """Create emotion distribution chart and save as PNG"""
        try:
            if not emotion_data or 'emotion_distribution' not in emotion_data:
                return None
            
            distribution = emotion_data['emotion_distribution']
            if not distribution:
                return None
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            emotions = list(distribution.keys())
            counts = list(distribution.values())
            
            # Create bar plot
            bars = plt.bar(emotions, counts, color='skyblue', edgecolor='navy', alpha=0.7)
            
            # Customize plot
            title = 'Emotion Distribution Throughout Interview'
            if question_num:
                title += f' - Question {question_num}'
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel('Emotions', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.xticks(rotation=45)
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(count), ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Save to temporary file
            chart_name = f'emotion_chart_q{question_num}.png' if question_num else 'emotion_chart.png'
            chart_path = os.path.join(temp_dir, chart_name)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"Error creating emotion chart: {e}")
            return None
    
    def generate_report(self, analysis_results, question, question_type, candidate_id=None, output_dir="reports"):
        """
        Generate comprehensive PDF report
        
        Args:
            analysis_results: Dictionary containing all analysis results
            question: Interview question text
            question_type: Type of question (Technical/HR)
            candidate_id: Candidate identifier
            output_dir: Directory to save the PDF
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        question_idx = analysis_results.get('question_index', 1)
        candidate_name = candidate_id or "CANDIDATE"
        filename = f"{candidate_name}_{timestamp}_Q{question_idx}_report.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create temporary directory for images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=1*inch)
            story = []
            
            # Page 1: Cover
            story.extend(self.create_cover_page(question, question_type, timestamp, question_idx, candidate_name))
            story.append(PageBreak())
            
            # Page 2: Emotion Section
            story.extend(self.create_emotion_page(analysis_results.get('emotion_analysis', {}), temp_dir))
            story.append(PageBreak())
            
            # Page 3: Grammar Section
            story.extend(self.create_grammar_page(analysis_results.get('grammar_analysis', {})))
            story.append(PageBreak())
            
            # Page 4: Answer Evaluation
            story.extend(self.create_evaluation_page(analysis_results.get('answer_evaluation', {})))
            story.append(PageBreak())
            
            # Page 5: Aggregate Section
            story.extend(self.create_aggregate_page(analysis_results))
            
            # Build PDF
            doc.build(story)
        
        return filepath
    
    def generate_complete_interview_report(self, interview_summary, candidate_id=None, output_dir="reports"):
        """
        Generate a comprehensive PDF report for all interview questions
        
        Args:
            interview_summary: Dictionary containing all interview data and statistics
            candidate_id: Candidate identifier
            output_dir: Directory to save the PDF
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        candidate_name = candidate_id or "CANDIDATE"
        filename = f"{candidate_name}_Complete_Interview_Report_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create temporary directory for images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=1*inch)
            story = []
            
            # Page 1: Executive Summary Cover
            story.extend(self.create_interview_summary_cover(interview_summary, candidate_name, timestamp))
            story.append(PageBreak())
            
            # Page 2: Overall Performance Dashboard
            story.extend(self.create_overall_performance_page(interview_summary))
            story.append(PageBreak())
            
            # Individual Question Pages
            for question_data in interview_summary.get('questions_data', []):
                # Each question gets its own set of pages
                story.extend(self.create_question_cover_page(question_data))
                story.append(PageBreak())
                
                # Emotion page for this question
                story.extend(self.create_emotion_page(
                    question_data['analysis'].get('emotion_analysis', {}), 
                    temp_dir,
                    question_num=question_data['question_number']
                ))
                story.append(PageBreak())
                
                # Grammar page for this question
                story.extend(self.create_grammar_page(question_data['analysis'].get('grammar_analysis', {})))
                story.append(PageBreak())
                
                # Answer evaluation page for this question
                story.extend(self.create_evaluation_page(question_data['analysis'].get('answer_evaluation', {})))
                story.append(PageBreak())
                
                # Aggregate page for this question
                story.extend(self.create_aggregate_page(question_data['analysis']))
                story.append(PageBreak())
            
            # Final Summary and Recommendations
            story.extend(self.create_final_recommendations_page(interview_summary))
            
            # Build PDF
            doc.build(story)
        
        return filepath

    def create_interview_summary_cover(self, interview_summary, candidate_name, timestamp):
        """Create executive summary cover page"""
        story = []
        
        # Main title
        title_text = f"Complete Interview Assessment Report"
        story.append(Paragraph(title_text, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Candidate info
        candidate_text = f"<b>Candidate:</b> {candidate_name}"
        story.append(Paragraph(candidate_text, self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Date/Time stamp
        date_text = f"<b>Assessment Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Interview statistics
        stats_data = [
            ['Metric', 'Value'],
            ['Total Questions', str(interview_summary.get('total_questions', 0))],
            ['Completed Questions', str(interview_summary.get('completed_questions', 0))],
            ['Completion Rate', f"{interview_summary.get('completion_rate', 0):.1f}%"],
        ]
        
        # Add overall score if available
        if interview_summary.get('overall_aggregate'):
            overall_score = interview_summary['overall_aggregate']['aggregate_score']
            stats_data.append(['Overall Score', f"{overall_score}/100"])
        
        stats_table = Table(stats_data, colWidths=[2.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(Paragraph("<b>Interview Summary:</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(stats_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Assessment overview
        story.append(Paragraph("<b>Assessment Overview:</b>", self.styles['Heading2']))
        overview_text = """
        This comprehensive report provides a detailed analysis of the candidate's interview performance across multiple dimensions:
        
        • <b>Emotional Intelligence:</b> Analysis of confidence levels and emotional control during responses<br/>
        • <b>Communication Skills:</b> Grammar, language quality, and verbal clarity assessment<br/>
        • <b>Content Quality:</b> Technical accuracy, completeness, and relevance of answers<br/>
        • <b>Overall Performance:</b> Weighted aggregate scoring across all evaluation criteria<br/>
        
        Each question has been individually analyzed and scored, with detailed breakdowns and improvement recommendations provided.
        """
        story.append(Paragraph(overview_text, self.styles['Normal']))
        
        return story

    def create_overall_performance_page(self, interview_summary):
        """Create overall performance dashboard page"""
        story = []
        
        # Page header
        story.append(Paragraph("Overall Performance Dashboard", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Overall aggregate score (if available)
        if interview_summary.get('overall_aggregate'):
            overall_agg = interview_summary['overall_aggregate']
            aggregate_score = overall_agg['aggregate_score']
            score_color = self.get_score_color(aggregate_score)            # --- Big boxed score style - Fixed to prevent text overlap ---
            score_color = self.get_score_color(aggregate_score)
            
            # Create separate paragraphs for label and score to prevent overlap
            overall_label_style = ParagraphStyle(
                name='OverallScoreLabel',
                parent=self.styles['Heading2'],
                fontSize=20,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceBefore=12,
                spaceAfter=12
            )
            
            overall_score_style = ParagraphStyle(
                name='OverallScoreValue',
                parent=self.styles['LargeScore'],
                fontSize=28,  # Reduced font size to fit properly in box
                textColor=score_color,
                borderWidth=6,
                borderColor=score_color,
                borderPadding=25,  # Increased padding for better containment
                backColor=colors.HexColor('#F0F0F0'),
                alignment=TA_CENTER,
                spaceBefore=12,
                spaceAfter=18,
                leftIndent=0,
                rightIndent=0
            )
            
            # Add the label and score as separate elements with proper spacing
            story.append(Paragraph("Overall Interview Score:", overall_label_style))
            story.append(Spacer(1, 0.1*inch))  # Add spacer between label and score
            story.append(Paragraph(f"{aggregate_score:.1f}/100", overall_score_style))
            story.append(Spacer(1, 0.4*inch))
            
            # Subtitle before the table
            story.append(Paragraph(
                "<b>Component Performance Breakdown:</b>",
                ParagraphStyle(
                    name='SubHeader',
                    parent=self.styles['Heading2'],
                    fontSize=14,
                    textColor=colors.black,
                    spaceAfter=6
                )
            ))
            story.append(Spacer(1, 0.1*inch))
            
            # Build the breakdown table
            breakdown = overall_agg.get('breakdown', {})
            weights = overall_agg.get('weights_used', {})
            
            component_details = {
                'emotion': {'name': 'Emotional Intelligence', 'icon': '🎭'},
                'grammar': {'name': 'Communication Skills', 'icon': '📝'},
                'answer': {'name': 'Content Quality', 'icon': '🤖'}
            }
            
            breakdown_data = [['Component', 'Score', 'Weight (%)', 'Weighted Contribution']]
            for component, score in breakdown.items():
                details = component_details.get(component, {'name': component.title(), 'icon': '📊'})
                weight = weights.get(component, 0)
                weighted_score = score * weight / 100
                breakdown_data.append([
                    f"{details['icon']} {details['name']}",
                    f"{score:.1f}/100",
                    f"{weight:.1f}%",
                    f"{weighted_score:.1f}"
                ])
            
            breakdown_table = Table(breakdown_data, colWidths=[2.2*inch, 1.2*inch, 1*inch, 1.1*inch])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),  # header purple
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0F0F0')),  # body light gray
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(breakdown_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Question-by-question summary
        story.append(Paragraph("<b>Question-by-Question Summary:</b>", self.styles['Heading2']))
        
        questions_data = interview_summary.get('questions_data', [])
        if questions_data:
            summary_data = [['Question', 'Type', 'Score', 'Performance Level']]
            
            for q_data in questions_data:
                q_num = q_data['question_number']
                q_type = q_data['question_type']
                
                # Get aggregate score for this question
                analysis = q_data['analysis']
                if analysis.get('aggregate_evaluation'):
                    q_score = analysis['aggregate_evaluation']['aggregate_score']
                    
                    # Determine performance level
                    if q_score >= 85:
                        level = "🌟 Excellent"
                    elif q_score >= 75:
                        level = "⭐ Very Good"
                    elif q_score >= 65:
                        level = "👍 Good"
                    elif q_score >= 50:
                        level = "📈 Fair"
                    else:
                        level = "❌ Needs Work"
                    
                    summary_data.append([
                        f"Q{q_num}",
                        q_type,
                        f"{q_score:.1f}/100",
                        level
                    ])
            
            summary_table = Table(summary_data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 2.3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F8FF')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(summary_table)
        
        return story

    def create_question_cover_page(self, question_data):
        """Create a cover page for individual question"""
        story = []
        
        q_num = question_data['question_number']
        q_type = question_data['question_type']
        question = question_data['question']
        
        # Question header
        title_text = f"Question {q_num} Analysis"
        story.append(Paragraph(title_text, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Question type
        type_text = f"<b>Question Type:</b> {q_type}"
        story.append(Paragraph(type_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Question text
        question_style = ParagraphStyle(
            name='QuestionDetailStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=20,
            leftIndent=20,
            rightIndent=20,
            borderWidth=2,
            borderColor=colors.HexColor('#2E86AB'),
            borderPadding=15,
            backColor=colors.HexColor('#F0F8FF')
        )
        
        question_text = f"<b>Question:</b><br/><br/>{question}"
        story.append(Paragraph(question_text, question_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Quick summary if aggregate available
        analysis = question_data['analysis']
        if analysis.get('aggregate_evaluation'):
            agg_score = analysis['aggregate_evaluation']['aggregate_score']
            score_color = self.get_score_color(agg_score)
            
            summary_style = ParagraphStyle(
                name='QuickSummaryStyle',
                parent=self.styles['Normal'],
                fontSize=16,
                textColor=score_color,
                alignment=TA_CENTER,
                borderWidth=1,
                borderColor=score_color,
                borderPadding=10,
                backColor=colors.HexColor('#FAFAFA')
            )
            
            summary_text = f"<b>Overall Score for this Question: {agg_score}/100</b>"
            story.append(Paragraph(summary_text, summary_style))
        
        return story

    def create_final_recommendations_page(self, interview_summary):
        """Create final recommendations and summary page"""
        story = []
        
        # Page header
        story.append(Paragraph("Final Assessment & Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Overall assessment
        if interview_summary.get('overall_aggregate'):
            overall_score = interview_summary['overall_aggregate']['aggregate_score']
            
            # Performance assessment
            if overall_score >= 85:
                assessment = "Outstanding candidate with excellent performance across all areas."
                recommendation = "Highly recommended for the position. Consider for senior or leadership roles."
                emoji = "🌟"
            elif overall_score >= 75:
                assessment = "Strong candidate with very good performance in most areas."
                recommendation = "Recommended for the position with confidence."
                emoji = "⭐"
            elif overall_score >= 65:
                assessment = "Good candidate with solid performance and some areas for development."
                recommendation = "Suitable for the position with appropriate training and support."
                emoji = "👍"
            elif overall_score >= 50:
                assessment = "Fair candidate with adequate basic skills but significant development needs."
                recommendation = "Consider for junior positions with extensive training and mentorship."
                emoji = "📈"
            else:
                assessment = "Candidate requires substantial development before being ready for this role."
                recommendation = "Not recommended for current position. Suggest additional training and re-evaluation."
                emoji = "❌"
            
            story.append(Paragraph(f"<b>{emoji} Overall Assessment:</b>", self.styles['Heading2']))
            story.append(Paragraph(assessment, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("<b>💼 Hiring Recommendation:</b>", self.styles['Heading2']))
            story.append(Paragraph(recommendation, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Detailed analysis by component
        if interview_summary.get('overall_aggregate'):
            breakdown = interview_summary['overall_aggregate'].get('breakdown', {})
            
            story.append(Paragraph("<b>📊 Detailed Component Analysis:</b>", self.styles['Heading2']))
            
            component_analysis = {
                'emotion': {
                    'name': 'Emotional Intelligence',
                    'high': 'Excellent emotional control and confidence throughout the interview.',
                    'medium': 'Good emotional stability with minor areas for confidence building.',
                    'low': 'Needs development in emotional regulation and confidence building.'
                },
                'grammar': {
                    'name': 'Communication Skills', 
                    'high': 'Excellent grammar and communication clarity.',
                    'medium': 'Good communication with minor grammar improvements needed.',
                    'low': 'Requires significant improvement in grammar and communication skills.'
                },
                'answer': {
                    'name': 'Content Quality',
                    'high': 'Excellent technical knowledge and comprehensive answers.',
                    'medium': 'Good content quality with some areas for deeper knowledge.',
                    'low': 'Needs significant improvement in technical knowledge and answer quality.'
                }
            }
            
            for component, score in breakdown.items():
                if component in component_analysis:
                    analysis = component_analysis[component]
                    
                    story.append(Paragraph(f"<b>• {analysis['name']} ({score:.1f}/100):</b>", self.styles['Normal']))
                    
                    if score >= 80:
                        feedback = analysis['high']
                    elif score >= 60:
                        feedback = analysis['medium']
                    else:
                        feedback = analysis['low']
                    
                    story.append(Paragraph(feedback, self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
        
        # Final note
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("<b>📋 Report Generated:</b>", self.styles['Heading2']))
        final_note = f"This comprehensive assessment was generated on {datetime.now().strftime('%B %d, %Y')} using AI-powered analysis tools for emotion recognition, grammar evaluation, and content assessment."
        story.append(Paragraph(final_note, self.styles['Normal']))
        
        return story
    
    def create_cover_page(self, question, question_type, timestamp, question_idx, candidate_name):
        """Create cover page content"""
        story = []
        
        # Title
        title_text = f"{candidate_name} - Question {question_idx}"
        story.append(Paragraph(title_text, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Date/Time stamp
        date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Question type
        type_text = f"<b>Question Type:</b> {question_type}"
        story.append(Paragraph(type_text, self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Question text in stylized header
        question_style = ParagraphStyle(
            name='QuestionStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=20,
            leftIndent=20,
            rightIndent=20,
            borderWidth=2,
            borderColor=colors.HexColor('#2E86AB'),
            borderPadding=15,
            backColor=colors.HexColor('#F0F8FF')
        )
        
        question_text = f"<b>Question:</b><br/><br/>{question}"
        story.append(Paragraph(question_text, question_style))
        
        return story
    
    def create_emotion_page(self, emotion_data, temp_dir, question_num=None):
        """Create emotion analysis page"""
        story = []
        
        # Section header
        story.append(Paragraph("Emotion Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        if emotion_data:
            # Create and embed emotion chart
            chart_path = self.create_emotion_chart(emotion_data, temp_dir, question_num)
            if chart_path and os.path.exists(chart_path):
                # Add chart
                img = Image(chart_path, width=6*inch, height=3.6*inch)
                story.append(img)
                story.append(Spacer(1, 0.3*inch))
            
            # Dominant emotion
            dominant_emotion = emotion_data.get('dominant_emotion', 'Unknown')
            dominant_text = f"<b>Dominant Emotion:</b> {dominant_emotion.title()}"
            story.append(Paragraph(dominant_text, self.styles['ScoreStyle']))
            
            # Average confidence
            avg_confidence = emotion_data.get('avg_confidence', 0)
            confidence_text = f"<b>Average Confidence:</b> {avg_confidence:.3f}"
            story.append(Paragraph(confidence_text, self.styles['ScoreStyle']))
            
            # Additional metrics
            if 'total_segments' in emotion_data:
                segments_text = f"<b>Total Segments Analyzed:</b> {emotion_data['total_segments']}"
                story.append(Paragraph(segments_text, self.styles['Normal']))
            
        else:
            story.append(Paragraph("No emotion analysis data available.", self.styles['Normal']))
        
        return story
    
    def create_grammar_page(self, grammar_data):
        """Create grammar analysis page"""
        story = []
        
        # Section header
        story.append(Paragraph("Grammar Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        if grammar_data:
            # Grammar score with color coding
            grammar_score = grammar_data.get('grammar_score', 0)
            score_color = self.get_score_color(grammar_score)
            
            score_style = ParagraphStyle(
                name='GrammarScoreStyle',
                parent=self.styles['LargeScore'],
                textColor=score_color
            )
            
            score_text = f"Grammar Score: {grammar_score}/100"
            story.append(Paragraph(score_text, score_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Key strengths
            if 'key_strengths' in grammar_data and grammar_data['key_strengths']:
                story.append(Paragraph("<b>Key Strengths:</b>", self.styles['Heading2']))
                for strength in grammar_data['key_strengths']:
                    story.append(Paragraph(f"• {strength}", self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Key issues
            if 'key_issues' in grammar_data and grammar_data['key_issues']:
                story.append(Paragraph("<b>Key Issues:</b>", self.styles['Heading2']))
                for issue in grammar_data['key_issues']:
                    story.append(Paragraph(f"• {issue}", self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Specific suggestions
            if 'specific_suggestions' in grammar_data and grammar_data['specific_suggestions']:
                story.append(Paragraph("<b>Improvement Suggestions:</b>", self.styles['Heading2']))
                for suggestion in grammar_data['specific_suggestions']:
                    story.append(Paragraph(f"• {suggestion}", self.styles['Normal']))
            
        else:
            story.append(Paragraph("No grammar analysis data available.", self.styles['Normal']))
        
        return story
    
    def create_evaluation_page(self, evaluation_data):
        """Create answer evaluation page"""
        story = []
        
        # Section header
        story.append(Paragraph("Answer Evaluation", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        if evaluation_data:
            # Historic score (if applicable)
            if 'old_score' in evaluation_data and evaluation_data['old_score'] is not None:
                historic_text = f"<b>Historic Score:</b> {evaluation_data['old_score']}/100"
                story.append(Paragraph(historic_text, self.styles['ScoreStyle']))
                story.append(Spacer(1, 0.1*inch))
            
            # Rubric breakdown
            rubric_breakdown = evaluation_data.get('rubric_breakdown', {})
            if rubric_breakdown:
                rubric_score = rubric_breakdown.get('overall_score', 0)
                
                # --- Styled Rubric Score ---
                rubric_score_style = ParagraphStyle(
                    name='RubricScoreStyle',
                    parent=self.styles['Normal'],
                    fontSize=20,
                    textColor=colors.HexColor('#F18F01'),  # same orange
                    alignment=TA_CENTER,
                    spaceBefore=6,
                    spaceAfter=12
                )
                story.append(Paragraph(f"Rubric Score: {rubric_score:.2f}/100", rubric_score_style))
                story.append(Spacer(1, 0.15*inch))
                
                # Detailed Rubric Breakdown subtitle
                story.append(Paragraph(
                    "<b>Detailed Rubric Breakdown:</b>",
                    ParagraphStyle(
                        name='RubricTableHeader',
                        parent=self.styles['Heading2'],
                        fontSize=14,
                        textColor=colors.black,
                        spaceAfter=6
                    )                ))
                story.append(Spacer(1, 0.1*inch))
                  # Build the rubric table
                scores = rubric_breakdown.get('scores', [])
                if scores:
                    table_data = [['Criterion', 'Score', 'Explanation']]
                    for item in scores:
                        name = item.get('name', '')
                        sc = item.get('score', 0)
                        exp = item.get('explanation', '')
                        
                        # Create a Paragraph for the criterion name to enable text wrapping
                        criterion_style = ParagraphStyle(
                            name='CriterionCell',
                            parent=self.styles['Normal'],
                            fontSize=10,
                            leading=12,
                            leftIndent=4,
                            rightIndent=4,
                            spaceBefore=2,
                            spaceAfter=2,
                            wordWrap='CJK'
                        )
                        criterion_para = Paragraph(name, criterion_style)
                        
                        # Create a Paragraph for the explanation to enable text wrapping
                        explanation_style = ParagraphStyle(
                            name='ExplanationCell',
                            parent=self.styles['Normal'],
                            fontSize=10,
                            leading=12,
                            leftIndent=4,
                            rightIndent=4,
                            spaceBefore=2,
                            spaceAfter=2,
                            wordWrap='CJK'
                        )
                        explanation_para = Paragraph(exp, explanation_style)
                        
                        table_data.append([criterion_para, f"{sc}/100", explanation_para])
                    
                    # Adjusted table width and column widths - wider criterion column
                    table = Table(table_data, colWidths=[2.0*inch, 0.8*inch, 3.7*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),  # deep blue header
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),  # Smaller font for content rows
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),  # body white
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F8F8')]),  # Alternating row colors
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),  # Increased top padding
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),  # Increased bottom padding
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 0.4*inch))            # Final Combined Score - Fixed to prevent text overlap with proper spacing
            final_score = evaluation_data.get('final_combined_score', evaluation_data.get('answer_score', 0))
            final_color = self.get_score_color(final_score)
            
            # Add page break to ensure label and score stay together on same page
            story.append(PageBreak())
            
            # Add extra spacing after the page break
            story.append(Spacer(1, 0.5*inch))
            
            # Create separate paragraphs for label and score to prevent overlap
            final_label_style = ParagraphStyle(
                name='FinalScoreLabel',
                parent=self.styles['Heading2'],
                fontSize=18,
                textColor=colors.black,                alignment=TA_CENTER,
                spaceBefore=12,
                spaceAfter=12
            )
            
            final_score_style = ParagraphStyle(
                name='FinalScoreValue',
                parent=self.styles['LargeScore'],
                fontSize=28,  # Reduced from 32 to ensure it fits in the box
                textColor=final_color,
                alignment=TA_CENTER,
                spaceBefore=12,
                spaceAfter=18,
                borderWidth=3,
                borderColor=final_color,
                borderPadding=25,  # Increased padding for better box containment
                backColor=colors.HexColor('#F8F8FF'),
                leftIndent=0,
                rightIndent=0
            )
            
            # Add the label and score as separate elements with proper spacing
            story.append(Paragraph("Final Combined Score:", final_label_style))
            story.append(Spacer(1, 0.1*inch))  # Add spacer between label and score
            story.append(Paragraph(f"{final_score:.2f}/100", final_score_style))
        
        else:
            story.append(Paragraph("No evaluation data available.", self.styles['Normal']))
        
        return story
    
    def create_aggregate_page(self, analysis_results):
        """Create aggregate results page"""
        story = []
        
        # Section header
        story.append(Paragraph("Overall Performance Summary", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Overall aggregate score
        aggregate_score = analysis_results.get('combined_score', 0)
        if aggregate_score == 0 and analysis_results.get('aggregate_evaluation'):
            aggregate_score = analysis_results['aggregate_evaluation'].get('aggregate_score', 0)
        if aggregate_score == 0:
            # Calculate if not available
            aggregate_score = self.calculate_aggregate_score(analysis_results)          # Large colorized score box - Fixed to prevent text overlap with proper spacing
        score_color = self.get_score_color(aggregate_score)
        
        # Add extra spacing before the aggregate score section
        story.append(Spacer(1, 0.3*inch))
        
        # Create separate paragraphs for label and score to prevent overlap
        aggregate_label_style = ParagraphStyle(
            name='AggregateLabelStyle',
            parent=self.styles['Heading2'],
            fontSize=20,
            textColor=colors.black,
            alignment=TA_CENTER,            spaceBefore=12,
            spaceAfter=12
        )
        
        aggregate_score_style = ParagraphStyle(
            name='AggregateScoreStyle',
            parent=self.styles['LargeScore'],
            fontSize=30,  # Reduced from 34 to ensure it fits in the box
            textColor=score_color,
            borderWidth=3,
            borderColor=score_color,
            borderPadding=25,  # Increased padding for better box containment
            backColor=colors.HexColor('#F8F8FF'),
            alignment=TA_CENTER,
            spaceBefore=12,
            spaceAfter=24,
            leftIndent=0,
            rightIndent=0
        )
        
        # Add the label and score as separate elements with proper spacing
        story.append(Paragraph("Overall Aggregate Score:", aggregate_label_style))
        story.append(Spacer(1, 0.15*inch))  # Add spacer between label and score
        story.append(Paragraph(f"{aggregate_score:.1f}/100", aggregate_score_style))
        story.append(Spacer(1, 0.4*inch))
        
        # Component breakdown table
        story.append(Paragraph("<b>Component Breakdown:</b>", self.styles['Heading2']))
        
        # Calculate component scores and weights
        emotion_score = 0
        grammar_score = 0
        answer_score = 0
        
        if analysis_results.get('emotion_analysis'):
            # Convert emotion confidence to score (placeholder logic)
            emotion_score = analysis_results['emotion_analysis'].get('avg_confidence', 0) * 100
        
        if analysis_results.get('grammar_analysis'):
            grammar_score = analysis_results['grammar_analysis'].get('grammar_score', 0)
        
        if analysis_results.get('answer_evaluation'):
            answer_score = analysis_results['answer_evaluation'].get('final_combined_score', 
                          analysis_results['answer_evaluation'].get('answer_score', 0))
        
        # Component weights
        emotion_weight = 20
        grammar_weight = 25
        answer_weight = 55
        
        breakdown_data = [
            ['Component', 'Score', 'Weight (%)', 'Weighted Score'],
            ['Emotion Analysis', f"{emotion_score:.1f}/100", f"{emotion_weight}%", f"{emotion_score * emotion_weight / 100:.1f}"],
            ['Grammar Analysis', f"{grammar_score:.1f}/100", f"{grammar_weight}%", f"{grammar_score * grammar_weight / 100:.1f}"],
            ['Answer Evaluation', f"{answer_score:.1f}/100", f"{answer_weight}%", f"{answer_score * answer_weight / 100:.1f}"]
        ]
        
        breakdown_table = Table(breakdown_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.3*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0F0F0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(breakdown_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Performance summary and recommendations
        story.append(Paragraph("<b>Performance Summary:</b>", self.styles['Heading2']))
        
        performance_level, recommendations = self.generate_performance_summary(aggregate_score, analysis_results)
        
        summary_text = f"Based on the comprehensive analysis, the candidate demonstrates {performance_level} performance. {recommendations}"
        story.append(Paragraph(summary_text, self.styles['Normal']))
        
        return story
    
    def calculate_aggregate_score(self, analysis_results):
        """Calculate aggregate score from components"""
        emotion_score = 0
        grammar_score = 0
        answer_score = 0
        
        if analysis_results.get('emotion_analysis'):
            emotion_score = analysis_results['emotion_analysis'].get('avg_confidence', 0) * 100
        
        if analysis_results.get('grammar_analysis'):
            grammar_score = analysis_results['grammar_analysis'].get('grammar_score', 0)
        
        if analysis_results.get('answer_evaluation'):
            answer_score = analysis_results['answer_evaluation'].get('final_combined_score', 
                          analysis_results['answer_evaluation'].get('answer_score', 0))
        
        # Weights
        emotion_weight = 0.20
        grammar_weight = 0.25
        answer_weight = 0.55
        
        aggregate = (emotion_score * emotion_weight + 
                    grammar_score * grammar_weight + 
                    answer_score * answer_weight)
        
        return aggregate
    
    def generate_performance_summary(self, score, analysis_results):
        """Generate performance level and recommendations"""
        if score >= 85:
            level = "excellent"
            recommendations = "The candidate shows strong competency across all evaluated areas. Consider for advanced positions or leadership roles."
        elif score >= 70:
            level = "good"
            recommendations = "The candidate shows solid performance with room for improvement in specific areas. Suitable for most positions with appropriate training."
        elif score >= 55:
            level = "satisfactory"
            recommendations = "The candidate meets basic requirements but would benefit from additional training and development before taking on complex responsibilities."
        else:
            level = "needs improvement"
            recommendations = "The candidate requires significant development in multiple areas before being ready for this type of role."
        
        return level, recommendations

# Test function
def test_pdf_generator():
    """Test the PDF generator with sample data"""
    
    # Sample data
    sample_results = {
        'emotion_analysis': {
            'dominant_emotion': 'confident',
            'avg_confidence': 0.78,
            'total_segments': 25,
            'emotion_distribution': {
                'confident': 12,
                'happy': 8,
                'neutral': 5
            }
        },
        'grammar_analysis': {
            'grammar_score': 82,
            'key_strengths': ['Clear sentence structure', 'Good vocabulary usage'],
            'key_issues': ['Minor punctuation errors'],
            'specific_suggestions': ['Use active voice more frequently', 'Vary sentence length']
        },
        'answer_evaluation': {
            'final_combined_score': 78,
            'old_score': 75,
            'rubric_breakdown': {
                'overall_score': 80,
                'scores': [
                    {'name': 'Clarity', 'score': 85, 'explanation': 'Response was clear and well-structured'},
                    {'name': 'Technical Accuracy', 'score': 75, 'explanation': 'Good technical knowledge with minor gaps'},
                    {'name': 'Completeness', 'score': 80, 'explanation': 'Covered most aspects of the question'}
                ]
            }
        },
        'combined_score': 79.5,
        'question_index': 1
    }
    
    question = "Explain the differences between supervised and unsupervised machine learning, and provide examples of each."
    question_type = "Technical"
    
    generator = PDFReportGenerator()
    pdf_path = generator.generate_report(sample_results, question, question_type, "TEST_CANDIDATE")
    
    print(f"Test PDF generated: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    test_pdf_generator()
