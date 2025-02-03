# Acne Detector

Acne Detector is a web application that uses a YOLO (You Only Look Once) model to detect different types of acne in uploaded images. The application allows users to upload images, runs YOLO inference to detect acne, and returns the detection results along with the processed image.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Description

The Acne Detector project aims to provide an automated solution for detecting various types of acne in images. The application uses a YOLO model trained on annotated images to identify different acne types such as whiteheads, blackheads, papules, pustules, nodules, cysts, post-inflammatory hyperpigmentation, and scarring.

## Features

- Upload images for acne detection
- Run YOLO inference to detect acne
- Display detection results and processed image
- Support for multiple acne types

## Technologies Used

- FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.6+.
- YOLO: A state-of-the-art, real-time object detection system.
- React: A JavaScript library for building user interfaces.
- Tailwind CSS: A utility-first CSS framework for styling.
- Python-dotenv: A library to load environment variables from a `.env` file.

## Setup Instructions

### Prerequisites

- Python 3.6+
- Node.js and npm
- Git

### Backend Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/acne-detector.git
   cd acne-detector/backend

   ```

2. Create a virtual environment and activate it:
   python -m venv .venv
   source .venv/bin/activate # On Windows, use `.venv\Scripts\activate`

3. Install the required packages:
   pip install -r requirements.txt

4. Create a .env file in the backend directory and add the following environment variables:
   UPLOAD_DIR=path/to/upload/directory
   PREDICT_DIR=path/to/predict/directory
   MODEL_PATH=path/to/model/weights/best.pt

5. Run the FastAPI server:
   uvicorn main:app --reload

Frontend Setup

1. Navigate to the frontend directory:
   cd ../frontend/acne-detector-app

2. Install the required packages:
   npm install

3. Start the React development server:
   npm run dev

Usage

1. Open your web browser and navigate to your local host.
2. Upload an image for acne detection.
3. View the detection results and the processed image.

Contributing
Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature).
3. Commit your changes (git commit -m 'Add some feature').
4. Push to the branch (git push origin feature/your-feature).
5. Open a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

### Explanation

- **Project Description**: Provides an overview of the project and its purpose.
- **Features**: Lists the main features of the application.
- **Technologies Used**: Lists the technologies and frameworks used in the project.
- **Setup Instructions**: Provides detailed steps to set up the backend and frontend of the application.
- **Usage**: Explains how to use the application.
- **Contributing**: Provides guidelines for contributing to the project.
- **License**: Specifies the license under which the project is distributed.

Feel free to customize this README to better fit your project's specifics and requirements.
