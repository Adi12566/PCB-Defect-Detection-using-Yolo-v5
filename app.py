import io
from flask import Flask, request, jsonify, send_file
import subprocess
import os
from PIL import Image
import gradio as gr
from fpdf import FPDF


# Initialize Flask app
app = Flask(__name__)

def run_detection(image_path):
    # Path to detect.py script relative to the current script
    detect_script = os.path.join(os.getcwd(), 'detect.py')
    weights_file = os.path.join(os.getcwd(), 'best.pt')
    
    # Call the detect.py script using subprocess and capture the output directory
    result = subprocess.run(['python', detect_script, '--source', image_path, '--weights', weights_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Find the latest res{number} directory under output
    detect_dir = os.path.join(os.getcwd(), 'output')
    res_dirs = [d for d in os.listdir(detect_dir) if d.startswith('res') and os.path.isdir(os.path.join(detect_dir, d))]
    latest_res = max(res_dirs, key=lambda d: int(d[3:])) if res_dirs else None
    
    if latest_res:
        output_dir = os.path.join(detect_dir, latest_res)
        output_image_path = os.path.join(output_dir, 'uploaded_image.jpg')  # Adjust based on your output image format
        return output_image_path
    else:
        return None

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Save the image to the current directory
    image_path = os.path.join(os.getcwd(), file.filename)
    file.save(image_path)
    
    # Run the detection script
    output_image_path = run_detection(image_path)
    
    if output_image_path:
        return send_file(output_image_path, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No detection results found.'}), 404
    

def generate_pdf(image):
    # Save the image to the current directory
    image_path = os.path.join(os.getcwd(), 'uploaded_image.jpg')
    image.save(image_path)
    
    # Run the detection script
    output_image_path = run_detection(image_path)
    
    if output_image_path:
        # Create a PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add input image to PDF
        pdf.image(image_path, x=10, y=10, w=90)
        
        # Add output image to PDF
        pdf.image(output_image_path, x=110, y=10, w=90)
        
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
    output_image_path = run_detection(image_path)
    
    if output_image_path:
        return Image.open(output_image_path)
    else:
        return 'No detection results found.'

# Gradio interface (if you're using it)
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
