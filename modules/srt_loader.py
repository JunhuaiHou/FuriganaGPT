import os


class SRTLoader:
    def __init__(self, gpt_name):
        self.gpt_name = gpt_name
        self.srt_file_name = self.find_srt_file()
        self.srt_file_path = os.path.join('subtitles', self.srt_file_name)

    def find_srt_file(self):
        srt_files = os.listdir('./subtitles')

        for file_name in srt_files:
            if file_name.lower().endswith('.srt') and not file_name.startswith(f'{self.gpt_name}_'):
                gpt_file_name = f'{self.gpt_name}_{file_name}'
                if gpt_file_name not in srt_files:
                    return file_name
        return None

    def load_srt(self):
        with open(self.srt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        text = []
        current_subtitle = []
        previous_line_was_timestamp = False

        for line in lines:
            line_content = line.strip()

            if line_content.startswith('\ufeff'):
                line_content = line_content[1:]

            if line_content.isdigit():
                if current_subtitle:
                    text.append(' '.join(current_subtitle))
                    current_subtitle = []
                previous_line_was_timestamp = False
                continue

            if '-->' in line_content:
                previous_line_was_timestamp = True
                continue

            if line_content:
                current_subtitle.append(line_content)
                previous_line_was_timestamp = False
            else:
                if previous_line_was_timestamp:
                    current_subtitle.append('♬～')
                    previous_line_was_timestamp = False

        if current_subtitle:
            text.append(' '.join(current_subtitle))
        return text

    def load_full_srt(self):
        with open(self.srt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        text = []
        current_subtitle = []
        for line in lines:
            line_content = line.strip()
            if line_content.startswith('\ufeff'):
                line_content = line_content[1:]

            if line_content.isdigit() and current_subtitle:
                text.append('\n'.join(current_subtitle))
                current_subtitle = [line_content]
            else:
                current_subtitle.append(line_content)

        if current_subtitle:
            text.append('\n'.join(current_subtitle))

        return text

    def create_new_srt(self, gpt_responses):
        print('Creating new subtitle file.')
        srt_contents = self.load_full_srt()
        new_srt_content = []

        counter = 1

        for original, response in zip(srt_contents, gpt_responses):
            first_two_lines, remaining_lines = original.split('\n', 2)[:2], original.split('\n', 2)[2:]
            if not response.endswith('\n'):
                response += '\n'

            new_srt_content.append('\n'.join(first_two_lines) + '\n' + f'{counter}_ {response}')
            counter += 1

        with open(f'subtitles/{self.gpt_name}_{self.srt_file_name}', 'w', encoding='utf-8-sig') as file:
            file.write('\n'.join(new_srt_content))

        print('New subtitle file Created.')
