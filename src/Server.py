from flask import Flask, request, jsonify,Response
import requests
import os
import mean_sst
import threading
import xarray
import json
import uuid
docker = False
app = Flask(__name__)




job = {"status": None, "id": None}

@app.route("/doJob", methods=["POST"])
def doJob():
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=Job, args=(dataFromPost,))
    t.start()
    return Response(status=200)

@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    return jsonify(job)

#zum testen: requests.post("localhost:80/doJob",json={"arguments":{"data":data,"timeframe":["1984-10-01","1984-11-01"],"bbox":[-999,-999,-999,-999]}})


def Job(dataFromPost):
    #Funktionsaufruf von wrapper_mean_sst
    dataset = xarray.load_dataset("data/" + str(dataFromPost["arguments"]["data"]["from_node"])+".nc")
    x = mean_sst.wrapper_mean_sst(data=dataset,timeframe=dataFromPost["arguments"]["timeframe"],bbox=dataFromPost["arguments"]["bbox"])
    id = uuid.uuid1()
    id = "SST"#Todo: Löschen
    x.to_netcdf("data/"+str(id)+".nc")
    job["id"] = str(id)
    job["status"]="done"






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
