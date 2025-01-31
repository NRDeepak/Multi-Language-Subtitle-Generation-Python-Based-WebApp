import extract_audio
import transcribe_audio
import generate_subtitle_file
import add_subtitle_to_video
import convert_subtitle_file
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi'}
#fill_this_out
app.secret_key = 'your_secret_key_here'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_video(selected_language, input_path, output_path):
    translate_language = str(selected_language)
    input_video = input_path
    input_video_name = input_video.replace(".mp4", "")

    extracted_audio = extract_audio.extract_audio_from_video().extract_audio(input_video_name=input_video_name,
                                                                             input_video=input_video)

    language, segments = transcribe_audio.transcribe_audio_class().transcribe(audio=extracted_audio)

    subtitle_file = generate_subtitle_file.generate_sub_file_srt().generate_subtitle_file(language=language,
                                                                                          segments=segments,
                                                                                          input_video_name=input_video_name,
                                                                                          translate_language=translate_language)

    converted_subtitle_file = convert_subtitle_file.convert_srt_ass().convert_srt_to_ass(subtitle_file=subtitle_file)

    add_subtitle_to_video.add_sub_to_video().add_subtitle_to_video(soft_subtitle=False,
                                                                   subtitle_file=converted_subtitle_file,
                                                                   input_video_name=input_video_name,
                                                                   input_video=input_video)




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    selected_language = request.form.get('action')

    if file and allowed_file(file.filename):

        original_filename = secure_filename(file.filename)

        processed_filename = f"processed-{original_filename.replace(".mp4", "")}-with-captions.mp4"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)

        file.save(original_filename)


        process_video(selected_language,original_filename, processed_path)


        return {'download_link': url_for('download_file', filename=processed_filename)}

    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)