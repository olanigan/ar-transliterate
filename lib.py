import google.generativeai as genai
import streamlit as st

from prompt import OPTIMIZED_PROMPT
def improve_transcript(transcript):

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
                st.error(f"Gemini Gemini API error: {response.status_code} - {response.text}")
                return None
    with open("edited_transcript.txt", "w") as f:
         f.write(edited_transcript)
    return edited_transcript


def compare_and_correct(original, edited):
    model = genai.GenerativeModel("gemini-1.5-pro-002")
    
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

      response = model.generate_content(payload);
      if response.status_code == 200:
                corrected_transcript += response.json()["candidates"][0]["output"]

      else:
            st.error(f"Gemini Pro API error: {response.status_code} - {response.text}")
            return None
    with open("corrected_transcript.txt", "w") as f:
        f.write(corrected_transcript)
    return corrected_transcript
