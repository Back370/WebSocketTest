import asyncio
import websockets 
import uuid
from loguru import logger
from .mylib import transcribe  #なんで.mylibでいけるのかわからない
from .mylib import compare_text
import json
from sentence_transformers import SentenceTransformer, util
import torch
connected_clients = set()



#pathを取り除いた
class ServerSide():

    def __init__(self):
        self.spells = []
        # 日本語に対応しているモデルを使用
        self.model = SentenceTransformer('hotchpotch/static-embedding-japanese', device="cuda")

    async def handle_client(self, websocket):
        # このWebSocket接続用のユニークなIDを生成
        connection_id = uuid.uuid4()
        client_address = websocket.remote_address
        client_info = f"接続元 IP: {client_address[0]}, ポート: {client_address[1]}"

        if connection_id not in connected_clients:
            # 初回接続時のみ、WebSocket IDを含むクライアント情報をログに記録し、クライアントに送信
            logger.info(f"クライアント接続: {client_info} (WebSocket ID: {connection_id})")
            connection_info_message = f"サーバーに接続しました。接続情報: {client_info}, WebSocket ID: {connection_id}"
            await websocket.send(connection_info_message)
            logger.info(f"{client_address}に接続情報を送信: {connection_info_message}")
            connected_clients.add(connection_id)

        try:
            async for message in websocket:
                logger.info(f"{client_address}からメッセージを受信 (WebSocket ID: {connection_id}): {message}")
                response = f"サーバーが受信: {message}"

                try:
                    #json形式のメッセージを受信
                    data = json.loads(message)

                        #音声をテキストに変換
                    if "KeyState" in data:   
                        In_data = data["KeyState"]
                        if isinstance(In_data, dict): #In_dataが辞書であることを確かめる
                            if In_data["Key"] == "released E key":
                                await self.transcript_text(websocket)
                                response = "Eキーが離されました"
                            if In_data["Key"] == "pressed E key":
                                self.spells = In_data["Spells"]
                                response = f"スペルリストを更新しました: {self.spells}"  
                        else:
                            response = "不正な形式のデータです"                      
                     
                except json.JSONDecodeError as e:
                    response = f"JSONデコードエラー: {str(e)}"        
                       
                #await websocket.send(response)
                logger.info(f"{client_address}に応答を送信 (WebSocket ID: {connection_id}): {response}")
        except websockets.ConnectionClosed as e:
            logger.info(f"クライアントによる接続切断: {client_info} (WebSocket ID: {connection_id}), コード: {e.code}, 理由: {e.reason}")
            connected_clients.remove(connection_id)

        logger.info(f"クライアント切断: {client_info} (WebSocket ID: {connection_id})")

    #音声をテキストに変換
    async def transcript_text(self, websocket):
        transcriptions = transcribe.move_wav_files(transcribe.source_folder, transcribe.destination_folder)
        if(transcriptions):
            if(self.spells != []):
                #テキストどうしの類似度を計算する
                max_similarity_spell = await self.compare_text(' '.join(transcriptions), self.spells)
                print(f"変換結果: {' '.join(max_similarity_spell)}")
                Converted_Text = f"テキストを送信:{' '.join( max_similarity_spell)}"
            else:
                print("スペルリストが空です")    
                Converted_Text = "テキストを送信: スペルリストが空です"
        else:
            Converted_Text = "テキストを送信: 変換結果がありません"    
        await websocket.send(Converted_Text) #変換したテキストを送信

    #テキストどうしの類似度を計算する
    async def compare_text(self, DoneText, Spells):
        SimilarityList = []
        tasks = []
        for spell in Spells:
            task = asyncio.create_task(compare_text.compare_text(self, DoneText, spell, ))
            tasks.append(task)

        similaritys = await asyncio.gather(*tasks)
        for spell, similarity in similaritys:
            SimilarityList.append((spell, similarity))
            print(f"スペル: {spell}, 類似度: {similarity}")
        return max(SimilarityList, key=lambda x: x[1])[0] #類似度が最大のスペルを返す
      
async def start_server():
    serverside = ServerSide()
    server = await websockets.serve(serverside.handle_client, "localhost", 8080)
    logger.info("WebSocketサーバーを ws://localhost:8080 で起動")
    await server.wait_closed()     

if __name__ == "__main__":
    logger.add("websocket_server.log", rotation="1 MB", retention="7 days")
    asyncio.run(start_server())