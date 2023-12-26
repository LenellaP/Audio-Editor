from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pydub import AudioSegment

import os
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_COOKIE_MAX_SIZE'] = 8192

ALLOWED_EXTENSIONS = {'mp3', 'wav'}
app.config['UPLOAD_FOLDER'] = 'C:/Users/polina/.vscode/codes/AppWeb/upload'
app.config['EDITED_FOLDER'] = 'C:/Users/polina/.vscode/codes/AppWeb/edited'

def allowed_file(filename):
    if '.' not in filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            raise Exception("No file part")

        file = request.files['file']

        if file.filename == '':
            raise Exception("No selected file")

        if file and allowed_file(file.filename):
            audio_data = file.read()

            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(audio_data)
                f.seek(0)

                # Save the file path in the session
                session['audio_file_path'] = f.name
                print("File upload successful")
                return redirect(url_for('edit'))

    except Exception as e:
        return render_template('error.html', error_message=str(e))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'audio_file_path' not in session:
        return redirect(url_for('index'))

    file_path = session['audio_file_path']

    try:
        # Load audio from the saved file path
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        return render_template('error.html', error_message=f"Error loading audio: {e}")

    if request.method == 'POST':
        try:
            volume = int(request.form['volume'])
            pitch = float(request.form['pitch'])
            speed = float(request.form['speed'])
        except ValueError:
            return render_template('error.html', error_message="Invalid volume or pitch")

        # Change pitch by setting the frame rate
        edited_audio = audio + volume
        edited_audio = edited_audio.set_frame_rate(int(audio.frame_rate * pitch))
        edited_audio = audio.speedup(playback_speed=speed)

        # Save the edited audio to a file
        edited_file_name = os.path.basename(file_path)
        edited_file_path = f"C:/Users/polina/.vscode/codes/AppWeb/edited/{edited_file_name}.mp3"

        print(f"Edited file name: {edited_file_name}")
        print(f"Edited file path: {edited_file_path}")

        # Check if the directory exists
        edited_directory = os.path.dirname(edited_file_path)
        if not os.path.exists(edited_directory):
            os.makedirs(edited_directory)

        # Save the edited audio to a file
        edited_audio.export(edited_file_path, format="mp3")

        print("File saved successfully")

        return render_template('edit.html', audio=edited_audio, edited_file_name=edited_file_name)

    return render_template('edit.html', audio=audio)
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['EDITED_FOLDER'], filename)

if app.debug:
    app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    app.run(debug=True)