import os
import re


def remove_brackets(text):
    text_no_curly = re.sub(r'\{.*?\}', '', text)
    text_no_tag = re.sub(r'\<.*?\>', '', text_no_curly)
    text_no_parentheses = re.sub(r'(^|\n)\s*\(.*?\)\s*', r'\1', text_no_tag)
    text_no_full_width_parentheses = re.sub(r'(^|\n)\s*（.*?）\s*', r'\1', text_no_parentheses)

    return text_no_full_width_parentheses


class SRTLoader:
    def __init__(self, gpt_name):
        self.gpt_name = gpt_name
        self.folder_name = 'subtitles'
        self.srt_file_name = self.find_srt_file()
        self.srt_file_path = os.path.join(self.folder_name, self.srt_file_name)
        self.timestamps = []

    def find_srt_file(self):
        srt_files = os.listdir(f'./{self.folder_name}')

        for file_name in srt_files:
            if file_name.lower().endswith('.srt') and not file_name.startswith(f'{self.gpt_name}_'):
                gpt_file_name = f'{self.gpt_name}_{file_name}'
                if gpt_file_name not in srt_files:
                    return file_name
        return None

    def load_srt(self):
        with open(self.srt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        subtitles = []
        current_subtitle = []
        previous_line_was_timestamp = False

        for line in lines:
            line_content = line.strip()

            if line_content.startswith('\ufeff'):
                line_content = line_content[1:]

            if line_content.isdigit():
                if current_subtitle:
                    self.add_subtitle(current_subtitle, subtitles)
                    current_subtitle = []
                previous_line_was_timestamp = False
                continue

            if '-->' in line_content:
                self.timestamps.append(line_content)
                previous_line_was_timestamp = True
                continue

            if line_content:
                current_subtitle.append(remove_brackets(line_content))
                previous_line_was_timestamp = False
            else:
                if previous_line_was_timestamp:
                    current_subtitle.append('♬～')
                    previous_line_was_timestamp = False

        if current_subtitle:
            self.add_subtitle(current_subtitle, subtitles)
        return subtitles

    def add_subtitle(self, current_subtitle, subtitles):
        subtitle_text = ' '.join(current_subtitle)
        if all(c in ' \n' for c in subtitle_text):
            self.timestamps.pop()
        else:
            subtitles.append(subtitle_text)

    def create_new_srt(self, gpt_responses):
        print('Creating new subtitle file.')

        new_srt_content = []

        counter = 1

        for timestamp, response in zip(self.timestamps, gpt_responses):
            srt = str(counter) + '\n' + timestamp + '\n' + f'{counter}_ {response}'
            new_srt_content.append(srt)
            counter += 1

        with open(f'{self.folder_name}/{self.gpt_name}_{self.srt_file_name}', 'w', encoding='utf-8-sig') as file:
            file.write('\n\n'.join(new_srt_content))

        print('New subtitle file Created.')
