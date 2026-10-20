CHILLIGUARD VISION
==================

Pest detection frontend + FastAPI backend for Thevindu's chilli pest module.

MODEL
-----
Expected trained model:
C:\Users\LENOVO\Downloads\Thevindu_AI_Part\training_results\YOLOv8n_Pest_Detection\weights\best.pt

Expected model classes:
0 = MP (Aphid)
1 = BT (Whitefly)
2 = T  (Thrips)
3 = C  (Caterpillar)

QUICK START
-----------
1. Extract the folder anywhere.
2. Make sure the trained best.pt remains at the path shown above.
3. Run install_all.bat once if required.
4. Double-click run_all.bat.
5. Backend:  http://127.0.0.1:8000
6. API docs: http://127.0.0.1:8000/docs
7. Frontend: http://localhost:8501

MANUAL START
------------
Backend:
cd "<this folder>\backend"
"C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

Frontend (new terminal):
cd "<this folder>\frontend"
"C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" -m streamlit run app.py

WHAT THE BACKEND RETURNS
------------------------
- pest class
- common pest name
- confidence score
- bounding box
- target centre in pixels
- normalized target centre
- annotated image
- per-class detection summary

SPRAY TARGET NOTE
-----------------
The returned target centre is an image coordinate. It is not yet a physical nozzle coordinate.
Before real spraying, calibrate the camera position, field of view, nozzle position, actuator motion and safety limits.

FOLDERS
-------
backend/
  app/
    config.py
    main.py
    model_service.py
  outputs/
  requirements.txt

frontend/
  app.py
  requirements.txt
  .streamlit/config.toml
  IMAGE_SOURCE.txt

IMAGE CREDIT
------------
The interface uses a Wikimedia Commons reference image:
"Paprika mit Blattlaus Befall-2-Josef Schlaghecken.jpg"
Author: Schlaghecken Josef
License: CC BY 4.0
