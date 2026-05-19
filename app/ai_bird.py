import json
import os
import anthropic

_client = None
_species_roster = None

SPECIES_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'species', 'species-config.json')


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
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
    Calls Claude with the species system prompt and returns the bird's reply.

    history is a list of prior {role, content} message dicts so the bird
    remembers what it already said this session.
    """
    if history is None:
        history = []

    species = load_species(species_name)
    client = _get_client()

    messages = history + [{'role': 'user', 'content': question}]

    response = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=300,
        system=species['system-prompt'],
        messages=messages,
    )

    return response.content[0].text


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
