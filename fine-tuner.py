from modules.api.gpt_client import GPTClient
from modules.data_builder import DataBuilder
from modules.moderator import Moderator


def has_content(list_of_lists):
    return any(sublist for sublist in list_of_lists)


if __name__ == '__main__':
    gpt_client = GPTClient()
    data_builder = DataBuilder(gpt_client.instruction)
    moderator = Moderator(gpt_client)

    print("Moderation starting...")
    violations = moderator.get_violations(data_builder.training_pairs)

    if has_content(violations):
        print("The following training data violates OpenAI's policy!!!!!")
        for violation in violations:
            print('------------------------------------')
            print(violation)

    else:
        print("Moderation complete. No OpenAI policy violation.")

        data_builder.save_training_data()

        gpt_client.fine_tune(data_builder.training_data)

        data_builder.archive_training()
        data_builder.rewrite_training_template()
