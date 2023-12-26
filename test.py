from pydub import AudioSegment
import simpleaudio as sa
import os

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

# Example usage
play_and_delete('output.mp3')
