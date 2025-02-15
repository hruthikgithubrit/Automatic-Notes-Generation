from youtube_transcript_api import YouTubeTranscriptApi
import os
from reportlab.pdfgen import canvas
from .text_processing import textrank_summarize
from .firebase_config import bucket, db

def process_youtube_video(youtube_url):
    try:
        # Extract video ID
        video_id = youtube_url.split('v=')[1].split('&')[0]
        
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine transcript text
        full_text = ' '.join([entry['text'] for entry in transcript])
        
        # Create downloads directory if not exists
        os.makedirs('downloads', exist_ok=True)
        
        # Save transcript
        transcript_filename = f'downloads/{video_id}_transcript.txt'
        with open(transcript_filename, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Generate summary
        summary = textrank_summarize(full_text)

        # Replace existing PDF generation code
        pdf_filename = f'downloads/{video_id}_summary.pdf'
        c = canvas.Canvas(pdf_filename)
        c.drawString(100, 750, "Video Summary")
        text_object = c.beginText(100, 700)

        # Use the new wrapping function
        wrapped_lines = wrap_text_to_10_words(summary)
        for line in wrapped_lines:
            text_object.textLine(line)

        c.drawText(text_object)
        c.showPage()
        c.save()
        
        # Upload to Firebase
        transcript_blob = bucket.blob(f'transcripts/{video_id}_transcript.txt')
        transcript_blob.upload_from_filename(transcript_filename)
        
        summary_blob = bucket.blob(f'summaries/{video_id}_summary.pdf')
        summary_blob.upload_from_filename(pdf_filename)
        
        return pdf_filename
    
    except Exception as e:
        print(f"Error processing YouTube video: {e}")
        return None
    

def wrap_text_to_10_words(summary):
    words = summary.split()
    wrapped_lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        
        # If line reaches 10 words or a period, create a new line
        if len(current_line) == 10 or word.endswith('.'):
            wrapped_lines.append(' '.join(current_line))
            current_line = []
    
    # Add remaining words if any
    if current_line:
        wrapped_lines.append(' '.join(current_line))
    
    return wrapped_lines

