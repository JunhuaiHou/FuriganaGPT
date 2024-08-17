from modules.srt_loader import SRTLoader
from modules.api.gpt_client import GPTClient
import time
import json
from multiprocessing import Process, Queue


def process_subtitles(subtitles, start, gpt_client):
    responses = []
    for idx, subtitle in enumerate(subtitles, start=start):
        response = gpt_client.query_chatgpt(subtitle)
        content = response.choices[0].message.content
        responses.append(content)
        print(f'Request completed for subtitle {idx}')
    return responses

def create_batch_file(self, requests, filename):
        print('Creating batch file.')
        with open(filename, 'w') as f:
            for request in requests:
                f.write(json.dumps(request) + '\n')

def get_responses(gpt_client, subtitles):
    start_time = time.time()
    time_limit = 300

    print('Preparing requests.')
    requests = gpt_client.prepare_batch_requests(subtitles)
    print('Requests prepared.')
    #gpt_client.create_batch(requests, 'batch.jsonl')
    print('Batch file created.')
    #id = batch_query_chatgpt(client)
    print('Batch file uploaded to OpenAI server.')
    batch_response = None#retrieve_batch(client, id, time_limit)

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

        gpt_responses = process_subtitles(subtitles, mid_point+1, gpt_client)

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


if __name__ == '__main__':
    gpt_name = 'FGPT'
    raw_instruction = """x"""
    gpt_client = GPTClient()
    srt_loader = SRTLoader(gpt_name)
    if srt_loader.srt_file_path:
        srt_text = srt_loader.load_srt()
        print(f'Loaded subtitle file name {srt_loader.srt_file_name}')
        responses = get_responses(gpt_client, srt_text)
        srt_loader.create_new_srt(responses)
    else:
        print("No SRT file found in the current directory.")