import os
import sys
import psutil
from flask import Flask, jsonify, render_template

# Ensure we can import history_store
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from history.history_store import get_analytics_summary

# Setup templates and static folder paths relative to this file
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system')
def system_metrics():
    # Get CPU usage
    cpu_percent = psutil.cpu_percent(interval=None)
    # Get memory usage
    memory = psutil.virtual_memory()
    mem_percent = memory.percent
    
    return jsonify({
        "cpu": cpu_percent,
        "memory": mem_percent
    })

@app.route('/api/analytics')
def analytics():
    try:
        data = get_analytics_summary()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def start_server(port=5000):
    app.run(host='127.0.0.1', port=port, debug=False)

if __name__ == '__main__':
    start_server()
