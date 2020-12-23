#Python Version
FROM python:3.8.6

#Kopiere requirements
COPY req.txt .

#Installiere Abhängigkeiten
RUN pip install -r req.txt

#Port Oeffnen Empfehlung, beim starten noch mit -80:80 ausführen
EXPOSE 80

#Kopiere Code
COPY src/ .

#Ausführen beim Starten
CMD ["python3", "./Server.py"]