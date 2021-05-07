# import pyaudio  # audio recording
# import wave  # file saving
import pygame  # midi playback
import fnmatch  # name matching
import os  # file listing

#### CONFIGURATION ####

# do_ffmpeg_convert = True  # Uses FFmpeg to convert WAV files to MP3. Requires ffmpeg.exe in the script folder or PATH
# do_wav_cleanup = True  # Deletes WAV files after conversion to MP3
sample_rate = 44100  # Sample rate used for WAV/MP3
channels = 2  # Audio channels (1 = mono, 2 = stereo)
buffer = 1024  # Audio buffer size
# mp3_bitrate = 128  # Bitrate to save MP3 with in kbps (CBR)
# input_device = 1  # Which recording device to use. On my system Stereo Mix = 1


# Begins playback of a MIDI file
def play_music(music_file):
    try:
        pygame.mixer.music.load(music_file)

    except pygame.error:
        print("Couldn't play %s! (%s)" % (music_file, pygame.get_error()))
        return

    pygame.mixer.music.play()


# Init pygame playback
bitsize = -16  # unsigned 16 bit
pygame.mixer.init(sample_rate, bitsize, channels, buffer)

# optional volume 0 to 1.0
pygame.mixer.music.set_volume(1.0)



# Make a list of .mid files in the current directory and all subdirectories
matches = []
for root, dirnames, filenames in os.walk("./"):
    for filename in fnmatch.filter(filenames, '*.mid'):
        matches.append(os.path.join(root, filename))

for song in matches:

    file_name = os.path.splitext(os.path.basename(song))[0]

    # Playback the song
    print("Playing " + file_name + ".mid\n")
    play_music(song)
