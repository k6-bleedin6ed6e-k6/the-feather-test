import json
import os
from groq import Groq

_client = None
_species_roster = None

SPECIES_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'species', 'species-config.json')


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    return _client


def _get_roster():
    global _species_roster
    if _species_roster is None:
        with open(SPECIES_CONFIG_PATH) as f:
            _species_roster = json.load(f)
    return _species_roster


def load_species(species_name):
    roster = _get_roster()
    species = roster.get(species_name)
    if not species:
        raise ValueError(f'unknown species: {species_name}')
    return species


def get_bird_response(species_name, question, history=None):
    """
    Calls Groq (llama-3.1-8b-instant) with the species system prompt and returns the bird's reply.

    history is a list of prior {role, content} message dicts so the bird
    remembers what it already said this session.
    """
    if history is None:
        history = []

    species = load_species(species_name)
    client = _get_client()

    messages = [{'role': 'system', 'content': species['system-prompt']}] + history + [{'role': 'user', 'content': question}]

    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        max_tokens=300,
        messages=messages,
    )

    return response.choices[0].message.content


def list_species():
    roster = _get_roster()
    return [
        {
            'id': key,
            'name': val['name'],
            'scientific-name': val['scientific-name'],
            'personality': val['personality'],
        }
        for key, val in roster.items()
    ]
