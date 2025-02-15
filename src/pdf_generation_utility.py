import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.colors import darkblue, black

class PDFGenerator:
    def __init__(self, output_path):
        """
        Initialize PDF Generator with output path and configuration
        
        Args:
            output_path (str): File path where PDF will be saved
        """
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._configure_custom_styles()
    
    def _configure_custom_styles(self):
        """Configure custom paragraph styles for PDF"""
        # Custom Title Style
        self.styles.add(ParagraphStyle(
            name='CenteredTitle',
            parent=self.styles['Title'],
            alignment=TA_CENTER,
            textColor=darkblue,
            fontSize=16,
            spaceAfter=12
        ))
        
        # Custom Body Style
        self.styles.add(ParagraphStyle(
            name='JustifiedNormal',
            parent=self.styles['Normal'],
            alignment=TA_JUSTIFY,
            textColor=black,
            fontSize=10,
            leading=14,
            spaceAfter=6
        ))
    
    def _wrap_text(self, text, words_per_line=10):
        """
        Wrap text to ensure approximately specified words per line
        
        Args:
            text (str): Input text to be wrapped
            words_per_line (int): Number of words per line
        
        Returns:
            list: List of wrapped text lines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            
            if len(current_line) >= words_per_line:
                lines.append(' '.join(current_line))
                current_line = []
        
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def generate_summary_pdf(self, summary, title="Video Summary"):
        """
        Generate a PDF with summary text
        
        Args:
            summary (str): The summary text to be converted to PDF
            title (str, optional): PDF document title
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            self.output_path, 
            pagesize=letter,
            rightMargin=72, 
            leftMargin=72,
            topMargin=72, 
            bottomMargin=18
        )
        
        # Prepare story/content
        story = []
        
        # Add title
        story.append(Paragraph(title, self.styles['CenteredTitle']))
        story.append(Spacer(1, 12))
        
        # Wrap and add summary paragraphs
        wrapped_lines = self._wrap_text(summary)
        
        for line in wrapped_lines:
            story.append(Paragraph(line, self.styles['JustifiedNormal']))
        
        # Build PDF
        doc.build(story)
        
        return self.output_path

def create_pdf(summary, output_path, title="Video Summary"):
    """
    Convenience function to create PDF
    
    Args:
        summary (str): Summary text
        output_path (str): Output file path
        title (str, optional): PDF document title
    
    Returns:
        str: Path to generated PDF
    """
    pdf_generator = PDFGenerator(output_path)
    return pdf_generator.generate_summary_pdf(summary, title)