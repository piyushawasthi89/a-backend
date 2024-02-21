import requests

def call_openai_api(messages):
    # Your OpenAI API key
    api_key = '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'

    # Endpoint sourURL
    url = 'https://api.openai.com/v1/chat/completions'

    # Request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(api_key)
    }

    # Request payload
    payload = {
        'messages': messages,
        'max_tokens': 300,
        'model': 'gpt-3.5-turbo'  # Example parameter, adjust as needed
    }

    # Make the request
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print('Error:', response.status_code)
        return None