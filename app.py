import streamlit as st
import yt_dlp
from transcribe import transcribe

# Google Gemini API Key (replace with your actual key)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Optimized prompt for Gemini Flash
OPTIMIZED_PROMPT = """
Arabic (and non-English) words are italicized.  Exception: Non-English words that have entered the English vernacular (e.g., Allah, Imām, Quran) are not italicized.  People's names and place names are not italicized.  Book titles are italicized.  "al-" is lowercase unless it is the first word of a sentence or title.  Do not use hamzat al-waṣl for *sūrah* names or prayers (e.g., *Sūrat al-Fātiḥah*, *ṣalāt al-Fajr*).  Do not use apostrophes or single quotes for ع or ء; use their respective symbols (ʿ and ʾ).  Words ending in ة end with "h" (e.g., *sūrah*, *Abu Ḥanīfah*).  Do not transliterate hamzah unless the word is between two words.  Represent *shaddah* with a double letter (e.g., شدّة = *shaddah*). Do not use contractions.  Keep the original Arabic text as is.  Do not add any extra information or commentary.  Only edit the provided text.
"""



def improve_transcript(transcript):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    url = "https://api.generativeai.google.com/v1beta2/models/gemini-flash-002:generateText"


    edited_transcript = ""
    chunks = [transcript[i:i+8000] for i in range(0, len(transcript), 8000)] #8000 charachter chunks

    for chunk in chunks:
         payload = {
             "prompt": {"text": f"{OPTIMIZED_PROMPT}\n\n{chunk}"},
        }
         response = requests.post(url, headers=headers, json=payload)
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


st.title("YouTube Transcript Improver")

youtube_url = st.text_input("Enter YouTube URL:")

if st.button("Transcribe and Improve"):
    if youtube_url:
        with st.spinner("Extracting audio..."):
            ydl_opts = {"format": "bestaudio/best", "outtmpl": "audio.%(ext)s"}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
               info =  ydl.extract_info(youtube_url, download=True)
               filename = ydl.prepare_filename(info)

               audio_file = AudioSegment.from_file(filename)




        with st.spinner("Transcribing with Groq..."):
            original_transcript = transcribe(youtube_url)
            if original_transcript is None:
                st.stop()  # Stop execution if transcription fails
            st.write("Original Transcript:")
            st.text(original_transcript)

        with st.spinner("Downloading audio..."):
            ydl_opts = {"format": "bestaudio/best", "outtmpl": "audio.%(ext)s"}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
               info =  ydl.extract_info(youtube_url, download=True)
               filename = ydl.prepare_filename(info)

               audio_file = AudioSegment.from_file(filename)


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
