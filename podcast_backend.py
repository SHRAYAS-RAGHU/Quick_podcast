# import modal
# import json
# import pathlib

# from typing import Iterator, Tuple

# from modal import NetworkFileSystem

# volume = NetworkFileSystem.persisted("dataset-cache-vol")

# MAIN_DIR = '/cache'

# def download_whisper():
#   # Load the Whisper model
#   import os
#   import whisper
#   print ("Download the Whisper model")


#   # Perform download only once and save to Container storage
#   whisper._download(whisper._MODELS["medium"], '/content/podcast/', False)


# stub = modal.Stub("corise-podcast-project")
# corise_image = modal.Image.debian_slim().pip_install("feedparser",
#                                                      "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
#                                                      "requests",
#                                                      "openai",
#                                                      "tiktoken",
#                                                      "wikipedia",
#                                                      "ffmpeg-python").apt_install("ffmpeg").pip_install("ffmpeg-python").run_function(download_whisper)

# @stub.function(image=corise_image, gpu="any", timeout=600, network_file_systems={MAIN_DIR: volume})
# def get_transcribe_podcast(rss_url, local_path):
#   print ("Starting Podcast Transcription Function")
#   print ("Feed URL: ", rss_url)
#   print ("Local Path:", local_path)

#   # Read from the RSS Feed URL
#   import feedparser
#   intelligence_feed = feedparser.parse(rss_url)
#   podcast_title = intelligence_feed['feed']['title']
#   episode_title = intelligence_feed.entries[0]['title']
#   episode_image = intelligence_feed['feed']['image'].href
#   for item in intelligence_feed.entries[0].links:
#     if (item['type'] == 'audio/mpeg'):
#       episode_url = item.href
#   episode_name = "podcast_episode.mp3"
#   print ("RSS URL read and episode URL: ", episode_url)

#   # Download the podcast episode by parsing the RSS feed
#   from pathlib import Path
#   p = Path(local_path)
#   p.mkdir(exist_ok=True)

#   print ("Downloading the podcast episode")
#   import requests
#   with requests.get(episode_url, stream=True) as r:
#     r.raise_for_status()
#     episode_path = p.joinpath(episode_name)
#     with open(episode_path, 'wb') as f:
#       for chunk in r.iter_content(chunk_size=8192):
#         f.write(chunk)

#   print ("Podcast Episode downloaded")

#   # Load the Whisper model
#   import os
#   # import whisper

#   # # Load model from saved location
#   # print ("Load the Whisper model")
#   # model = whisper.load_model('medium', device='cuda', download_root='/content/podcast/')

#   # # Perform the transcription
#   # print ("Starting podcast transcription")
#   # result = model.transcribe(local_path + episode_name)
#   print('get_transcribe_podcast', episode_path)
#   result  = transcribe_episode.call(audio_filepath = episode_path)
#   # Return the transcribed text
#   print ("Podcast transcription completed, returning results...")
#   output = {}
#   output['podcast_title'] = podcast_title
#   output['episode_title'] = episode_title
#   output['episode_image'] = episode_image
#   output['episode_transcript'] = result
#   return output

# @stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
# def get_podcast_summary(podcast_transcript):
#   import openai
#   instructPrompt = """
#   You are a world famous blogger who summarizes podcasts for your million subscribers from transcripts. Now you are going to summarize a podcast to your readers. Write the summary of the podcast and ensure to cover the important aspects of discussion and please be concise.
#   The transcript is available below \n
#   """

#   request = instructPrompt + podcast_transcript

#   chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
#                                               messages=[{"role": "system", "content": "You are a helpful assistant."},
#                                                         {"role": "user", "content": request}
#                                                         ]
#                                               )

#   podcastSummary = chatOutput.choices[0].message.content
#   return podcastSummary

# @stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
# def get_podcast_guest(podcast_transcript):
#   import openai
#   import wikipedia
#   import json

#   request = podcast_transcript[:10000]

#   completion = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": request}],
#     functions=[
#       {
#           "name": "get_podcast_guest_information",
#           "description": "Get information on the podcast guest using their full name and the name of the organization they are part of to search for them on Wikipedia or Google",
#           "parameters": {
#               "type": "object",
#               "properties": {
#                   "guest_name": {
#                       "type": "string",
#                       "description": "The full name of the guest who is speaking in the podcast",
#                   },
#                   "guest_organization": {
#                       "type": "string",
#                       "description": "The full name of the organization that the podcast guest belongs to or runs",
#                   },
#                   "guest_title": {
#                       "type": "string",
#                       "description": "The title, designation or role of the podcast guest in their organization",
#                   },
#               },
#               "required": ["guest_name"],
#           },
#       }
#   ],
#   function_call={"name": "get_podcast_guest_information"}
#   )

#   podcast_guest = ""
#   podcast_guest_org = ""
#   podcast_guest_title = ""
#   response_message = completion["choices"][0]["message"]
#   if response_message.get("function_call"):
#     function_name = response_message["function_call"]["name"]
#     function_args = json.loads(response_message["function_call"]["arguments"])
#     podcast_guest=function_args.get("guest_name")
#     podcast_guest_org=function_args.get("guest_organization")
#     podcast_guest_title=function_args.get("guest_title")

#     if podcast_guest is not None:
#       if podcast_guest_org is None:
#         podcast_guest_org = "Not Available"
#       if podcast_guest_title is None:
#         podcast_guest_title = "Not Available"
#       try:
#         input = wikipedia.page(podcast_guest + " " + podcast_guest_org + " " + podcast_guest_title, auto_suggest=True)
#         podcast_guest_summary = input.summary
#       except:
#         podcast_guest_summary = "Not Available"
#     else:
#       podcast_guest = "Not Available"
#       podcast_guest_org = "Not Available"
#       podcast_guest_title = "Not Available"
#       podcast_guest_summary = "Not Available"

#     podcast_guest_details = {
#       'name': podcast_guest,
#       'org': podcast_guest_org,
#       'title': podcast_guest_title,
#       'summary': podcast_guest_summary
#     }

#     return podcast_guest_details

# @stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
# def get_podcast_highlights(podcast_transcript):
#   import openai
#   instruct = """
#   You are the main editor for a podcast to be listened by millions of people. You are given with a podcast transcript and will have to identify atleast 5 key significant moments in the podcast as highlight.
#   - Each highlight needs to be a statement or quote by the podcast guest
#   - Each highlight must be concise and should not bore the audience to leave the podcast
#   - Ensure to pick highlights from the entire episode
#   - Each highlight must be interesting and impactful for the readers

#   Provide only the highlights as a full sentence and format it as follows:

#   - Highlight 1 of the podcast
#   - Highlight 2 of the podcast
#   - Highlight 3 of the podcast
#   """
#   request = instruct + podcast_transcript
#   chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
#                                               messages=[{"role": "system", "content": "You are a helpful assistant."},
#                                                         {"role": "user", "content": request}
#                                                         ]
#                                               )

#   podcastHighlights = chatOutput.choices[0].message.content
#   return podcastHighlights

# @stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200, network_file_systems={'/cache': volume})
# def process_podcast(url, path):
#   output = {}
#   podcast_details = get_transcribe_podcast.call(url, path)
#   podcast_summary = get_podcast_summary.call(podcast_details['episode_transcript'])
#   podcast_guest = get_podcast_guest.call(podcast_details['episode_transcript'])
#   podcast_highlights = get_podcast_highlights.call(podcast_details['episode_transcript'])
#   output['podcast_details'] = podcast_details
#   output['podcast_summary'] = podcast_summary
#   output['podcast_guest'] = podcast_guest
#   output['podcast_highlights'] = podcast_highlights
#   import json
#   with open(f"/cache/content/{output['podcast_details']['episode_title']}.json", "w") as outfile:
#       json.dump(output, outfile)
#   return output

# @stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200, network_file_systems={'/cache': volume})
# def get_stored_podcast():
#   total_out = []
#   output = {}
#   import json
#   import os
#   json_files = [f for f in os.listdir('/cache/content/') if f.endswith('.json')]
#   for file in json_files:
#     with open(f"/cache/content/{file}", "r") as outfile:
#         output = json.load(outfile)
#         total_out.append(output)

#   return total_out

# def split_silences(
#     path: str, min_segment_length: float = 30.0, min_silence_length: float = 1.0
# ) -> Iterator[Tuple[float, float]]:
#     """Split audio file into contiguous chunks using the ffmpeg `silencedetect` filter.
#     Yields tuples (start, end) of each chunk in seconds."""

#     import re

#     import ffmpeg

#     silence_end_re = re.compile(
#         r" silence_end: (?P<end>[0-9]+(\.?[0-9]*)) \| silence_duration: (?P<dur>[0-9]+(\.?[0-9]*))"
#     )
#     import os
#     os.chdir('/cache/content/')
#     # print(os.getcwd() + '\n',  os.listdir())
#     # os.chdir('..')
#     print(os.getcwd() + '\n', os.listdir())
#     try:
#       metadata = ffmpeg.probe('podcast_episode.mp3')
#     except ffmpeg.Error as e:
#       # print('stdout:', e.stdout.decode('utf8'))
#       print('stderr:', e.stderr.decode('utf8'))
#       raise e
#     # print('Metadata' + metadata)
#     duration = float(metadata["format"]["duration"])

#     reader = (
#         ffmpeg.input(str(path))
#         .filter("silencedetect", n="-10dB", d=min_silence_length)
#         .output("pipe:", format="null")
#         .run_async(pipe_stderr=True)
#     )

#     cur_start = 0.0
#     num_segments = 0

#     while True:
#       try:
#         line = reader.stderr.readline().decode("utf-8")
#         if not line:
#             break
#         match = silence_end_re.search(line)
#         if match:
#             silence_end, silence_dur = match.group("end"), match.group("dur")
#             split_at = float(silence_end) - (float(silence_dur) / 2)

#             if (split_at - cur_start) < min_segment_length:
#                 continue

#             yield cur_start, split_at
#             cur_start = split_at
#             num_segments += 1
#       except Exception as e:
         
#          print('Error here in split method ', e)
#          print(reader.stderr.readline().decode("utf-8"))
#     print('Silence exiting done')
#     os.chdir('..')
#     # silencedetect can place the silence end *after* the end of the full audio segment.
#     # Such segments definitions are negative length and invalid.
#     if duration > cur_start and (duration - cur_start) > min_segment_length:
#         yield cur_start, duration
#         num_segments += 1

#     print(f"Split into {num_segments} segments")

# @stub.function(image=corise_image,  cpu=2, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200, network_file_systems={'/cache': volume})   
# def transcribe_segment(
#     start: float,
#     end: float,
#     audio_filepath: str
# ):
#     import tempfile
#     import time

#     import ffmpeg
#     import whisper

#     t0 = time.time()
#     with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
#         (
#             ffmpeg.input(str(audio_filepath))
#             .filter("atrim", start=start, end=end)
#             .output(f.name)
#             .overwrite_output()
#             .run(quiet=True)
#         )

#         model = whisper.load_model(
#             'medium', download_root='/content/podcast')
#         result = model.transcribe(f.name, language="en", fp16=False)  # type: ignore

#     print(
#         f"Transcribed segment {start:.2f} to {end:.2f} ({end - start:.2f}s duration) in {time.time() - t0:.2f} seconds."
#     )

#     return result

# @stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200, network_file_systems={'/cache': volume})   
# def transcribe_episode(
#     audio_filepath: str,
# ):

#     # segment_gen = split_silences(str(audio_filepath))

#     # output_text = ""
#     # output_segments = []

#     # for s, e in segment_gen:
#     #   import time

#     #   import ffmpeg
#     #   import whisper

#     #   with open('/cache/content/temp-1.mp3', 'wb') as f:
#     #       (
#     #           ffmpeg.input(str(audio_filepath))
#     #           .filter("atrim", start=s, end=e)
#     #           .output(f.name)
#     #           .overwrite_output()
#     #           .run(quiet=True)
#     #       )
      
#     #   model = whisper.load_model('medium', device='cuda', download_root='/content/podcast/')
#     #   result = model.transcribe('/cache/content/temp-1.mp3', language="en", fp16=True)  # type: ignore

#     #   output_text += result['text']
    
#     # return output_text

#     segment_gen = split_silences(str(audio_filepath))

#     print('Segment generation success')

#     output_text = ""

#     for result in transcribe_segment.starmap(
#         segment_gen, kwargs=dict(audio_filepath=audio_filepath)
#     ):
#         output_text += result["text"]

#     return output_text

# @stub.local_entrypoint()
# def test_method(url, path):
#   output = {}
#   podcast_details = get_transcribe_podcast.call(url, path)
#   print ("Podcast Summary: ", get_podcast_summary.call(podcast_details['episode_transcript']))
#   print ("Podcast Guest Information: ", get_podcast_guest.call(podcast_details['episode_transcript']))
#   print ("Podcast Highlights: ", get_podcast_highlights.call(podcast_details['episode_transcript']))