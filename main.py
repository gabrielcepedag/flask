from flask import Flask, request, jsonify, render_template
import requests
import uuid
import json
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "https://api-panama.infinitetech.me/"}})
# CORS(app, resources={r"/*": {"origins": "http://localhost:6789.com"}})

URL = 'http://dev-admin.orkapi.net:6815/api/servicio/'
TOKEN = None

@app.route('/deposito', methods=['GET'])
def deposito():
    global TOKEN
    terminalId = request.args.get('idTerminal')
    monto = request.args.get('monto')
    consulta = consultar_agente_prepago(terminalId)

    if (consulta.get('transaccion')):
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

        respuesta = json.loads(response.content)
        if (response.status_code == 200):
            print(response.content)
            return jsonify(respuesta)
        elif (response.content.get('error') == 'Necesita iniciar sesión.'):
            login(terminalId)
            deposito()
        else:
            print("Error de API: "+str(respuesta))
            return respuesta
    else:
        print('No existe transaccion en consultar agente prepago')
        return consulta
    

@app.route('/consulta-agente', methods=['GET'])
def home():
    terminalId = request.args.get('idTerminal')
    message = consultar_agente_prepago(terminalId=terminalId)

    return jsonify(message)


def consultar_agente_prepago(terminalId):

    login(terminalId=terminalId)
    global TOKEN
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    uuid = generar_uuid()
    consulta = f'terminales/{terminalId}/consultar?tag={terminalId}&referencia_externa={uuid}'

    response = requests.get(URL+consulta, headers=headers)
    if (response.content.get('error') == 'Necesita iniciar sesión.'):
        login(terminalId)
        consultar_agente_prepago(terminalId)
    respuesta = json.loads(response.content)
    

    if (response.status_code == 200):
        print(respuesta)
        return respuesta
    else:
        print("Error de API EN consultar_agente_prepago: "+str(respuesta))
        return respuesta
    

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
        respuesta = json.loads(response.content)
        if (response.status_code == 200):
            TOKEN = respuesta['data']['jwt_token']
            # print(respuesta)
            print('Devolviendo TOKEN')
            return {'token' : respuesta['data']['jwt_token']}
        else:
            print("Error de API en login: "+str(respuesta))
            return respuesta
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
    # app.run(host='0.0.0.0', port=6789, debug=True)
