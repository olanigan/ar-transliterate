import streamlit as st
import yt_dlp
import requests
from transcribe import transcribe
from pydub import AudioSegment
import os
import tempfile

# Google Gemini API Key (replace with your actual key)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Optimized prompt for Gemini Flash
OPTIMIZED_PROMPT = """
Arabic (and non-English) words are italicized.  Exception: Non-English words that have entered the English vernacular (e.g., Allah, Imām, Quran) are not italicized.  People's names and place names are not italicized.  Book titles are italicized.  "al-" is lowercase unless it is the first word of a sentence or title.  Do not use hamzat al-waṣl for *sūrah* names or prayers (e.g., *Sūrat al-Fātiḥah*, *ṣalāt al-Fajr*).  Do not use apostrophes or single quotes for ع or ء; use their respective symbols (ʿ and ʾ).  Words ending in ة end with "h" (e.g., *sūrah*, *Abu Ḥanīfah*).  Do not transliterate hamzah unless the word is between two words.  Represent *shaddah* with a double letter (e.g., شدّة = *shaddah*). Do not use contractions.  Keep the original Arabic text as is.  Do not add any extra information or commentary.  Only edit the provided text.
"""

import google.generativeai as genai


genai.configure(api_key= st.secrets["GEMINI_API_KEY"])

def improve_transcript(transcript):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    # url = "https://api.generativeai.google.com/v1beta2/models/gemini-flash-002:generateText"


    edited_transcript = ""
    chunks = [transcript[i:i+8000] for i in range(0, len(transcript), 8000)] #8000 charachter chunks
    model = genai.GenerativeModel("gemini-1.5-flash")
    for chunk in chunks:
         payload = {
             "prompt": {"text": f"{OPTIMIZED_PROMPT}\n\n{chunk}"},
        }
        #  response = requests.post(url, headers=headers, json=payload)
         response = model.generate_content(payload);

         if response.status_code == 200:
               edited_transcript += response.json()["candidates"][0]["output"]
         else:
                st.error(f"Gemini Flash API error: {response.status_code} - {response.text}")
                return None
    return edited_transcript





def compare_and_correct(original, edited):

    # Placeholder for comparison logic (Gemini Pro) - requires more complex implementation
    # due to context window limitations and cost considerations
    # This is a simplified example, you'll need to chunk the text for longer transcripts    
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    url = "https://api.generativeai.google.com/v1beta2/models/gemini-pro-002:generateText"

    corrected_transcript = ""
    chunks = [edited[i:i+8000] for i in range(0, len(edited), 8000)]

    for chunk_edited, chunk_original in zip(chunks,[original[i:i+8000] for i in range(0, len(original), 8000)]):
      prompt = f"""Compare the edited transcript with the original transcript and correct any errors or unnecessary changes in the edited transcript.\
                 Make sure the edited transcript follows the prompt and the changes are accurate.\
                 Original Transcript:\n{chunk_original} \
                 Edited Transcript:\n{chunk_edited}"""
      payload = {
             "prompt": {"text": prompt},
        }

      response = requests.post(url, headers=headers, json=payload)
      if response.status_code == 200:
                corrected_transcript += response.json()["candidates"][0]["output"]

      else:
            st.error(f"Gemini Pro API error: {response.status_code} - {response.text}")
            return None

    return corrected_transcript

def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(id)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        return f"{info['id']}.mp3"

st.title("YouTube Transcript Improver")

youtube_url = st.text_input("Enter YouTube URL:")
use_existing_audio = st.checkbox("Use existing audio file")

if st.button("Transcribe and Improve"):
    if youtube_url:
        existing_audio_file = None
        # if use_existing_audio:
        #     audio_files = [f for f in os.listdir() if f.endswith('.mp3')]
        #     if audio_files:
        #         existing_audio_file = st.selectbox("Select existing audio file:", audio_files)
        #     else:
        #         st.warning("No existing audio files found. Proceeding with download.")

        # if not existing_audio_file:
        #     with st.spinner("Downloading audio..."):
        #         audio_file = download_audio(youtube_url)
        # else:
        #     audio_file = existing_audio_file

        # with st.spinner("Transcribing with Groq..."):
        #     original_transcript = transcribe(youtube_url, existing_audio_file=audio_file)
        #     if original_transcript is None:
        #         st.error("Transcription failed. Please try again.")
        #         st.stop()
        #     st.write("Original Transcript:")
        #     st.text(original_transcript)
        
        with open("transcript.txt", "r") as file:
            original_transcript = file.read()
        st.write("Original Transcript:")
        st.text(original_transcript)

        with st.spinner("Improving transcript with Gemini Flash..."):
            edited_transcript = improve_transcript(original_transcript)
            if edited_transcript is None:
                st.stop()
            st.write("Edited Transcript:")
            st.text(edited_transcript)

        with st.spinner("Comparing and Correcting with Gemini Pro..."):
            corrected_transcript = compare_and_correct(original_transcript, edited_transcript)
            if corrected_transcript is None:
                st.stop()
            st.write("Corrected Transcript:")
            st.text(corrected_transcript)

        if not existing_audio_file:
            os.remove(audio_file)
