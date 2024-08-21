from modules.api.gpt_client import GPTClient
from modules.data_builder import DataBuilder


if __name__ == '__main__':
    gpt_client = GPTClient()
    data_builder = DataBuilder(gpt_client.instruction)

    print("Moderation starting...")

    compliant = True

    for pair in data_builder.training_pairs:
        prompt = pair[0]
        moderation_result_0 = gpt_client.client.moderations.create(input=prompt)

        if moderation_result_0.results[0].flagged:
            print(prompt + " does violate rules!!!!!!!")
            compliant  = False
            continue

        answer = pair[1]
        moderation_result_1 = gpt_client.client.moderations.create(input=answer)

        if moderation_result_1.results[0].flagged:
            print(answer + " does violate rules!!!!!!!")
            compliant = False

    if compliant:
        print("Moderation complete. No OpenAI policy violation.")
        data_builder.save_training_data()

        gpt_client.fine_tune(data_builder.training_data)

        data_builder.archive_training()
        data_builder.rewrite_training_template()
    else:
        print("The training data violates OpenAI's policy!!!")
