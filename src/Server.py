from flask import Flask, request, jsonify
import requests
app = Flask(__name__)

@app.route("/doJob", methods=["POST"])
def doJob():
    dataFromPost = request.get_json()
    #Todo: Eval. Json
    data = None #Todo: Json fordert Konkrete Daten an. API Aushandeln
    r = requests.get("http://localhost:443/data", json=data)
    #Todo: Funktions aufruf was daten bearbeitet
    data = None
    return jsonify(data)






def main():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    app.run(debug=True, host="0.0.0.0", port=444)


if __name__ == "__main__":
    main()
