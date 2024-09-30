import time
import json
from openai import OpenAI


class GPTClient:
    def __init__(self, ):
        self.instruction = "x"
        self.api_key_path = 'modules/api/api_key.txt'
        self.client = OpenAI(api_key=self.load_api_key())
        self.model = self.get_latest_model()
        self.gpt_name = 'FGPT'

    def load_api_key(self):
        with open(self.api_key_path, 'r') as file:
            api_key = file.read().strip()
        return api_key

    def get_latest_model(self):
        fine_tune_jobs = self.client.fine_tuning.jobs.list()
        fine_tune_jobs.data.sort(key=lambda x: x.created_at, reverse=True)

        fine_tuned_model = None
        for job in fine_tune_jobs.data:
            fine_tuned_model = job.fine_tuned_model
            if fine_tuned_model is not None:
                break

        if fine_tuned_model is None:
            fine_tuned_model = 'gpt-4o-2024-08-06'

        print('Retrieved model name: ' + fine_tuned_model)
        return fine_tuned_model

    def batch_query_chatgpt(self):
        batch_input_file = self.client.files.create(
          file=open("batch.jsonl", "rb"),
          purpose="batch"
        )
        batch_input_file_id = batch_input_file.id
        response = self.client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
              "description": "Annotate Subtitles"
            }
        )
        return response.id

    def retrieve_batch(self, batch_id, time_limit):
        second_counter = 0
        while True:
            batch = self.client.batches.retrieve(batch_id)

            total_requests = batch.request_counts.total
            completed_requests = batch.request_counts.completed
            failed_requests = batch.request_counts.failed

            if completed_requests + failed_requests == total_requests and total_requests > 0:
                print(f"Batch almost complete. Please wait...")
            elif total_requests == 0:
                print(f"Validating Batch...")
            else:
                print(f"Requests finished: {completed_requests}/{total_requests} (Failed: {failed_requests})")

            if failed_requests > 0:
                print(f"Some Requests Failed. Cancelling Batch.")
                self.client.batches.cancel(batch_id)
                return None
            elif batch.status == 'completed':
                print("Batch completed. Retrieving content...")
                binary_content = b""
                for chunk in self.client.files.content(batch.output_file_id).iter_bytes():
                    binary_content += chunk

                jsonl_content = binary_content.decode('utf-8')
                json_objects = []
                for line in jsonl_content.strip().split('\n'):
                    if line.strip():
                        json_objects.append(json.loads(line))

                json_objects.sort(key=lambda obj: int(obj['custom_id'].split('-')[1]))
                sorted_jsonl_content = '\n'.join(json.dumps(obj) for obj in json_objects)

                return sorted_jsonl_content

            elif batch.status == 'expired' or batch.status == 'failed' or batch.status == 'cancelled':
                print("Batch Failed.")
                return None
            elif second_counter > time_limit:
                print(f"Batch time exceeded time limit of {time_limit/60:.2f} minutes.")
                print("Cancelling Batch.")
                self.client.batches.cancel(batch_id)
                return None
            else:
                print("Batch not completed yet. Checking again in 1 second...")

            time.sleep(1)
            second_counter += 1

    def query_chatgpt(self, prompt):
        completion = self.client.chat.completions.create(
          model=self.model,
          temperature=0.0,
          messages=[
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": prompt}
          ]
        )

        return completion

    def fine_tune(self, training_data):
        training_file = self.client.files.create(
            file=open(training_data, "rb"),
            purpose="fine-tune"
        )

        self.client.fine_tuning.jobs.create(
            training_file=training_file.id,
            model=self.model,
            hyperparameters={
                "n_epochs": 5,
                "batch_size": 1,
                "learning_rate_multiplier": 2
            },
            suffix=self.gpt_name,
        )
