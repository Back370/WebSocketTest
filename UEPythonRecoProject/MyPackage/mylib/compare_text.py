from sentence_transformers import SentenceTransformer, util
import torch
import warnings
import asyncio
warnings.filterwarnings("ignore", category=UserWarning)

# text1 = "赤"
# text2 = "青"

async def compare_text(self, text1, text2):

    
    # モデルがどのデバイスを使用しているか確認
    print(f"Model is using device: {self.model.device}")

    # テキストをエンコードしてPytorchのテンソルに変換
    maintext = self.model.encode(text1, convert_to_tensor=True)
    subtext = self.model.encode(text2, convert_to_tensor=True)
    
    # エンコードされたテンソルがどのデバイスに配置されているか確認
    # print(f"Main text tensor is on device: {maintext.device}")
    # print(f"Sub text tensor is on device: {subtext.device}")

    cosine_score = util.pytorch_cos_sim(maintext, subtext)[0][0]
    return text2, cosine_score

#print(compare_text(text1, text2))