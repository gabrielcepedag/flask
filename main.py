from flask import Flask, request, jsonify, render_template
import requests
import uuid
import json
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "https://api-panama.infinitetech.me/"}})

URL = 'http://dev-admin.orkapi.net:6815/api/servicio/'
TOKEN = None

@app.route('/consulta-agente', methods=['GET'])
def home():
    terminalId = request.args.get('idTerminal')
    message = consultar_agente_prepago(terminalId=terminalId)

    return jsonify(message), 200


@app.route('/deposito', methods=['GET'])
def deposito():
    terminalId = request.args.get('idTerminal')
    monto = request.args.get('monto')
    consulta = consultar_agente_prepago(terminalId)
    
    if (consulta['transaccion']):
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }
        uuid = generar_uuid()
        transaccionId = consulta['transaccion']
        data = { 
            "transaccion" : transaccionId,
            "monto" : monto,
            "tag" : terminalId,
            "referencia_externa" : uuid
        }
        string = f'terminales/{terminalId}/depositar'
        login(terminalId)
        response = requests.post(URL+string, json=data, headers=headers)

        if (response.status_code == 200):
            print(response.content)
            respuesta = json.loads(response.content)
            
            return jsonify(respuesta), 200
        else:
            message = f'Error al hacer deposito: {response.content}'
            return {"message" : message}
    else:
        return {"message" : consulta}


def consultar_agente_prepago(terminalId):
    login(terminalId=terminalId)
    global TOKEN
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    uuid = generar_uuid()
    consulta = f'terminales/{terminalId}/consultar?tag={terminalId}&referencia_externa={uuid}'

    response = requests.get(URL+consulta, headers=headers)
    if (response.status_code == 200):
        respuesta = json.loads(response.content)
        # print(respuesta)
        return respuesta
    else:
        print(response.content)
        return {"message" : "Error al consultar agente prepago"}

def login(terminalId):
    global TOKEN
    username = "c08f8fca@orkapi_demo"
    password = "123456"
    data = { 
        "usuario" : 
        {
            "username" : username,
            "password" : password
        }
    }
    if (TOKEN == None):
        print('Entre a buscar token')
        response = requests.post(URL+'sessions', json=data)
        if (response.status_code == 200):
            respuesta = json.loads(response.content)
            TOKEN = respuesta['data']['jwt_token']
            # print(respuesta)
            return {'token' : respuesta['data']['jwt_token']}
        else:
            print(response.content)
            return {"message" : "Error al hacer login"}
    else:
        print('Ya tengo token')
        return {'token' : TOKEN}


def generar_uuid():
    return str(uuid.uuid4())


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
