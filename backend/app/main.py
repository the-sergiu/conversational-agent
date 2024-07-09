import base64
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

load_dotenv()
app = FastAPI()

root_dir = Path(__file__).parent.parent.parent
frontend_path = root_dir / "frontend"
app.mount("/static", StaticFiles(directory=frontend_path), name="static")
audio_path = root_dir / "audio_files"


client = OpenAI(
    organization=os.environ.get("organization"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Mark start of app as ground truth and compare relative to each chunk
start_time = time.time()
message_queue = []

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, text: str, websocket: WebSocket):
        await websocket.send_text(text)
    
    async def get_active_connection(self):
        print(self.active_connections[0])
        await self.active_connections[0].accept()
        return self.active_connections[0]


manager = ConnectionManager()



# @app.post("/text-to-speech")
# async def text_to_speech(text: str):
#     # Convert text to speech using OpenAI's TTS API
#     # This is a hypothetical function, replace with actual API call
#     audio_stream = client.text_to_speech.synthesize(text)
#     return StreamingResponse(audio_stream, media_type="audio/wav")

@app.websocket("/ws")
async def test_file(websocket: WebSocket):
     print("HEERE")
     await manager.connect(websocket)
     raw_data = await websocket.receive_text()
     file_content = base64.b64decode(raw_data)
     with open(audio_path / "temp_audio.wav", "wb") as f:
        f.write(file_content.decode("utf-8"))


@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), audio_path: Path = audio_path):
    # Save the file temporarily
    with open(audio_path / "temp_audio.wav", "wb") as f:
        f.write(await file.read())

    audio_file = open(audio_path / "temp_audio.wav", "rb")
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        # response_format="verbose_json",
        # timestamp_granularities=["segment"]
    )

    res = call_open_api(transcript.text)
   # websocket = manager.active_connections[0]

    try:
        collected_chunks = []
        collected_messages = []
        # iterate through the stream of events
        for chunk in res:
            chunk_time = (
                time.time() - start_time
            )  # calculate the time delay of the chunk
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk.choices[
                0
            ].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message

            if chunk_message is not None and chunk_message.find(".") != -1:
                print("Found full stop")
                message = [m for m in collected_messages if m is not None]
                full_reply_content = "".join([m for m in message])

                #await manager.send_text(full_reply_content, websocket)
                message_queue.append(full_reply_content)
                collected_messages = []

            print(
                f"Message received {chunk_time:.2f} seconds after request: {chunk_message}"
            )  # print the delay and text

        if len(collected_messages) > 0:
            message = [m for m in collected_messages if m is not None]
            full_reply_content = "".join([m for m in message])

            #await manager.send_text(full_reply_content, websocket)
            message_queue.append(full_reply_content)
            collected_messages = []

    except WebSocketDisconnect:
        print("DISCONECTING WEBSOCKET")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {str(e)}")

    return {"transcript": transcript.text}


def call_open_api(message):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a assistance named Bluu , A asistance from scalebuildAI , you help people to find the best product for them , Scalebuild is a software company",
            },
            # add 10 last messages history here
            {"role": "user", "content": message},
        ],
        temperature=0,
        stream=True,  # again, we set stream=True
    )
    # create variables to collect the stream of chunks
    return completion

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket) await manager.connect(websocket)
#     try:
#         while True:
#             try:
#                 # Receive text data (speech recognition result) from the client
#                 data = await websocket.receive_text()

#                 # Process the data
#                 print(f"Received text: {data}")  # Example: print it to the console
#                 res = call_open_api(data)
#                 # Optionally, send a response back to the client
#                 collected_chunks = []
#                 collected_messages = []
#                 # iterate through the stream of events
#                 for chunk in res:
#                     chunk_time = (
#                         time.time() - start_time
#                     )  # calculate the time delay of the chunk
#                     collected_chunks.append(chunk)  # save the event response
#                     chunk_message = chunk.choices[
#                         0
#                     ].delta.content  # extract the message
#                     collected_messages.append(chunk_message)  # save the message

#                     if chunk_message is not None and chunk_message.find(".") != -1:
#                         print("Found full stop")
#                         message = [m for m in collected_messages if m is not None]
#                         full_reply_content = "".join([m for m in message])

#                         await manager.send_text(full_reply_content, websocket)
#                         collected_messages = []

#                     print(
#                         f"Message received {chunk_time:.2f} seconds after request: {chunk_message}"
#                     )  # print the delay and text

#                 if len(collected_messages) > 0:
#                     message = [m for m in collected_messages if m is not None]
#                     full_reply_content = "".join([m for m in message])

#                     await manager.send_text(full_reply_content, websocket)
#                     collected_messages = []

#             except WebSocketDisconnect:
#                 manager.disconnect(websocket)
#                 break
#             except Exception as e:
#                 print(f"Error: {str(e)}")
#                 break
#     finally:
#         manager.disconnect(websocket)

#the connection closes once the request is completed. 
# @app.websocket("/ws")
# async def create_websocket_connection(websocket: WebSocket):
#     await manager.connect(websocket)
#     while True:
#             if message_queue.count > 0:
#                 message = message_queue.pop()
#                 print("MESSAGE" + message)
#                 #manager.send_text(message, websocket)
#                 break


@app.get("/")
async def get():
    # return FileResponse("voice_frontend_new.html")
    html_file_path = frontend_path / "index.html"
    return FileResponse(html_file_path)
