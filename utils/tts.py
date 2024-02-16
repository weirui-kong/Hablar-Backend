'''
  For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk
'''
import base64
import os
import time
import datetime

import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment

# Creates an instance of a speech config with specified subscription key and service region.
speech_key = "97cc09f8bba54d12b5fc4d30f07910ff"
service_region = "eastasia"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)


# Note: the voice setting will not overwrite the voice element in input SSML.

def request_speech(key_id, voice_code: str, content: str) -> str:
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3)
    speech_config.speech_synthesis_voice_name = voice_code
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = speech_synthesizer.speak_text_async(content).get()
    stream = speechsdk.AudioDataStream(result)

    folder_path = '../saved_audio'
    if not os.path.exists(folder_path):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(folder_path)

    file_path = f'./saved_audio/{key_id}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.mp3'
    stream.save_to_wav_file(file_path)
    return file_path


def encode_audio_to_base64(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            # 读取音频文件内容
            audio_content = audio_file.read()

            # 使用base64编码
            base64_encoded = base64.b64encode(audio_content).decode('utf-8')

            return base64_encoded

    except FileNotFoundError:
        return None  # 文件不存在的处理，你可以根据需要进行调整
    
if __name__ == '__main__':
    file = request_speech(1, 'ja-JP-KeitaNeural', '大阪旅行のプランニングの参考に！定番から穴場、最新スポット、話題のグルメまで、大阪のおすすめ観光スポットをエリア別に紹介します。')
    print(file)