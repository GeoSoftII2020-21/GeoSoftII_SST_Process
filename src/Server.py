from flask import Flask, request, jsonify
import requests
import os
docker = False
app = Flask(__name__)




job = {"status": "running"}

@app.route("/doJob", methods=["POST"])
def doJob():
    dataFromPost = request.get_json()
    #Todo: Eval. Json
    data = None #Todo: Json fordert Konkrete Daten an. API Aushandeln
    #Todo: Funktions aufruf was daten bearbeitet

    data = None
    return jsonify(data)

@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    return jsonify(job)






def main():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    if docker:
        port = 80
    else:
        port=442
    app.run(debug=True, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
