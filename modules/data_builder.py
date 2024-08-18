import yaml
import json


class DataBuilder:
    def __init__(self, instruction):
        self.instruction = instruction
        self.training_translation = 'data/training_translation.yaml'
        self.archive_path = 'data/archive/training_archive.yaml'
        self.training_data = 'data/training_data.jsonl'
        self.template_path = 'data/archive/template.yaml'
        self.training_pairs = self.extract_training_pairs()

    def extract_training_pairs(self):
        translation_pairs = []
        try:
            with open(self.training_translation, 'r', encoding='utf-8') as file:
                loaded_pairs = yaml.safe_load(file)

                for pair in loaded_pairs:
                    japanese = pair.get('prompt', 'Prompt not found')
                    english = pair.get('answer', 'Answer not found')

                    translation_pairs.append((japanese, english))
        except FileNotFoundError:
            print(f"The file {self.training_translation} was not found.")
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return translation_pairs

    def format_fine_tune_data(self, prompt, answer):
        return {
            "messages": [
                {"role": "system", "content": self.instruction},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer}
            ]
        }

    def save_training_data(self):
        with open(self.training_data, 'w') as file:
            for index, (question, answer) in enumerate(self.training_pairs):
                formatted_translation = self.format_fine_tune_data(question, answer)
                json.dump(formatted_translation, file)
                file.write('\n')

    def archive_training(self):
        with open(self.training_translation, 'r', encoding='utf-8') as src_file:
            src_contents = src_file.read()

        while src_contents.endswith('\n'):
            src_contents = src_contents.rstrip()

        with open(self.archive_path, 'a', encoding='utf-8') as dst_file:
            dst_file.write("\n\n" + src_contents)

    def rewrite_training_template(self):
        with open(self.template_path, 'r', encoding='utf-8') as src_file:
            src_contents = src_file.read()

        while src_contents.endswith('\n'):
            src_contents = src_contents.rstrip()

        with open(self.training_translation, 'w', encoding='utf-8') as dst_file:
            dst_file.write(src_contents)
