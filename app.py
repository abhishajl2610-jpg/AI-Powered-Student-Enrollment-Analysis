import os
import json
from flask import Flask, render_template, jsonify, request
import sys

# Ensure src is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from src import gemini_service
except ImportError:
    import gemini_service

app = Flask(__name__)

DATA_PATH = os.path.join('outputs', 'dashboard_data.json')

def load_dashboard_data():
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    data = load_dashboard_data()
    if data is None:
        return jsonify({"error": "Data not found. Please run export_dashboard_data.py first."}), 404
    return jsonify(data)

@app.route('/api/ai/summary', methods=['POST'])
def api_ai_summary():
    req_data = request.json or {}
    kpis = req_data.get('kpis', {})
    if not kpis:
        return jsonify({"error": "No KPIs provided"}), 400
    try:
        summary = gemini_service.summarize_dashboard_kpis(kpis)
        return jsonify({"insight": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/trend', methods=['POST'])
def api_ai_trend():
    req_data = request.json or {}
    stats = req_data.get('stats', {})
    if not stats:
        return jsonify({"error": "No stats provided"}), 400
    try:
        insight = gemini_service.generate_trend_insight(stats)
        return jsonify({"insight": insight})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/prediction', methods=['POST'])
def api_ai_prediction():
    req_data = request.json or {}
    try:
        explanation = gemini_service.explain_prediction(
            state_ut=req_data.get('state_ut', 'Unknown'),
            year_int=req_data.get('year_int', 2024),
            predicted=req_data.get('predicted', 0),
            model_name=req_data.get('model_name', 'Unknown'),
            model_r2=req_data.get('model_r2', 0.0)
        )
        return jsonify({"insight": explanation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/ask', methods=['POST'])
def api_ai_ask():
    req_data = request.json or {}
    question = req_data.get('question', '')
    context = req_data.get('context', '')
    if not question or not context:
        return jsonify({"error": "Missing question or context"}), 400
    try:
        answer = gemini_service.ask_data_question(question, context)
        return jsonify({"insight": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
