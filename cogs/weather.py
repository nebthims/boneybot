import requests
import os
from openai import AsyncOpenAI
import openai
import json
from elevenlabs import set_api_key
import discord
from discord.ext import commands
from pydub import AudioSegment
import simpleaudio as sa

client = AsyncOpenAI()

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(" - WEATHER: Ready!")
        
    @commands.command()
    async def weather(self,ctx):
      w = await get_weather(ctx)
      t = await interpret_weather(w,ctx)
      s = Elevenlabs_TTS(t)
      play_and_delete(s)
      
    @commands.command()
    async def speak(self,ctx):
      text = ctx.message.content
      split_text = text.split(' ')
      aiprompt = ' '.join(split_text[1:])
      s = Elevenlabs_TTS(aiprompt)
      play_and_delete(s)


# Get Weather Data for Melbourne for Today
async def get_weather(ctx):
  # Variable setup
  lat = -37.73516949940518 
  lon = 144.95277008659258
  API_key = os.environ['OPENWEATHER_API_KEY']
  
  # API Request
  request = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={API_key}&units=metric")
  info = request.json()

  result = {
    "current_temperature": round(info["current"]["temp"],1),
    "max_temperature": round(info["daily"][0]["temp"]["max"],1),
    "chance_of_rainfall": str(info["daily"][0].get("pop", 0)*100)+"%",
    "rainfall": str(info["daily"][0].get("rain", 0))+" millimetres",
    "UV_index": info["daily"][0]["uvi"],
  }
  
  await ctx.send(f"Current Temp: {result['current_temperature']}, UV Index: {result['UV_index']}.")
  return result

# Send Weather Data to GPT for parsing into BoneyBot's report
async def interpret_weather(weather_report,ctx):
  openai.api_key = os.getenv("OPENAI_API_KEY")
  completion = await client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are Boney the Skeleton, a helpful classroom assistant. You are a friendly cowboy skeleton who loves to teach kids about the weather. Your catchphrase is 'Howdy Kids, welcome to Boney's weather Bone-Anza!', and you must use it to begin your report. You will interpret a weather report in your own unique Boney style, using some simple cowboy references. Remember that we are an Australian audience, and that you are speaking to young children. If there is rain, let the kids know that it will probably be a 'wet day timetable'. If the UV Rating is lower than 4, tell children they don't need to wear hats. If it is higher than 4, tell the children they DO need to wear hats. You are limited on your response size, so keep things succinct. "},
            {"role": "user", "content": 
             f"""Today's weather report is:\n
             The current temperature today is {weather_report["current_temperature"]} degrees C, and the maximum temperature today is {weather_report["max_temperature"]} degrees C. There is a {weather_report["chance_of_rainfall"]} chance of rainfall today, and we are expecting {weather_report["rainfall"]}. Today's UV Rating is {weather_report["UV_index"]}.    
             """}
            ],  
          max_tokens=250,
          n=1,
          stop=None,
          temperature=0.4,
            )
  response = json.loads(completion.model_dump_json(indent=2))
  await ctx.send(str(response['choices'][0]['message']['content']))
  return(str(response['choices'][0]['message']['content']))

def Elevenlabs_TTS(text):
  SPEECH_KEY = os.environ['SPEECH_KEY']
  CHUNK_SIZE = 1024
  url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
  
  headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": SPEECH_KEY
  }
  
  data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.5
    }
  }
  
  response = requests.post(url, json=data, headers=headers)
  with open('output.mp3', 'wb') as f:
      for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
          if chunk:
              f.write(chunk)
  return 'output.mp3'

def convert_mp3_to_wav(mp3_file_path):
    # Load mp3 file
    audio = AudioSegment.from_mp3(mp3_file_path)

    # Convert to wav
    wav_file_path = mp3_file_path.replace('.mp3', '.wav')
    audio.export(wav_file_path, format="wav")

    return wav_file_path

def play_and_delete(file_path):
    try:
        # Convert MP3 to WAV
        wav_file_path = convert_mp3_to_wav(file_path)

        # Play the audio file
        wave_obj = sa.WaveObject.from_wave_file(wav_file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing

        # Delete the audio files
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error: {e}")


async def setup(bot):
    await bot.add_cog(Weather(bot))
