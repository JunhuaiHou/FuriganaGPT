import json
from modules.api.gpt_client import GPTClient
import time
from multiprocessing import Process, Queue


class GPTGenerator:
    def __init__(self):
        self.gpt_client = GPTClient()

    def process_subtitles(self, subtitles, start):
        responses = []
        for idx, subtitle in enumerate(subtitles, start=start):
            response = self.gpt_client.query_chatgpt(subtitle)
            content = response.choices[0].message.content
            responses.append(content)
            print(f'Request completed for subtitle {idx}')
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
        # id = batch_query_chatgpt(client)
        print('Batch file uploaded to OpenAI server.')
        batch_response = None  # retrieve_batch(client, id, time_limit)

        gpt_responses = []
        if batch_response is None:
            print('Batch Generation has Failed to deliver within the Time Limit.')
            print('Sequential Generation Starting...')
            start_time = time.time()
            total_subtitles = len(subtitles)
            mid_point = total_subtitles // 2

            # result_queue = Queue()
            # subs1 = subtitles[:mid_point]
            # subs2 = subtitles[mid_point:]
            # p1 = Process(target=process_subtitles, args=(subs1, 1, model))
            # p2 = Process(target=process_subtitles, args=(subs2, mid_point+1, model))
            # p1.start()
            # p2.start()
            # p1.join()
            # p2.join()
            #
            # gpt_responses = result_queue.get() + result_queue.get()

            gpt_responses = self.process_subtitles(subtitles, mid_point + 1)

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
