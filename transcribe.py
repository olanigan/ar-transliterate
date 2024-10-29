import logging
from groq import Groq
import streamlit as st
from pydub import AudioSegment
import math
import os
import yt_dlp
import tempfile

def transcribe(video_url, existing_audio_file=None):
    try:
        if existing_audio_file:
            audio_file = existing_audio_file
            logging.info(f"Using existing audio file: {audio_file}")
        else:
            logging.info("Attempting to download audio")
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                audio_file = temp_audio.name
            # Download audio using yt-dlp (implementation not shown)
            logging.info(f"Audio downloaded successfully: {audio_file}")

        logging.info("Initializing Groq client")
        client = Groq(api_key=st.secrets['GROQ_API_KEY'])

        logging.info("Loading audio file")
        audio = AudioSegment.from_mp3(audio_file)

        chunk_length_ms = 10 * 60 * 1000
        num_chunks = math.ceil(len(audio) / chunk_length_ms)
        logging.info(f"Audio will be processed in {num_chunks} chunks")

        transcriptions = []

        for i in range(num_chunks):
            logging.info(f"Processing chunk {i+1}/{num_chunks}")
            start_time = i * chunk_length_ms
            end_time = min((i + 1) * chunk_length_ms, len(audio))

            chunk = audio[start_time:end_time]
            chunk_file = f"chunk_{i}.mp3"
            chunk.export(chunk_file, format="mp3")

            logging.info(f"Transcribing chunk {i+1}/{num_chunks}")
            with open(chunk_file, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(chunk_file, file.read()),
                    model="whisper-large-v3",
                    response_format="text",
                    language="en",
                    temperature=0.0
                )
            transcriptions.append(transcription)
            logging.info(f"Chunk {i+1} transcription: {transcription[:100]}...")

            os.remove(chunk_file)

        full_transcription = "\n\n".join(transcriptions)
        logging.info(f"Full transcription (first 500 chars): {full_transcription[:500]}...")

        transcript_file = f"{os.path.splitext(os.path.basename(audio_file))[0]}_transcript.txt"
        transcript_file = "transcript.txt"
        with open(transcript_file, "w") as f:
            f.write(full_transcription)

        logging.info("Transcription completed successfully")

        # new_transcription = Transcription(
        #     video_url=video_url,
        #     transcription_text=full_transcription,
        #     audio_file=audio_file,
        #     transcript_file=transcript_file,
        #     language=language
        # )
        # db.session.add(new_transcription)
        # db.session.commit()
        # logging.info("Transcription saved to database")

        # return jsonify({
        #     "transcription": full_transcription,
        #     "audio_file": audio_file,
        #     "transcript_file": transcript_file,
        #     "language": language,
        #     "transcription_id": new_transcription.id
        # })
    except Exception as e:
        logging.error(f"Error during transcription: {str(e)}")
        return None

    finally:
        if not existing_audio_file and 'audio_file' in locals():
            os.remove(audio_file)

    return full_transcription
