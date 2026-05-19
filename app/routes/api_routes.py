from flask import Blueprint, request, jsonify
from ..ai_bird import get_bird_response

api_bp = Blueprint('api', __name__)


@api_bp.route('/bird-response', methods=['POST'])
def bird_response():
    data = request.get_json()
    species = data.get('species')
    question = data.get('question')
    history = data.get('history', [])

    if not species or not question:
        return jsonify({'error': 'species and question are required'}), 400

    try:
        reply = get_bird_response(species, question, history)
        return jsonify({'reply': reply})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'bird did not respond', 'detail': str(e)}), 500
