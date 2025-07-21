import requests

def ask_llama(prompt, api_key, is_json=False):
    """
    Sends a prompt to the LLaMA model using a provided API key.
    If is_json is True, it will ask the model to format the output as JSON.
    """
    TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        final_prompt = prompt
        if is_json:
            final_prompt += "\n\nIMPORTANT: Please provide the response in a valid JSON format only, without any explanatory text before or after the JSON block."

        data = {
            "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "messages": [
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }

        if is_json:
            data["response_format"] = {"type": "json_object"}

        response = requests.post(TOGETHER_API_URL, headers=HEADERS, json=data)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ Failed to get a response: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Exception occurred: {str(e)}"