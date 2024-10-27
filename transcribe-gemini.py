import os
import sys
import time
import google.generativeai as genai

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-002",
  generation_config=generation_config,
)

def get_full_path(folder_path, file_name):
    cwd = os.getcwd()
    return os.path.join(cwd, folder_path, file_name)
    

# sample local files for testing
files = [
  upload_to_gemini(os.path.join(get_full_path("test_files", "sample.mp3")), mime_type="audio/mpeg"),
]

# Some files have a processing delay. Wait for them to be ready.
wait_for_files_active(files)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
        "Transcribe this audio, then use the following instruction to correct and edit it;\n\n\n I need you to format it according to the following rules:\n\nArabic (and non-English) words are  italicized. That is the general rule. The exception is when a non-English word has entered the English vernacular. E.g. Allāh, imām, Qurʾān, etc.\nPeople’s names and names of places are not italicized even if they are Arabic names e.g. Imām Bukhāri, Makkah\nItalicize names of books (all books whether English and Arabic) E.g. Ṣaḥīḥ Bukhāri, Sharḥ al-Mumutiʿ ʿAla Zād al-Mustaqniʿ\nDo not use double vowels, use: ā, ī, and ū. Please note that we do not end words with the long vowel. Eg. Ḥanbali, Bukhāri\nFor al- it is always lower case  unless it is the first word in a sentence or title.\nWe do not use hamzatʾl-waṣl for sūrah names and the prayers, so it’s: Sūrat al-Fātiḥah and ṣalāt al-Fajr\nPlease DO NOT use the apostrophe or single quotation marks for ع or ء--use the symbol assigned to it [02bf and 02be respectively].\nWords ending with ة end with an ‘h’ e.g. sūrah, Abu Ḥanīfah\nThere is no need to transliterate the hamzah if a word begins with a hamzah unless that word is in between two words e.g. ayah, taḥiyyatʾl-masjid\nShaddah: any letter that has a shaddah on it needs to be represented with two letters e.g. شدّة shaddah\n\nDo not use contractions like isn't or you've or don't. Instead use their full form like is not, you have, and do not. \n",
      ],
    }
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)