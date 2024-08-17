import json


class GPTGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=api_key)

    def process_subtitles(self, subtitles, start, model, client):
        responses = []
        for idx, subtitle in enumerate(subtitles, start=start):
            response = query_chatgpt(client, subtitle, model)
            content = response.choices[0].message.content
            responses.append(content)
            print(f'Request completed for subtitle {idx}')
        return responses

    def create_batch_file(self, requests, filename):
        print('Creating batch file.')
        with open(filename, 'w') as f:
            for request in requests:
                f.write(json.dumps(request) + '\n')