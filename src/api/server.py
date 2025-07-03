from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
import time
from ..analysis.seo_analyzer import SEOAnalyzer
from ..core.config import Config
from ..core.logger import Logger
from ..core.exceptions import ConfigurationError, NetworkError, APIError, handle_exception

app = Flask(__name__)
CORS(app)

analysis_status = {}
analysis_results = {}

class SEOAnalysisThread(threading.Thread):
    def __init__(self, domain, analysis_id):
        threading.Thread.__init__(self)
        self.domain = domain
        self.analysis_id = analysis_id
        self.analyzer = SEOAnalyzer()
        Logger.info(f"Analysis thread created: {analysis_id}")
    
    def run(self):
        try:
            analysis_status[self.analysis_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Starting analysis...',
                'start_time': datetime.now().isoformat()
            }
            Logger.info(f"Analysis started: {self.analysis_id} - {self.domain}")
            
            config = Config()
            config.validate_config()
            
            analysis_status[self.analysis_id]['progress'] = 25
            analysis_status[self.analysis_id]['message'] = 'Fetching page content...'
            
            result = self.analyzer.analyze_domain(self.domain)
            
            if result:
                analysis_status[self.analysis_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Analysis completed',
                    'end_time': datetime.now().isoformat()
                }
                analysis_results[self.analysis_id] = result
                Logger.info(f"Analysis completed successfully: {self.analysis_id}")
            else:
                analysis_status[self.analysis_id] = {
                    'status': 'failed',
                    'progress': 0,
                    'message': 'Analysis failed',
                    'end_time': datetime.now().isoformat()
                }
                Logger.error(f"Analysis failed: {self.analysis_id}")
                
        except ConfigurationError as e:
            analysis_status[self.analysis_id] = {
                'status': 'failed',
                'progress': 0,
                'message': f'Configuration error: {str(e)}',
                'end_time': datetime.now().isoformat()
            }
            Logger.error(f"Configuration error: {self.analysis_id} - {str(e)}")
            
        except Exception as e:
            analysis_status[self.analysis_id] = {
                'status': 'failed',
                'progress': 0,
                'message': f'Error: {str(e)}',
                'end_time': datetime.now().isoformat()
            }
            Logger.error(f"Analysis error: {self.analysis_id} - {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    Logger.info("Health check performed")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/analyze', methods=['POST'])
@handle_exception
def start_analysis():
    Logger.info("New analysis request received")
    
    try:
        data = request.get_json()
        
        if not data or 'domain' not in data:
            Logger.warning("Invalid request: domain parameter missing")
            return jsonify({
                'error': 'Domain parameter required',
                'example': {'domain': 'example.com'},
                'info': 'API key should be set as OPENROUTER_API_KEY in .env file'
            }), 400
        
        domain = data['domain'].strip()
        
        if not domain:
            Logger.warning("Empty domain parameter")
            return jsonify({
                'error': 'Please enter a valid domain'
            }), 400
        
        try:
            config = Config()
            config.validate_config()
        except ConfigurationError as e:
            Logger.error(f"Configuration error: {str(e)}")
            return jsonify({
                'error': f'Configuration error: {str(e)}',
                'info': 'Set OPENROUTER_API_KEY value in .env file'
            }), 400
        
        analysis_id = f"analysis_{int(time.time())}_{hash(domain) % 10000}"
        Logger.info(f"Analysis ID created: {analysis_id} - {domain}")
        
        thread = SEOAnalysisThread(domain, analysis_id)
        thread.start()
        
        return jsonify({
            'analysis_id': analysis_id,
            'domain': domain,
            'status': 'started',
            'message': 'Analysis started. Use /status endpoint to check progress.'
        }), 202
        
    except Exception as e:
        Logger.error(f"Unexpected error in start_analysis: {str(e)}")
        return jsonify({
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/status/<analysis_id>', methods=['GET'])
def get_analysis_status(analysis_id):
    Logger.info(f"Status query: {analysis_id}")
    
    if analysis_id not in analysis_status:
        Logger.warning(f"Analysis ID not found: {analysis_id}")
        return jsonify({
            'error': 'Analysis ID not found'
        }), 404
    
    status = analysis_status[analysis_id]
    response = {
        'analysis_id': analysis_id,
        'status': status['status'],
        'progress': status['progress'],
        'message': status['message'],
        'start_time': status.get('start_time')
    }
    
    if status['status'] in ['completed', 'failed']:
        response['end_time'] = status.get('end_time')
    
    return jsonify(response)

@app.route('/result/<analysis_id>', methods=['GET'])
def get_analysis_result(analysis_id):
    Logger.info(f"Result request: {analysis_id}")
    
    if analysis_id not in analysis_status:
        Logger.warning(f"Analysis ID not found: {analysis_id}")
        return jsonify({
            'error': 'Analysis ID not found'
        }), 404
    
    status = analysis_status[analysis_id]
    
    if status['status'] == 'running':
        Logger.info(f"Analysis still in progress: {analysis_id}")
        return jsonify({
            'error': 'Analysis not yet completed',
            'status': status['status'],
            'progress': status['progress']
        }), 202
    
    if status['status'] == 'failed':
        Logger.warning(f"Failed analysis result requested: {analysis_id}")
        return jsonify({
            'error': 'Analysis failed',
            'message': status['message']
        }), 400
    
    if analysis_id not in analysis_results:
        Logger.error(f"Analysis result not found: {analysis_id}")
        return jsonify({
            'error': 'Analysis result not found'
        }), 404
    
    result = analysis_results[analysis_id]
    
    filename = f"seo_analysis_{analysis_id}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        Logger.info(f"Result saved to file: {filename}")
    except Exception as e:
        Logger.error(f"File save error: {str(e)}")
    
    return jsonify({
        'analysis_id': analysis_id,
        'status': 'completed',
        'result': result,
        'saved_to': filename
    })

@app.route('/analyze-sync', methods=['POST'])
@handle_exception
def analyze_sync():
    Logger.info("Synchronous analysis request received")
    
    try:
        data = request.get_json()
        
        if not data or 'domain' not in data:
            Logger.warning("Domain parameter missing in sync analysis")
            return jsonify({
                'error': 'Domain parameter required',
                'example': {'domain': 'example.com'}
            }), 400
        
        domain = data['domain'].strip()
        
        if not domain:
            return jsonify({
                'error': 'Please enter a valid domain'
            }), 400
        
        try:
            config = Config()
            config.validate_config()
        except ConfigurationError as e:
            return jsonify({
                'error': f'Configuration error: {str(e)}'
            }), 400
        
        analyzer = SEOAnalyzer()
        result = analyzer.analyze_domain(domain)
        
        if not result:
            Logger.error(f"Synchronous analysis failed: {domain}")
            return jsonify({
                'error': 'Analysis could not be completed'
            }), 500
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_domain = domain.replace('.', '_').replace('/', '_')
        filename = f"seo_analysis_{safe_domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            Logger.info(f"Synchronous analysis completed: {filename}")
        except Exception as e:
            Logger.error(f"File save error in sync analysis: {str(e)}")
        
        return jsonify({
            'status': 'completed',
            'domain': domain,
            'result': result,
            'saved_to': filename
        })
        
    except Exception as e:
        Logger.error(f"Synchronous analysis error: {str(e)}")
        return jsonify({
            'error': f'Analysis error: {str(e)}'
        }), 500

@app.route('/list-analyses', methods=['GET'])
def list_analyses():
    Logger.info("Analysis list requested")
    
    analyses = []
    for analysis_id, status in analysis_status.items():
        analyses.append({
            'analysis_id': analysis_id,
            'status': status['status'],
            'progress': status['progress'],
            'start_time': status.get('start_time'),
            'end_time': status.get('end_time')
        })
    
    return jsonify({
        'total_analyses': len(analyses),
        'analyses': analyses
    })

@app.route('/cleanup', methods=['POST'])
@handle_exception
def cleanup_old_analyses():
    Logger.info("Cleaning up old analyses")
    
    try:
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
        
        to_remove = []
        for analysis_id, status in analysis_status.items():
            if status.get('start_time'):
                start_time = datetime.fromisoformat(status['start_time']).timestamp()
                if start_time < cutoff_time:
                    to_remove.append(analysis_id)
        
        for analysis_id in to_remove:
            if analysis_id in analysis_status:
                del analysis_status[analysis_id]
            if analysis_id in analysis_results:
                del analysis_results[analysis_id]
        
        Logger.info(f"{len(to_remove)} old analyses cleaned up")
        
        return jsonify({
            'message': f'{len(to_remove)} old analyses cleaned up',
            'cleaned_analyses': to_remove
        })
        
    except Exception as e:
        Logger.error(f"Cleanup error: {str(e)}")
        return jsonify({
            'error': f'Cleanup error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    Logger.warning(f"404 error: {request.url}")
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /health',
            'POST /analyze',
            'GET /status/<analysis_id>',
            'GET /result/<analysis_id>',
            'POST /analyze-sync',
            'GET /list-analyses',
            'POST /cleanup'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    Logger.error(f"500 error: {str(error)}")
    return jsonify({
        'error': 'Internal server error'
    }), 500

def run_server(host='127.0.0.1', port=5000, debug=False):
    Logger.info(f"API server starting: {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server(debug=True) 