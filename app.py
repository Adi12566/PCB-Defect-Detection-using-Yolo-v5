import io
from flask import Flask, request, jsonify, send_file
import subprocess
import os
from PIL import Image
import gradio as gr
from fpdf import FPDF
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

def run_detection(image_path):
    # Path to detect.py script relative to the current script
    detect_script = os.path.join(os.getcwd(), 'detect.py')
    weights_file = os.path.join(os.getcwd(), 'best.pt')
    
    # Call the detect.py script using subprocess and capture the output directory
    result = subprocess.run(['python', detect_script, '--source', image_path, '--weights', weights_file, '--save-txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Find the latest res{number} directory under output
    detect_dir = os.path.join(os.getcwd(), 'output')
    res_dirs = [d for d in os.listdir(detect_dir) if d.startswith('res') and os.path.isdir(os.path.join(detect_dir, d))]
    latest_res = max(res_dirs, key=lambda d: int(d[3:])) if res_dirs else None
    
    if latest_res:
        output_dir = os.path.join(detect_dir, latest_res)
        output_image_path = os.path.join(output_dir, 'uploaded_image.jpg')  # Adjust based on your output image format
        txt_file_path = os.path.join(output_dir, 'labels', os.path.basename(image_path).replace('.jpg', '.txt'))
        return output_image_path, txt_file_path
    else:
        return None, None

def parse_defect_data():
    # Parse the data.xml file to get defect information
    tree = ET.parse('data.xml')
    root = tree.getroot()
    
    defect_data = {}
    for defect in root.findall('Defect'):
        class_num = defect.find('Class').text
        defect_type = defect.find('Type').text
        description = defect.find('Cause/Description').text
        defect_data[class_num] = {
            'type': defect_type,
            'description': description
        }
    
    return defect_data

def read_detected_classes(txt_file_path):
    detected_classes = []
    if os.path.exists(txt_file_path):
        with open(txt_file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts and parts[0].isdigit():
                    detected_classes.append(parts[0])
    return detected_classes

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Save the image to the current directory
    image_path = os.path.join(os.getcwd(), file.filename)
    file.save(image_path)
    
    # Run the detection script
    output_image_path, _ = run_detection(image_path)
    
    if output_image_path:
        return send_file(output_image_path, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No detection results found.'}), 404

def generate_pdf(image):
    # Save the image to the current directory
    image_path = os.path.join(os.getcwd(), 'uploaded_image.jpg')
    image.save(image_path)
    
    # Run the detection script
    output_image_path, txt_file_path = run_detection(image_path)
    
    if output_image_path and txt_file_path:
        # Parse the defect data
        defect_data = parse_defect_data()
        
        # Read detected classes
        detected_classes = read_detected_classes(txt_file_path)
        
        # Count the occurrences of each defect
        defect_counts = Counter(detected_classes)
        
        # Create a PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add header with title and date
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'Defect Detection Report', 0, 1, 'C')
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
        
        pdf.ln(10)  # Add some space after the header
        
        # Add input image to PDF
        if os.path.exists(image_path):
            pdf.image(image_path, x=10, y=40, w=90)
        else:
            print(f"Input image not found: {image_path}")
        
        # Add output image to PDF
        if os.path.exists(output_image_path):
            pdf.image(output_image_path, x=110, y=40, w=90)
        else:
            print(f"Output image not found: {output_image_path}")
        
        # Add defect information to PDF
        pdf.set_xy(10, 140)
        pdf.set_font("Arial", size=12)
        
        pdf.cell(0, 10, "Detected Defects:", ln=True)
        pdf.set_font("Arial", size=10)
        
        counter = 1
        for class_id, count in defect_counts.items():
            defect_info = defect_data.get(class_id)
            if defect_info:
                description = f"{counter}. {defect_info['type']}: {defect_info['description']}"
                if count > 1:
                    description += f" (Detected {count} times)"
                pdf.multi_cell(0, 10, description)
                counter += 1
    
        
        # Save the PDF to a file
        pdf_output_path = os.path.join(os.getcwd(), 'output.pdf')
        pdf.output(pdf_output_path)
        
        return pdf_output_path
    else:
        return 'No detection results found.'

# Gradio interface (if you're using it)
def gradio_interface(image):
    # Save the image to the current directory
    image_path = os.path.join(os.getcwd(), 'uploaded_image.jpg')
    image.save(image_path)
    
    # Run the detection script
    output_image_path, _ = run_detection(image_path)
    
    if output_image_path:
        return Image.open(output_image_path)
    else:
        return 'No detection results found.'

iface = gr.Interface(
    fn=gradio_interface,
    inputs=gr.Image(type='pil'),
    outputs=gr.Image(type='pil'),
    live=True
)

def gradio_pdf_interface(image):
    pdf_path = generate_pdf(image)
    if pdf_path and os.path.exists(pdf_path):
        return pdf_path
    else:
        return 'PDF generation failed.'

iface_pdf = gr.Interface(
    fn=gradio_pdf_interface,
    inputs=gr.Image(type='pil'),
    outputs=gr.File()
)

# Combine the interfaces
iface = gr.TabbedInterface([iface, iface_pdf], ["Detect Defects", "Generate PDF"])

# Flask app launch
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
    app.run(debug=True, host='0.0.0.0', port=5000)
