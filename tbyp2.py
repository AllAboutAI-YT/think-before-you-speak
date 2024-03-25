import anthropic
import os
from dotenv import load_dotenv
import requests
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import openai
from openai import OpenAI

load_dotenv()

api_keys = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY")
}
client = {
    "openai": openai.OpenAI(api_key=api_keys["openai"]),
    "anthropic": anthropic.Anthropic(api_key=api_keys["anthropic"])
}

NEON_GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET_COLOR = '\033[0m'

def text_to_speech(text, voice_id="G17SuINrv2H9FC6nvetn", xi_api_key="", output_file_path='C:/Users/kris_/Python/tbyp/voice', filename="output.mp3"):

    # Ensure the directory exists
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    # Complete file path
    full_file_path = os.path.join(output_file_path, filename)

    # URL and headers for the ElevenLabs API request
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": xi_api_key
    }

    # Data payload for the API request
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Making a POST request to the API
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Writing the received audio content to the specified file
        with open(full_file_path, 'wb') as f:
            f.write(response.content)
        return {"success": True, "message": "Audio generated successfully.", "file_path": full_file_path}
    else:
        return {"success": False, "message": "Failed to generate audio."}

def play_audio(file_path):
    # Load the audio file
    audio = AudioSegment.from_mp3(file_path)

    # Play the audio
    play(audio)

def openai_chat(user_input, system_message):
    """
    Function to send a query to OpenAI's model, get the response, and print it in yellow color.
    Logs the conversation to a file.
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input}
    ]
    # Perform the chat completion request
    chat_completion = client["openai"].chat.completions.create(
        model="gpt-4-0125-preview", # Adjust the model as necessary
        messages=messages,
        temperature=0.7,
    )
    # Extract the response content
    response_content = chat_completion.choices[0].message.content
    return response_content

def anthropic_chat(user_input, system_message):
    """
    Function to send a query to Anthropic's model, get the streamed response, and log it.
    """
    # Preparing the messages payload
    messages = [
        {
            "role": "user",
            "content": user_input
        }
    ]
    # Perform the chat completion request with streaming
    response_text = ""
    with client["anthropic"].messages.stream(
        model="claude-3-opus-20240229",  # Adjust the model as necessary
        max_tokens=3500,
        temperature=0.7,
        messages=messages,
        system=system_message,
    ) as stream:
        for text in stream.text_stream:
            response_text += text
            print(NEON_GREEN + text + RESET_COLOR, end="", flush=True)
    # Replace '\n' with actual newline characters
    response_text = response_text.replace('\\n', '\n')
    return response_text

qa = "Here is my issue: I am a 24 year old Male. In 3 months I have an opportunity to quit my job, and travel the world with some money i have saved up. The only problem is that the job market is very harsh for people in tech atm, so i dont know if i will find a job again. But I have saved for this trip for 7 years. What do you suggest I do?"
 
system_message1 = "You are a helpful assistant"

p1 = anthropic_chat(qa, system_message1)    
    
#think before you speak    
system_message = "You are a wise and empathetic life coach. Your role is to carefully consider the user's situation, have a inner monolouge and reflect on it as if it were your own. ALWAYS give the answers the reflects your thoughs about the problem"    

t1 = anthropic_chat(f"USERs Question:{qa}\n\nPicture your self in the same situation as the USER. Have an inner monolouge and reflect about your thoughts about the question and write your down thoughs, DO NOT answer the question directly:", system_message)

t2 = anthropic_chat(f"USER`s Question:{qa}\n\nYour thoughts and reflections about the USERs questions:{t1}\n\nNow ONLY answer the USER`s question, give a SHORT and CLEAR answer (DONT USE *), in a personal tone based on your thoughts and reflections:", system_message)  

#text_to_speech(t2)
#play_audio("C:/Users/kris_/Python/tbyp/voice/output.mp3")

system_message2 = "You are an expert in analysing and giving ratings to the best answers to a human from a given question"

e1 = openai_chat(f"USER Question: {qa}\n\nANSWER1: {p1}\n\n ANSWER2: {t2}\n\nFrom the answers to the USERs question above, give your thoughs and rating to both ANSWER1 and ANSWER2:", system_message2)
print(CYAN + e1 + RESET_COLOR)
