from modules.api.gpt_client import GPTClient
from modules.data_builder import DataBuilder
from modules.moderator import Moderator


if __name__ == '__main__':
    gpt_client = GPTClient()
    data_builder = DataBuilder(gpt_client.instruction)
    moderator = Moderator(gpt_client)

    print("Moderation starting...")
    moderation_results = moderator.get_violations(data_builder.training_pairs)
    violations = []
    highest_score = 0, ''

    for result in moderation_results:
        text, flagged, score = result

        if flagged:
            violations.append(text)

        if score > highest_score[0]:
            highest_score = score, text

    if violations:
        print("The following training data violates OpenAI's policy!!!!!")
        for violation in violations:
            print('------------------------------------')
            print(violation)

    else:
        print("Moderation complete. No OpenAI policy violation.")
        print("The following training data has the highest score:")
        print(highest_score[1])

        data_builder.save_training_data()
        gpt_client.fine_tune(data_builder.training_data)

        data_builder.archive_training()
        data_builder.rewrite_training_template()
