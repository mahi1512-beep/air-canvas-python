# air-canvas-python
A gesture controlled virtual drawing application built using Python, OpenCV, and MediaPipe.  
This project enables users to draw on a digital canvas using hand movements captured via a webcam.

Features

Hand gesture recognition using MediaPipe  
Drawing using index finger tracking  
Eraser functionality  
Multiple color selection  
Real time webcam input  

Tech Stack

Python  
OpenCV  
MediaPipe  
NumPy  

Project Structure

Air_canvas.py   Main application file  

How to Run

Clone the repository  
git clone https://github.com/mahi1512-beep/air-canvas-python.git  

Navigate to the project folder  
cd air-canvas-python  

Install required dependencies  
pip install opencv-python mediapipe numpy  

Run the application  
python Air_canvas.py  

How It Works

The application uses a webcam to capture live video. MediaPipe detects hand landmarks, and the position of the index finger is tracked to simulate drawing on the screen using OpenCV.

Future Improvements

Add shape drawing functionality  
Save drawings as image files  
Improve user interface  
Add multi hand support  

Author

Mahendra Singh
