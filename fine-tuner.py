from modules.api.gpt_client import GPTClient
from modules.data_builder import DataBuilder


if __name__ == '__main__':
    gpt_client = GPTClient()
    data_builder = DataBuilder(gpt_client.instruction)
    data_builder.save_training_data()

    gpt_client.fine_tune(data_builder.training_data)

    data_builder.archive_training()
    data_builder.rewrite_training_template()

