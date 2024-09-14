from flask import Flask, render_template, request, redirect, url_for
import os
from Cartoonize import cartoonize_image

app = Flask(__name__)

# Configure the folder to store uploaded and processed files
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PROCESSED_FOLDER = os.path.join('static', 'processed')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        
        file = request.files['image']  # Match input name
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            processed_file_path = os.path.join(app.config['PROCESSED_FOLDER'], file.filename)
            
            try:
                cartoonize_image(file_path, processed_file_path)
            except Exception as e:
                print(f"Error processing image: {e}")
                return redirect(request.url)
            
            # Pass filename to the results page
            return redirect(url_for('results', filename=file.filename))
    
    return render_template('upload.html')

@app.route('/results/<filename>')
def results(filename):
    original_file_url = url_for('static', filename=f'uploads/{filename}')
    processed_file_url = url_for('static', filename=f'processed/{filename}')
    # Pass both URLs to the template
    return render_template('results.html', original_file_url=original_file_url, processed_file_url=processed_file_url)

if __name__ == '__main__':
    app.run(debug=True)
