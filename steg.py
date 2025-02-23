from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image
import stepic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files or 'message' not in request.form:
        return "Missing image or message", 400
    
    image = request.files['image']
    message = request.form['message']
    
    if image.filename == '' or not allowed_file(image.filename):
        return "Invalid file format. Only PNG images are allowed.", 400
    
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    
    try:
        img = Image.open(image_path)
        encoded_img = stepic.encode(img, message.encode())
        encoded_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + filename)
        encoded_img.save(encoded_path)
        return send_file(encoded_path, as_attachment=True)
    except Exception as e:
        return f"Error encoding image: {str(e)}", 500

@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        return "Missing image", 400
    
    image = request.files['image']
    
    if image.filename == '' or not allowed_file(image.filename):
        return "Invalid file format. Only PNG images are allowed.", 400
    
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    
    try:
        img = Image.open(image_path)
        message = stepic.decode(img)
        return f"Hidden Message: {message.decode()}"
    except Exception as e:
        return f"Error decoding image: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)