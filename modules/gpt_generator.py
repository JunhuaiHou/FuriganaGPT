import json
from modules.api.gpt_client import GPTClient, remove_brackets
import time
import threading


class GPTGenerator:
    def __init__(self):
        self.gpt_client = GPTClient()
        self.subs1, self.subs2 = [], []
        self.counter = self.SharedCounter(0)
        self.gpt_name = self.gpt_client.client
        self.batch_file_name = 'batch.jsonl'

    def process_subtitles(self, subtitles, start, results, index, len_total_subs):
        responses = []

        for idx, subtitle in enumerate(subtitles, start=start):
            response = self.gpt_client.query_chatgpt(subtitle)
            content = response.choices[0].message.content
            responses.append(content)
            counter = self.counter.increment()
            print(f'Request completed for subtitle {idx}. {counter}/{len_total_subs} subtitles completed.')

        results[index] = responses

        return responses

    def create_batch_file(self, requests):
        print('Creating batch file.')
        with open(self.batch_file_name, 'w') as f:
            for request in requests:
                f.write(json.dumps(request) + '\n')

    def prepare_batch_requests(self, srt_text):
        requests = []
        for i, text in enumerate(srt_text):
            clean_text = remove_brackets(text)
            request = {
                "custom_id": f"request-{i+1}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.gpt_client.model,
                    "temperature": 0.0,
                    "messages": [
                        {"role": "system", "content": self.gpt_client.instruction},
                        {"role": "user", "content": clean_text}
                    ],
                    "max_tokens": 1000
                }
            }
            requests.append(request)
        return requests

    def get_responses(self, subtitles):
        start_time = time.time()
        time_limit = 300

        print('Preparing requests.')
        requests = self.prepare_batch_requests(subtitles)
        print('Requests prepared.')
        self.create_batch_file(requests)
        print('Batch file created.')
        batch_id = self.gpt_client.batch_query_chatgpt()
        print('Batch file uploaded to OpenAI server.')
        batch_response = self.gpt_client.retrieve_batch(batch_id, time_limit)

        gpt_responses = []
        if batch_response is None:
            print('Batch Generation has Failed to deliver within the time limit.')
            print('Sequential Generation Starting...')
            start_time = time.time()
            len_total_subs = len(subtitles)
            quarter_point = len_total_subs // 4
            results = [[] for _ in range(4)]

            subs_parts = [
                subtitles[:quarter_point],
                subtitles[quarter_point:quarter_point * 2],
                subtitles[quarter_point * 2:quarter_point * 3],
                subtitles[quarter_point * 3:]
            ]

            threads = []

            for i in range(4):
                thread = threading.Thread(
                    target=self.process_subtitles,
                    args=(subs_parts[i], i * quarter_point + 1, results, i, len_total_subs)
                )
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            gpt_responses = results[0] + results[1] + results[2] + results[3]

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

    class SharedCounter:
        def __init__(self, initial=0):
            self.value = initial
            self._lock = threading.Lock()

        def increment(self):
            with self._lock:
                self.value += 1
            return self.value
