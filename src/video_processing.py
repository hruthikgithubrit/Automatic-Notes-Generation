import cv2
import pytesseract
from pydub import AudioSegment
import speech_recognition as sr
import os
from .text_processing import textrank_summarize
from .firebase_config import bucket
from reportlab.pdfgen import canvas  

def process_local_video(video_path):
    # Create directories
    os.makedirs('downloads/frames', exist_ok=True)
    os.makedirs('downloads/audio', exist_ok=True)
    
    # Video and Audio Processing
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * 60)  # Extract frame every minute
    
    # OCR and Frame Extraction
    ocr_texts = []
    frame_count = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            # Save frame
            frame_path = f'downloads/frames/frame_{frame_count}.jpg'
            cv2.imwrite(frame_path, frame)
            
            # Perform OCR
            ocr_text = pytesseract.image_to_string(frame)
            ocr_texts.append(ocr_text)
            
            # Upload frame to Firebase
            frame_blob = bucket.blob(f'frames/frame_{frame_count}.jpg')
            frame_blob.upload_from_filename(frame_path)
        
        frame_count += 1
    
    video.release()
    
    # Audio to Text Conversion
    audio_path = f'downloads/audio/extracted_audio.wav'
    audio_clip = AudioSegment.from_file(video_path, format='mp4')
    audio_clip.export(audio_path, format='wav')
    
    # Speech Recognition
    r = sr.Recognizer()
    audio_texts = []
    audio = sr.AudioFile(audio_path)
    
    """with audio as source:
        chunks = r.split_into_chunks(source, chunk_length=30)
        for chunk in chunks:
            try:
                text = r.recognize_google(chunk)
                audio_texts.append(text)
            except sr.UnknownValueError:
                continue"""
    
    # Split audio into chunks and perform speech recognition
    audio_clip = AudioSegment.from_file(audio_path)
    chunk_length_ms = 30000  # 30 seconds per chunk
    chunks = [audio_clip[i:i + chunk_length_ms] for i in range(0, len(audio_clip), chunk_length_ms)]

    for i, chunk in enumerate(chunks):
        # Save the chunk to a temporary file
        chunk_path = f"downloads/audio/chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
    
        with sr.AudioFile(chunk_path) as source:
            audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data)
                audio_texts.append(text)
            except sr.UnknownValueError:
                continue

    
    # Combine OCR and Audio Text
    full_text = ' '.join(ocr_texts + audio_texts)
    
    # Save Combined Transcript
    transcript_path = f'downloads/transcript_{os.path.basename(video_path)}.txt'
    with open(transcript_path, 'w') as f:
        f.write(full_text)
    
    # Upload Transcript to Firebase
    transcript_blob = bucket.blob(f'transcripts/{os.path.basename(video_path)}_transcript.txt')
    transcript_blob.upload_from_filename(transcript_path)
    
    # Generate Summary
    summary = textrank_summarize(full_text)
    
    # Create PDF Summary
    """pdf_path = f'downloads/summary_{os.path.basename(video_path)}.pdf'
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Video Summary")
    text_object = c.beginText(100, 700)
    for line in summary.split('. '):
        text_object.textLine(line)
    c.drawText(text_object)
    c.showPage()
    c.save()"""
    # Replace existing PDF generation code
    pdf_path = f'downloads/summary_{os.path.basename(video_path)}.pdf'
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Video Summary")
    text_object = c.beginText(100, 700)

        # Use the new wrapping function
    wrapped_lines = wrap_text_to_10_words(summary)
    for line in wrapped_lines:
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()
    c.save()
    
    # Upload Summary to Firebase
    summary_blob = bucket.blob(f'summaries/{os.path.basename(video_path)}_summary.pdf')
    summary_blob.upload_from_filename(pdf_path)
    
    return pdf_path


def wrap_text_to_10_words(summary):
    """
    Wrap summary text to ensure each line has approximately 10 words.
    
    Args:
        summary (str): Input summary text
    
    Returns:
        list: Lines with approximately 10 words each
    """
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

