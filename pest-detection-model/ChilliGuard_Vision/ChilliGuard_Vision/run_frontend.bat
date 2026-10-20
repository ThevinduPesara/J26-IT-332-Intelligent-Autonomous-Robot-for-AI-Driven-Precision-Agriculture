@echo off
cd /d "%~dp0frontend"
"C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" -m streamlit run app.py
pause
