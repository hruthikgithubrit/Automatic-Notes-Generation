from flask import Flask, request, send_file, render_template
from src.youtube_processing import process_youtube_video
from src.video_processing import process_local_video

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html') 

@app.route('/process', methods=['POST'])
def process_video():
    youtube_url = request.form.get('youtube_url')
    video_file = request.files.get('video_file')
    
    if youtube_url:
        pdf_path = process_youtube_video(youtube_url)
    elif video_file:
        video_path = 'downloads/uploaded_video' + video_file.filename
        video_file.save(video_path)
        pdf_path = process_local_video(video_path)
    else:
        return "No video provided", 400
    
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)