import json
from modules.api.gpt_client import GPTClient
import time
import threading


class GPTGenerator:
    def __init__(self):
        self.gpt_client = GPTClient()
        self.subs1, self.subs2 = [], []

    def process_subtitles(self, subtitles, start, results, index):
        responses = []

        for idx, subtitle in enumerate(subtitles, start=start):
            response = self.gpt_client.query_chatgpt(subtitle)
            content = response.choices[0].message.content
            responses.append(content)
            print(f'Request completed for subtitle {idx}')

        results[index] = responses

        return responses

    def create_batch_file(self, requests, filename):
        print('Creating batch file.')
        with open(filename, 'w') as f:
            for request in requests:
                f.write(json.dumps(request) + '\n')

    def get_responses(self, subtitles):
        start_time = time.time()
        time_limit = 300

        print('Preparing requests.')
        requests = self.gpt_client.prepare_batch_requests(subtitles)
        print('Requests prepared.')
        self.create_batch_file(requests, 'batch.jsonl')
        print('Batch file created.')
        batch_id = self.gpt_client.batch_query_chatgpt()
        print('Batch file uploaded to OpenAI server.')
        batch_response = self.gpt_client.retrieve_batch(batch_id, time_limit)

        gpt_responses = []
        if batch_response is None:
            print('Batch Generation has Failed to deliver within the Time Limit.')
            print('Sequential Generation Starting...')
            start_time = time.time()
            total_subtitles = len(subtitles)
            mid_point = total_subtitles // 2
            results = [[], []]
            subs1 = subtitles[:mid_point]
            subs2 = subtitles[mid_point:]

            thread1 = threading.Thread(target=self.process_subtitles, args=(subs1, 1, results, 0))
            thread2 = threading.Thread(target=self.process_subtitles, args=(subs2, mid_point + 1, results, 1))
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
            gpt_responses = results[0] + results[1]

            end_time = time.time()
            duration = end_time - start_time
            minutes, seconds = divmod(duration, 60)
            print(f'Sequential Generation Successful. Duration: {int(minutes)} minutes {seconds:.2f} seconds')
            return gpt_responses
        else:
            for line in batch_response.strip().split('\n'):
                if line.strip():
                    data = json.loads(line)
                    content = data['response']['body']['choices'][0]['message']['content']
                    gpt_responses.append(content)

            end_time = time.time()
            duration = end_time - start_time
            minutes, seconds = divmod(duration, 60)
            print(f'Batch Generation Successful. Duration: {int(minutes)} minutes {seconds:.2f} seconds')
            return gpt_responses
