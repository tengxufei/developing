from flask import Flask, request, render_template, Response, jsonify
import os
import sys
import json
import io
import re
import subprocess

# Add the project root to the Python path for module discovery
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from orchestrator.main import Orchestrator

app = Flask(__name__)
orchestrator = Orchestrator(project_root)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_task', methods=['GET'])
def run_task():
    user_task = request.args.get('task')

    if not user_task:
        return Response("Error: No task provided.", mimetype='text/plain', status=400)

    def generate():
        # First, confirm connection
        connection_message = {
            'type': 'status',
            'stage': 'Connection',
            'status': 'complete',
            'message': 'Server connection established.'
        }
        yield f"data: {json.dumps(connection_message)}\n\n"
        
        try:
            # The orchestrator now returns a generator that yields a single, comprehensive payload.
            streamer = orchestrator.stream_bioinformatics_task(user_task)
            
            # Process the stream from the orchestrator
            for update_json in streamer:
                yield f"data: {update_json}\n\n"

        except Exception as e:
            # Ensure any exception is caught and sent to the client
            import traceback
            tb_str = traceback.format_exc()
            print(f"ERROR in orchestrator stream: {e}\n{tb_str}")
            error_update = {"type": "status", "stage": "Error", "status": "error", "message": f"An unexpected error occurred: {e}"}
            yield f"data: {json.dumps(error_update)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    tasks = [
        'Perform co-expression analysis for DLL3, SEZ6, and B7H3 in TCGA-GBM.',
        'Run pathway analysis on the marker genes.',
        'Find top 15 therapeutic targets.',
        'Execute the full bioinformatics workflow.',
        'Critique the analysis results.',
        'Provide a biological interpretation.'
    ]
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)