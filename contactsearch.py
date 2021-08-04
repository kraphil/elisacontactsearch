import logging
import requests

import flask
from flask import request

logging.basicConfig( level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def requestZip(zip):
    url = "https://app-data.des-mia.de/plzservice/nearest/" + zip

    response = requests.get(url)
    json_data = response.json()

    response = "Ihr nächstgelegener Mieterverein: Name: " + json_data['results'][0]['name']+", Stadt: "+ json_data['results'][0]['city']+ ", Str.: " + json_data['results'][0]['street']+", PLZ: " + json_data['results'][0]['zip']+", Tel.: " + json_data['results'][0]['phone']+", Mail.: " + json_data['results'][0]['web']+"."
    return response

 
def extractZip(userMessage):
    if(len(userMessage) == 0):
        zip = ""
    else:
        zip = userMessage['messages'][0]['data']['content']
    return zip

def extractConversationId(userMessage):
    if(len(userMessage) == 0):
        conversationId = ""
    else:
        conversationId = userMessage['conversationId']
    return conversationId    

def createAnswer(conversationId, responseZip):
    payload = {
      "conversationId" : conversationId,
      "messages": [
        {
          "type" : "message",
          "data" : {
            "type" : "text/plain",
            "content" : responseZip
          }
        }
      ]
    }
    return json.dumps(payload)


#App
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/0.0.0.0", methods=["GET"])
def defaultFunction():
    return """<h1>Kontaktsuche</h1>""" 


@app.route("/", methods=["GET"])  # localhost
def home():
    return """<h1>Kontaktsuche</h1>"""


@app.route("/request", methods=["POST"])
def api_response_message():
    referer = request.headers.get("Referer")
    if referer is None:
      referer = request.args.get("referer")
    referer = referer.replace("//", "https://")
    # logging.info("____ referer: %s", referer)

    endpointUrl = referer + "/api/v1/conversation/send"
    message =  request.get_json(force=True)
    logging.info("____ message: %s", message)

    conversationId = extractConversationId(message)
    zip = extractZip(message)

    if(len(zip) == 0):
        zip = "Es konnte kein Postleitzahl erkannt werden!"
    else:    
        responseZip = requestZip(zip)
    answer = createAnswer(conversationId, responseZip)
    try:
      # logging.info("____ endpointUrl: %s", endpointUrl)
      # logging.info("Request data: {0}".format(answer))
      response = requests.post(endpointUrl, data=answer, headers={'content-type': 'application/json'})
      # logging.info("Request endpoint response: {0}".format(response))
    except requests.exceptions.RequestException as e:
      logging.debug("Request endpoint error: {0}".format(e))
    return ('{}', 200)


if __name__ == '__main__':
    app.run(debug=True)
