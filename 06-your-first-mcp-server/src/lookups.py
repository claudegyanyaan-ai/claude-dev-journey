"""Network fetch + pure formatting logic for the dictionary MCP server.

Kept separate from server.py so the formatting functions can be unit
tested without making real HTTP calls.
"""

import time

import requests


def _get_with_retry(url, params=None):
    """GET url with params, retrying up to 3 times (1 second apart) on
    actual network/connection errors only. Returns the requests.Response
    object on any completed request (even a 404 counts as "completed" -
    the server responded, it just said "not found"), or None if every
    attempt raised a network error.

    Deciding whether a completed response counts as success or failure
    is left to the caller - this helper only handles the transient,
    "couldn't even reach the server" case.
    """
    for attempt in range(3):
        try:
            return requests.get(url, params=params, timeout=10)
        except requests.exceptions.RequestException:
            pass
        if attempt < 2:
            time.sleep(1)
    return None


DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
TRANSLATION_URL = "https://api.mymemory.translated.net/get"


def fetch_english_definition(word):
    """Look up an English word's definition. Returns the parsed JSON on
    success, or None if the word wasn't found (404, not retried - a 404
    is the server correctly saying "no such word", not a glitch) or the
    network failed after 3 retries."""
    response = _get_with_retry(DICTIONARY_URL.format(word))
    if response is None:
        return None
    if response.status_code == 404:
        return None
    return response.json()


def fetch_hindi_translation(word):
    """Translate an English word to Hindi. Returns the parsed JSON on
    success, or None if the network failed after 3 retries, or the API
    itself reports the translation as unavailable (responseStatus != 200
    inside a normal 200 HTTP response - this API doesn't 404, so this is
    the only way it signals "bad answer")."""
    response = _get_with_retry(TRANSLATION_URL, {"q": word, "langpair": "en|hi"})
    if response is None:
        return None
    data = response.json()
    if data.get("responseStatus") != 200:
        return None
    return data


def format_definition(data):
    """Turn dictionaryapi.dev's response (a list of entries) into a
    short readable string with up to 2 "part of speech: definition"
    lines. Pure - no network, no I/O - so it's testable with fake JSON."""
    if not data:
        return "No definition found for this word."

    meanings = data[0].get("meanings", [])
    lines = []
    for meaning in meanings:
        definitions = meaning.get("definitions", [])
        if not definitions:
            continue
        part_of_speech = meaning.get("partOfSpeech", "unknown")
        first_definition = definitions[0].get("definition", "")
        lines.append(f"{part_of_speech}: {first_definition}")
        if len(lines) == 2:
            break

    if not lines:
        return "No definition found for this word."
    return " | ".join(lines)


def format_translation(data):
    """Turn mymemory.translated.net's response into the translated
    string. Pure - no network, no I/O - so it's testable with fake JSON."""
    if not data:
        return "Translation unavailable."
    translated = data.get("responseData", {}).get("translatedText", "")
    if not translated:
        return "Translation unavailable."
    return translated
