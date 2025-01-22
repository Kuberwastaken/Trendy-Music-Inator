from flask import Flask, request, jsonify, render_template
from audio_processing import analyze_audio

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trendy', methods=['POST'])
def trendy():
    data = request.json
    youtube_link = data.get('youtube_link')

    if not youtube_link:
        return jsonify({'error': 'YouTube link is required'}), 400

    timestamps = analyze_audio(youtube_link)

    if not timestamps:
        return jsonify({'error': 'Failed to process audio or no trendy parts found'}), 500

    return jsonify({'trendy_parts': {'start': timestamps[0], 'end': timestamps[1]}}), 200

if __name__ == '__main__':
    app.run(debug=True)