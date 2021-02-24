@ECHO OFF


echo cargando anaconda
call C:\Users\felip\anaconda3\Scripts\activate.bat C:\Users\felip\anaconda3
cd C:\Users\felip\Documents\GitHub\Process-Light-Fields-Captured-with-Lytro-Camera-via-Light-Field-Toolbox-for-MATLAB
python video_maker.py

PAUSE
