# # wss://api.cartesia.ai/tts/websocket

# """
# /send:
# - context_id: UUID
# - model_id: id of model to use
# - output_format: opt. Raw, WAV, MP3
# - transcript
# - voice: id, embedding
# - language: 1 of 15
# """
# import reflex as rx
# import base64
# import websocket
# import json
# import os
# import uuid
# import asyncio
# from dotenv import load_dotenv
# from openai import AsyncOpenAI

# load_dotenv()

# class State(rx.State):

#     transcript: str = ""
#     language: str = "English"

#     is_loading: bool = False
#     audio_data: str = ""

#     lang_codes = {
#         "English": "en",
#         "French": "fr",
#         "German": "de",
#         "Spanish": "es",
#         "Portuguese": "pt",
#         "Chinese": "zh",
#         "Japanese": "ja",
#         "Hindi": "hi",
#         "Italian": "it",
#         "Korean": "ko",
#         "Dutch": "nl",
#         "Polish": "pl",
#         "Russian": "ru",
#         "Swedish": "sv",
#         "Turkish": "tr"
#     }

#     # async def change_language(self):
#     #     print(self.language)
#     #     client = await AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
#     #     response = client.chat.completions.create(
#     #         model="gpt-4",
#     #         messages = [
#     #             {"role": "system", "content": "You're an AI assistant that categorizes the incoming user input as one of the following languages: English (en), French (fr), German (de), Spanish (es), Portuguese (pt), Chinese (zh), Japanese (ja), Hindi (hi), Italian (it), Korean (ko), Dutch (nl), Polish (pl), Russian (ru), Swedish (sv), Turkish (tr). Return only the 2-letter language code."},
#     #             {"role": "user", "content": self.language}
#     #         ],
#     #         temperature=0.3,
#     #         max_tokens=2
#     #     )
#     #     self.language = response.choices[0].message.content.strip().lower()
#     #     return self.language

#     def begin_fetch(self):
#         self.is_loading = True
#         asyncio.create_task(self.fetch_tts())

#     async def fetch_tts(self):
        # url = f"wss://api.cartesia.ai/tts/websocket?api_key={os.environ['CARTESIA_API_KEY']}&cartesia_version=2024-06-10"

        # audio_chunks = []

        # def on_error(ws, error):
        #     # print(f"Error: {error}")
        #     return

        # def on_message(ws, message):
        #     # print(message)  # Print first 50 characters

        #     try:
        #         json_data = json.loads(message)
        #         if 'error' in json_data:
        #             # print(f"Error from server: {json_data['error']}")
        #             print('error!!!')
        #         else:
        #             audio_chunks.append(message)
        #     except json.JSONDecodeError:
        #         audio_chunks.append(message)

        # def on_close(ws, close_status_code, close_msg):
        #     # print("WebSocket connection closed")

        #     combined_audio = b''.join(audio_chunks)
        #     base64_audio = base64.b64encode(combined_audio).decode('utf-8')
        #     self.audio_data = f"data:audio/wav;base64,{base64_audio}"
        #     self.is_loading = False

        # async def on_open(ws):
        #     # print("WebSocket connection opened")
        #     unique_id = uuid.uuid4()
        
        #     request_data = {
        #         "context_id": str(unique_id),
        #         "model_id": "sonic-multilingual",
        #         "output_format": {
        #             "container": "raw",
        #             "encoding": "pcm_f32le",
        #             "sample_rate": 44100
        #         },
        #         "transcript": self.transcript,
        #         "voice": {
        #             "mode": "id",
        #             "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab"
        #         },
        #         "language": self.lang_codes[self.language],
        #         "add_timestamps": True,
        #         "continue": True
        #     }
        #     halt_data = {
        #         "context_id": str(unique_id),
        #         "model_id": "sonic-multilingual",
        #         "output_format": {
        #             "container": "raw",
        #             "encoding": "pcm_f32le",
        #             "sample_rate": 44100
        #         },
        #         "transcript": "",
        #         "voice": {
        #             "mode": "id",
        #             "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab"
        #         },
        #         "language": self.lang_codes[self.language],
        #         "add_timestamps": True,
        #         "continue": False
        #     }
        #     print(self.language, self.transcript)
        #     await ws.send(json.dumps(request_data))
        #     await ws.send(json.dumps(halt_data))

        # ws = websocket.WebSocketApp(
        #     url,
        #     on_open=on_open,
        #     on_message=on_message,
        #     on_error=on_error,
        #     on_close=on_close
        # )
        
        # await asyncio.get_event_loop().run_in_executor(None, ws.run_forever)

# def voice_model() -> rx.Component:
#     return rx.vstack(
#         rx.button("Generate Speech", on_click=State.begin_fetch),
#         rx.cond(
#             State.is_loading,
#             rx.text("Loading..."),
#             rx.audio(src=State.audio_data, controls=True),
#         ),
#     )

# """ 
# Language options: English (en), French (fr), German (de), Spanish (es), Portuguese (pt), Chinese (zh), Japanese (ja), Hindi (hi), Italian (it), Korean (ko), Dutch (nl), Polish (pl), Russian (ru), Swedish (sv), Turkish (tr).
# """

import reflex as rx
from cartesia import AsyncCartesia
import os
import asyncio
import base64
import uuid

# class Socket(rx.State):

#     unique_id = uuid.uuid4()
#     model_id = "sonic-multilingual"
#     voice_id = "a167e0f3-df7e-4d52-a9c3-f949145efdab"

#     def create_socket(self):
#         url = f"wss://api.cartesia.ai/tts/websocket?api_key={os.environ['CARTESIA_API_KEY']}&cartesia_version=2024-06-10"

#         audio_chunks = []

#         def on_error(ws, error):
#             # print(f"Error: {error}")
#             return

#         def on_message(ws, message):
#             # print(message)  # Print first 50 characters

#             try:
#                 json_data = json.loads(message)
#                 if 'error' in json_data:
#                     # print(f"Error from server: {json_data['error']}")
#                     print('error!!!')
#                 else:
#                     audio_chunks.append(message)
#             except json.JSONDecodeError:
#                 audio_chunks.append(message)

#         def on_close(ws, close_status_code, close_msg):
#             # print("WebSocket connection closed")

#             combined_audio = b''.join(audio_chunks)
#             base64_audio = base64.b64encode(combined_audio).decode('utf-8')
#             self.audio_data = f"data:audio/wav;base64,{base64_audio}"
#             self.is_loading = False

#         async def on_open(ws):
#             # print("WebSocket connection opened")        
#             # request_data = {
#             #     "context_id": str(unique_id),
#             #     "model_id": "sonic-multilingual",
#             #     "output_format": {
#             #         "container": "raw",
#             #         "encoding": "pcm_f32le",
#             #         "sample_rate": 44100
#             #     },
#             #     "transcript": self.transcript,
#             #     "voice": {
#             #         "mode": "id",
#             #         "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab"
#             #     },
#             #     "language": self.lang_codes[self.language],
#             #     "add_timestamps": True,
#             #     "continue": True
#             # }
#             # halt_data = {
#             #     "context_id": str(unique_id),
#             #     "model_id": "sonic-multilingual",
#             #     "output_format": {
#             #         "container": "raw",
#             #         "encoding": "pcm_f32le",
#             #         "sample_rate": 44100
#             #     },
#             #     "transcript": "",
#             #     "voice": {
#             #         "mode": "id",
#             #         "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab"
#             #     },
#             #     "language": self.lang_codes[self.language],
#             #     "add_timestamps": True,
#             #     "continue": False
#             # }
#             inputs = [
#                 {"transcript": "Hello, Sonic!", "continue": True},
#                 {"transcript": " I'm streaming ", "continue": True},
#                 {"transcript": "inputs.", "continue": True},
#                 {"transcript": "", "continue": False}
#             ]
#             for input_data in inputs:
#                 ws.send(
#                     json.dumps()
# #                     context_id=self.unique_id,
# #                     model_id=self.model_id,
                    
# #                 )
# #             print(self.language, self.transcript)
# #             await ws.send(json.dumps(request_data))
# #             await ws.send(json.dumps(halt_data))

# #         ws = websocket.WebSocketApp(
# #             url,
# #             on_open=on_open,
# #             on_message=on_message,
# #             on_error=on_error,
# #             on_close=on_close
# #         )
        
# #         await asyncio.get_event_loop().run_in_executor(None, ws.run_forever)

# class State(rx.State):
#     language: str = ""
#     transcript: str = ""
#     audio_data: str = ""
#     is_streaming: bool = False
#     context_id: str = uuid.uuid4()

#     async def stream_inputs(self):
#         self.is_streaming = True
#         self.audio_data = ""
#         yield

#         try:
#             client = AsyncCartesia(api_key=os.environ.get("CARTESIA_API_KEY"))
#             print(client)
#             ws = await client.tts.websocket()
#             ctx = ws.context(context_id=self.context_id)

#             inputs = [
#                 {"transcript": "Hello, Sonic!", "continue": True},
#                 {"transcript": " I'm streaming ", "continue": True},
#                 {"transcript": "inputs.", "continue": True},
#                 {"transcript": "", "continue": False}
#             ]

#             for input_data in inputs:
#                 response = await ctx.send(
#                     model_id="sonic-english",
#                     voice_id="a167e0f3-df7e-4d52-a9c3-f949145efdab",
#                     **input_data
#                 )
#                 print(response)
#             print('reached!!')
#             audio_chunks = []
#             async for output in ctx.receive():
#                 buffer = await output["audio"]
#                 audio_chunks.append(buffer)
#                 # Update the audio_data state to show progress
#                 self.audio_data = f"Received {len(audio_chunks)} audio chunks"
#                 yield

#             # Combine all audio chunks and convert to base64
#             combined_audio = b"".join(audio_chunks)
#             audio_base64 = base64.b64encode(combined_audio).decode('utf-8')
#             self.audio_data = f"data:audio/wav;base64,{audio_base64}"

#         except Exception as e:
#             self.audio_data = f"Error: {str(e)}"
#         finally:
#             self.is_streaming = False
#             yield


from cartesia import AsyncCartesia
import asyncio
import pyaudio
import os

class State(rx.State):

    language: str = ""
    transcript: str = ""
    is_streaming: bool = True

    async def send_transcripts(self, ctx):
        # Check out voice IDs by calling `client.voices.list()` or on https://play.cartesia.ai/
        voice_id = "87748186-23bb-4158-a1eb-332911b0b708"

        # You can check out our models at https://docs.cartesia.ai/getting-started/available-models
        model_id = "sonic-english"

        # You can find the supported `output_format`s at https://docs.cartesia.ai/reference/api-reference/rest/stream-speech-server-sent-events
        output_format = {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": 44100,
        }

        transcripts = [
            "Sonic and Yoshi team up in a dimension-hopping adventure! ",
            "Racing through twisting zones, they dodge Eggman's badniks and solve ancient puzzles. ",
            "In the Echoing Caverns, they find the Harmonic Crystal, unlocking new powers. ",
            "Sonic's speed creates sound waves, while Yoshi's eggs become sonic bolts. ",
            "As they near Eggman's lair, our heroes charge their abilities for an epic boss battle. ",
            "Get ready to spin, jump, and sound-blast your way to victory in this high-octane crossover!"
        ]

        for transcript in transcripts:
            # Send text inputs as they become available
            await ctx.send(
                model_id=model_id,
                transcript=transcript,
                voice_id=voice_id,
                continue_=True,
                output_format=output_format,
            )

        # Indicate that no more inputs will be sent. Otherwise, the context will close after 5 seconds of inactivity.
        await ctx.no_more_inputs()

    async def receive_and_play_audio(self, ctx):
        p = pyaudio.PyAudio()
        stream = None
        rate = 44100

        async for output in ctx.receive():
            buffer = output["audio"]

            if not stream:
                stream = p.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=rate,
                    output=True
                )

            stream.write(buffer)

        stream.stop_stream()
        stream.close()
        p.terminate()

    async def stream_and_listen(self):
        client = AsyncCartesia(api_key=os.environ.get("CARTESIA_API_KEY"))

        # Set up the websocket connection
        ws = await client.tts.websocket()

        # Create a context to send and receive audio
        ctx = ws.context() # Generates a random context ID if not provided

        send_task = asyncio.create_task(self.send_transcripts(ctx))
        listen_task = asyncio.create_task(self.receive_and_play_audio(ctx))

        # Call the two coroutine tasks concurrently
        await asyncio.gather(send_task, listen_task)

        await ws.close()
        await client.close()
        self.is_streaming = False

    # asyncio.run(self.stream_and_listen())

def voice_model():
    return rx.vstack(
        rx.button("Stream Inputs", on_click=State.stream_and_listen()),
        rx.cond(
            State.is_streaming,
            rx.text("Streaming..."),
            rx.text("Done!"),
        ),
    )

# audioenv, myenv
