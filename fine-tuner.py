from modules.api.gpt_client import GPTClient
from modules.data_builder import DataBuilder
import threading


def has_content(list_of_lists):
    return any(sublist for sublist in list_of_lists)


def moderate(pairs, results, index):
    violations = []
    for pair in pairs:
        prompt = pair[0]
        moderation_result_0 = gpt_client.client.moderations.create(input=prompt)

        if moderation_result_0.results[0].flagged:
            violations.append(prompt)
            continue

        answer = pair[1]
        moderation_result_1 = gpt_client.client.moderations.create(input=answer)

        if moderation_result_1.results[0].flagged:
            violations.append(answer)

    results[index] = violations


if __name__ == '__main__':
    gpt_client = GPTClient()
    data_builder = DataBuilder(gpt_client.instruction)

    print("Moderation starting...")

    len_total_training_pairs = len(data_builder.training_pairs)
    quarter_point = len_total_training_pairs // 4
    results = [[] for _ in range(4)]

    pairs_parts = [
        data_builder.training_pairs[:quarter_point],
        data_builder.training_pairs[quarter_point:quarter_point * 2],
        data_builder.training_pairs[quarter_point * 2:quarter_point * 3],
        data_builder.training_pairs[quarter_point * 3:]
    ]

    threads = []

    for i in range(4):
        thread = threading.Thread(
            target=moderate,
            args=(pairs_parts[i], results, i)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    violations = results[0] + results[1] + results[2] + results[3]

    if has_content(violations):
        print("The following training data violates OpenAI's policy!!!!!")
        for item in violations:
            print('------------------------------------')
            print(item)

    else:
        print("Moderation complete. No OpenAI policy violation.")

        data_builder.save_training_data()

        gpt_client.fine_tune(data_builder.training_data)

        data_builder.archive_training()
        data_builder.rewrite_training_template()
