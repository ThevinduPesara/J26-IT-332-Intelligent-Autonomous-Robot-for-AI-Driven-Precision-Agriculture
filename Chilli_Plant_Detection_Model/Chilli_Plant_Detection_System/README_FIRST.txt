CHILLI PLANT DETECTION FULL AI SYSTEM
FastAPI Backend + Streamlit Frontend
=====================================

YOUR MODEL
----------
This package is already configured for:

C:\Users\LENOVO\Downloads\Lithira_Ai_part\Lithira_YOLO_NPK\training_results\YOLO11s_NPK\weights\best.pt

Expected model classes:

0 = Healthy
1 = N_Def
2 = P_Def
3 = K_Def


RECOMMENDED LOCATION
--------------------
Extract this whole folder to:

...\Chilli_Plant_Detection_System


FIRST TIME ONLY
---------------
Double-click:

install_all.bat


START THE COMPLETE SYSTEM
-------------------------
Double-click:

run_all.bat

It opens:

FastAPI Backend:
http://127.0.0.1:8000

FastAPI Swagger:
http://127.0.0.1:8000/docs

Streamlit Frontend:
http://127.0.0.1:8501


FRONTEND FEATURES
-----------------
1. Modern chilli-themed Streamlit dashboard.
2. Image upload.
3. Browser camera capture.
4. Live local webcam inference stream.
5. Overall Healthy / N_Def / P_Def / K_Def result.
6. Confidence display.
7. Original and annotated image comparison.
8. Every YOLO bounding-box detection.
9. Class summary chart and table.
10. FastAPI connection and model status.
11. Online chilli reference photos in the UI with attribution.


IMPORTANT
---------
Do NOT run backend/app/main.py directly.

Use:

run_backend.bat

or:

cd backend
C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000


IF YOUR MODEL PATH CHANGES
--------------------------
Edit:

backend\.env

and change:

MODEL_PATH=...


POWER SHELL / CONDA ISSUE
-------------------------
You do NOT need:

conda activate torch_gpu

The BAT files use the environment's Python executable directly:

C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe


CAMERA MODES
------------
Camera Capture:
Uses the camera through the Streamlit/browser interface and sends one frame to FastAPI.

Live Local Camera:
Uses the camera physically connected to the machine running FastAPI.
The backend continuously runs YOLO and streams the annotated frames.


RESEARCH NOTE
-------------
This is an AI screening interface.
Model predictions are not a replacement for laboratory nutrient analysis or professional agronomic diagnosis.
