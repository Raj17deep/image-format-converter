from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = '9d4d9417c260034752461e782a63a0e327737194dcfee9d435fd988364d1ea56'  # Replace with a real secret key

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        target_format = request.form.get('format')

        # Validate file selection
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Validate file type
        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed types: PNG, JPG, JPEG, WEBP')
            return redirect(request.url)

        try:
            # Process image
            img = Image.open(file.stream)
            img_io = BytesIO()

            # Handle grayscale conversion
            if target_format == 'grayscale':
                gray_img = img.convert('L')
                gray_img.save(img_io, 'PNG')
                img_io.seek(0)
                return send_file(
                    img_io,
                    mimetype='image/png',
                    as_attachment=True,
                    download_name='converted_grayscale.png'
                )

            # Handle other formats
            if target_format in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.save(img_io, format=target_format.upper())
            img_io.seek(0)

            mimetype = f'image/{target_format}' if target_format != 'jpg' else 'image/jpeg'
            extension = target_format if target_format != 'jpg' else 'jpeg'

            return send_file(
                img_io,
                mimetype=mimetype,
                as_attachment=True,
                download_name=f'converted.{extension}'
            )

        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)