import os
import shutil
import whisper
import torch
import pykakasi  # ひらがな変換用ライブラリ

# GPUが利用可能かどうかを確認し、利用可能であればGPUを使用
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = whisper.load_model("base",  device=device)

source_folder = "C:\\Users\\a7p7p\\Downloads\\UETestWavFile"
destination_folder = "C:\\Users\\a7p7p\\Downloads\\WebSocketTest\\UEPythonRecoProject\\MyPackage\\TestWavFiles"


# ひらがな変換用の関数
def convert_to_hiragana(text):
    kakasi = pykakasi.kakasi()
    kakasi.setMode("K", "H")  # カタカナをひらがなに変換
    kakasi.setMode("J", "H")  # 漢字をひらがなに変換
    converter = kakasi.getConverter()
    return converter.do(text)
    
def move_wav_files(source_folder, destination_folder):
    transcriptions = []
    try:
        # 移動先フォルダが存在しない場合は作成
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # 移動元フォルダ内のファイル一覧を取得し、更新日時でソート
        files = os.listdir(source_folder)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(source_folder, x)))
        

        # .wavファイルを見つけて移動
        for file in files:
            if file.endswith(".wav"):
                source_file = os.path.join(source_folder, file)
                destination_file = os.path.join(destination_folder, file)
                try:
                    shutil.move(source_file, destination_file)

                    # 音声ファイルを文字変換
                    print(f"Transcribing {destination_file}")
                    transcript = model.transcribe(destination_file, language="ja")
                    transcription = str(transcript["text"])
                    print("Original Transcription:", transcription)

                    # ひらがなに変換
                    hiragana_transcription = convert_to_hiragana(transcription)
                    print("Hiragana Transcription:", hiragana_transcription)
                    
                    transcriptions.append(transcription)
                    
                except Exception as e:
                    print(f"Error moving {file}: {str(e)}. Skipping.")
                    transcriptions.append(None)

        print("File moving completed.")
        return transcriptions

    except Exception as e:
        print("An error occurred:", str(e))
        return None

if __name__ == "__main__":
    move_wav_files(source_folder, destination_folder)