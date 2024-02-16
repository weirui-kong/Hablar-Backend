import openai

openai.api_key = 'fk212238-EEbBHfkuTmu6MoheLk992jObMV3QvnIi'
openai.base_url = 'https://oa.api2d.net/v1/'


def translate(src_lang_code: str, tar_lang_code: str, text: str):
    class Result:
        result_text: str
        tokens: int

        def __init__(self, result_text, tokens):
            self.result_text = result_text
            self.tokens = tokens

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an interpreter who assists users in translating one language into another. Please remember to use more colloquial words and avoid using difficult vocabulary. Never change the real meaning.",
            },
            {
                "role": "user",
                "content": f"Translate text below from {src_lang_code} to {tar_lang_code}. Remember only reply the result: {text}",
            },
        ],
    )

    return Result(result_text=completion.choices[0].message.content, tokens=completion.usage.total_tokens)
