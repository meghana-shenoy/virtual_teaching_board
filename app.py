from flask import Flask, render_template, send_file
import subprocess
from PIL import Image

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute_main_file')
def execute_main_file():
    subprocess.run(['python', 'mainfile.py'])
    # Add code to execute main file here
    return 'Main file executed successfully'

@app.route('/execute_main_file1')
def execute_main_file1():
    subprocess.run(['python', 'mainfile1.py'])
    # Add code to execute main file here
    return 'Main file1 executed successfully'

@app.route('/execute_check_color')
def execute_check_color():
    subprocess.run(['python', 'checkcolor.py'])
    # Add code to execute main file here
    return 'check color executed successfully'

@app.route('/convert_image_to_pdf')
def convert_image_to_pdf():
    # Add code to convert image to PDF here
    input_image_path = "paintWindow.png"
    output_pdf_path = "output_pdf.pdf"
    convert_image_to_pdf(input_image_path, output_pdf_path)
    return send_file(output_pdf_path, as_attachment=True)

def convert_image_to_pdf(image_path, output_path):
    image = Image.open(image_path)
    pdf_path = output_path
    # Convert image to PDF
    image.convert('RGB').save(pdf_path, "PDF", resolution=100.0)

if __name__ == '__main__':
    app.run(debug=True)
