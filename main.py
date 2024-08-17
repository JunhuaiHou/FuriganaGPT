from openai import OpenAI
from modules.srt_loader import SRTLoader
from modules.api.gpt_client import get_latest_model, prepare_batch_requests, load_api_key, batch_query_chatgpt, retrieve_batch, gpt_name, query_chatgpt
import time
import json
from multiprocessing import Process, Queue


def write_requests_to_file(requests, filename):
    print('Creating batch file.')
    with open(filename, 'w') as f:
        for request in requests:
            f.write(json.dumps(request) + '\n')


def process_subtitles(subtitles, start, model, client):
    responses = []
    for idx, subtitle in enumerate(subtitles, start=start):
        response = query_chatgpt(client, subtitle, model)
        content = response.choices[0].message.content
        responses.append(content)
        print(f'Request completed for subtitle {idx}')
    return responses


def get_responses(client, subtitles):
    start_time = time.time()
    time_limit = 300

    print('Preparing requests.')
    requests = prepare_batch_requests(subtitles, client)
    print('Requests prepared.')
    write_requests_to_file(requests, 'batch.jsonl')
    print('Batch file created.')
    #id = batch_query_chatgpt(client)
    print('Batch file uploaded to OpenAI server.')
    batch_response = None#retrieve_batch(client, id, time_limit)

    gpt_responses = []
    if batch_response is None:
        print('Batch Generation has Failed to deliver within the Time Limit.')
        print('Sequential Generation Starting...')
        start_time = time.time()
        model = get_latest_model(client)
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

        gpt_responses = process_subtitles(subtitles, mid_point+1, model, client)

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


def create_new_srt(input_file_path, output_file_path, gpt_responses):
    print('Creating new subtitle file.')
    srt_contents = load_full_srt(input_file_path)
    new_srt_content = []

    counter = 1

    for original, response in zip(srt_contents, gpt_responses):
        first_two_lines, remaining_lines = original.split('\n', 2)[:2], original.split('\n', 2)[2:]
        if not response.endswith('\n'):
            response += '\n'

        new_srt_content.append('\n'.join(first_two_lines) + '\n' + f'{counter}_ {response}')
        counter += 1
    with open(output_file_path, 'w', encoding='utf-8-sig') as file:
        file.write('\n'.join(new_srt_content))
    print('New subtitle file Created.')


if __name__ == '__main__':
    debug = False

    if debug:
        api_key = 'invalid_key'
    else:
        api_key = load_api_key()

    client = OpenAI(api_key=api_key)
    srt_loader = SRTLoader(gpt_name)
    if srt_loader.srt_file_path:
        srt_text = srt_loader.load_srt()
        print(f'Loaded subtitle file name {srt_loader.srt_file_name}')
        responses = get_responses(client, srt_text)
        srt_loader.create_new_srt(responses)
    else:
        print("No SRT file found in the current directory.")