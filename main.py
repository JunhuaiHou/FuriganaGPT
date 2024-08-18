from modules.srt_loader import SRTLoader
from modules.gpt_generator import GPTGenerator
from modules.api.gpt_client import remove_brackets

if __name__ == '__main__':
    # raw_instruction = 'x'
    # gpt_generator = GPTGenerator()
    # srt_loader = SRTLoader(gpt_generator.gpt_name)
    # if srt_loader.srt_file_path:
    #     srt_text = srt_loader.load_srt()
    #     print(f'Loaded subtitle file name {srt_loader.srt_file_name}')
    #     responses = gpt_generator.get_responses(srt_text)
    #     srt_loader.create_new_srt(responses)
    # else:
    #     print("No SRT file found in the current directory.")

    print(remove_brackets( "（メカ丸機内音声）術式装填(そうてん)" ))

