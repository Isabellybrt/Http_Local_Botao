from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Dados mais recentes
latest_data = {
    "button": False,
    "temp": 0.0,
    "timestamp": time.time()
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Monitor de Botão e Temperatura</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .status { 
            padding: 20px; 
            margin: 10px 0; 
            border-radius: 5px;
            background-color: #f0f0f0;
        }
        .button-on { background-color: #ffcccc; }
        .button-off { background-color: #ccffcc; }
        .temp-high { color: #ff3333; }
        .temp-normal { color: #3333ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Monitor de Hardware</h1>
        
        <div id="button-status" class="status button-off">
            Status do Botão: <span id="button-state">DESLIGADO</span>
        </div>
        
        <div id="temp-status" class="status">
            Temperatura: <span id="temp-value">0.0</span>°C
        </div>
        
        <div class="status">
            Última atualização: <span id="last-update">Nunca</span>
        </div>
    </div>

    <script>
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    // Atualiza botão
                    const buttonState = document.getElementById('button-state');
                    const buttonDiv = document.getElementById('button-status');
                    if (data.button) {
                        buttonState.textContent = "LIGADO";
                        buttonDiv.className = "status button-on";
                    } else {
                        buttonState.textContent = "DESLIGADO";
                        buttonDiv.className = "status button-off";
                    }
                    
                    // Atualiza temperatura
                    const tempElement = document.getElementById('temp-value');
                    tempElement.textContent = data.temp.toFixed(2);
                    tempElement.className = data.temp > 30 ? "temp-high" : "temp-normal";
                    
                    // Atualiza timestamp
                    const now = new Date(data.timestamp * 1000);
                    document.getElementById('last-update').textContent = now.toLocaleTimeString();
                });
        }
        
        // Atualiza a cada segundo e na carga inicial
        setInterval(updateData, 1000);
        updateData();
    </script>
</body>
</html>
"""

@app.route("/data", methods=["GET"])
def get_data():
    # Se receber novos dados via GET, atualiza
    if 'button' in request.args:
        latest_data['button'] = request.args.get('button', '0') == '1'
    if 'temp' in request.args:
        latest_data['temp'] = float(request.args.get('temp', '0.0'))
    latest_data['timestamp'] = time.time()
    
    print(f"Recebido - Botão: {latest_data['button']}, Temp: {latest_data['temp']}°C")
    return jsonify(latest_data)

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)