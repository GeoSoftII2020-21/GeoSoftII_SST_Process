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




job = {"status": None, "id": None, "jobid": None, "errorType":None}

@app.route("/doJob/<uuid:id>", methods=["POST"])
def doJob(id):
    """
    Takes a given job and starts the processing
    :param id:
    :return:
    """
    dataFromPost = request.get_json()
    job["status"] = "processing"
    t = threading.Thread(target=jobwrapper, args=(dataFromPost, id,))
    t.start()
    return Response(status=200)

@app.route("/jobStatus", methods=["GET"])
def jobStatus():
    """
    Returns the job status
    :return:
    """
    return jsonify(job)

def jobwrapper(dataFromPost, id):
    """
    Wrapper function for the SST Job
    :rtype: object
    """
    Job(dataFromPost, id)
    try:
        #Job(dataFromPost, id)
        print("Test")
    except:
        job["status"] = "error"
        job["errorType"] = "Unkown Error"
        return




def Job(dataFromPost, id):
    """
    Starts the job processing
    :param dataFromPost:
    :param id:
    :return:
    """
    job["status"] = "running"
    job["jobid"] = str(id)
    dataset = xarray.open_dataset("data/" + str(id) +"/"+ str(dataFromPost["arguments"]["data"]["from_node"])+".nc")

    try:
        x = mean_sst.wrapper_mean_sst(data=dataset, timeframe=dataFromPost["arguments"]["timeframe"],
                                      bbox=dataFromPost["arguments"]["bbox"])

    except mean_sst.ParameterTypeError as e:
        job["status"] = "error"
        job["errorType"] ="ParameterTypeError"
        return
    except mean_sst.BboxLengthError as e:
        job["status"] = "error"
        job["errorType"] = "BboxLengthError"
        return
    except mean_sst.LongitudeValueError as e:
        job["status"] = "error"
        job["errorType"] = "LongitudeValueError"
        return
    except mean_sst.LatitudeValueError as e:
        job["status"] = "error"
        job["errorType"] = "LatitudeValueError"
        return
    except mean_sst.BboxCellsizeError as e:
        job["status"] = "error"
        job["errorType"] = "BboxCellsizeError"
        return
    except mean_sst.TimeframeLengthError as e:
        job["status"] = "error"
        job["errorType"] = "TimeframeLengthError"
        return
    except mean_sst.TimeframeValueError as e:
        job["status"] = "error"
        job["errorType"] = "TimeframeValueError"
        return
    except:
        job["status"] = "error"
        job["errorType"] = "UnkownError"
        return


    subid = uuid.uuid1()
    x.to_netcdf("data/"+str(id)+"/"+str(subid)+".nc")
    job["id"] = str(subid)
    job["status"]="done"






def main():
    """
    Starts the server.
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
