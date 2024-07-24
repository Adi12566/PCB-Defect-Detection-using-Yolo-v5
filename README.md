# PCB Defect Detection using YOLOv5

This repository provides a user-friendly interface for detecting PCB (Printed Circuit Board) defects using the YOLOv5 object detection model. The interface is built with Gradio and Flask, allowing easy interaction and efficient defect detection.

## Features

- **Detect PCB Defects:** Utilize the power of YOLOv5 to identify and highlight defects on PCBs.
- **Generate Detailed Reports:** Create detailed PDF reports of detected defects with descriptions and occurrence counts.
- **Interactive Interface:** User-friendly Gradio interface for uploading images and viewing results.
- **Web-Based Access:** Access the detection tool via a web browser.

## Installation

Follow these steps to set up and run the application:

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Adi12566/PCB-Defect-Detection-using-Yolo-v5.git
   cd PCB-Defect-Detection-using-Yolo-v5

   
2. **Install Required Python Modules**

    ```bash
    pip install -r requirements.txt

    ```

3. **Start the Application**

    ```bash
    python app.py
    ```
4. **Open the Gradio Interface**

    ```arduino
    http://127.0.0.1:7860
    ```

# Usage

## Detect Defects

1. Upload an image of a PCB using the Gradio interface.
2. The YOLOv5 model will process the image and detect any defects.
3. View the detected defects on the interface.

## Generate PDF Report

1. Upload an image of a PCB using the Gradio interface.
2. The YOLOv5 model will process the image and detect any defects.
3. A PDF report will be generated, listing each defect with a description and count of occurrences.

# Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make your changes.
4. Commit your changes (git commit -am 'Add new feature').
5. Push to the branch (git push origin feature-branch).
6. Create a new Pull Request.

# License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

# Acknowledgments

* [YOLOv5](https://github.com/ultralytics/yolov5/) for object detection
* [Gradio](https://www.gradio.app) for the interactive interface
* [Flask](https://flask.palletsprojects.com/en/3.0.x/) for the web framework
* [PIL](https://pypi.org/project/pillow/) for image processing
