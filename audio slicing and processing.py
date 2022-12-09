#library for sound processing
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.effects import high_pass_filter
from pydub.silence import split_on_silence
#operating system module
import os
#library for data processing and analysis
import pandas as pd



###############################################################################################################
########                           VARIABLES                                          #########################
###############################################################################################################
#audio file name
n ='file_name'

#add only the path to the directory where the wav file will be (it's better to do everything in one folder)
SILENCE_FILE = "your_path/silence.wav"

#add only the path to the directory where the noise profile file will be
SILENCE_PROFILE = "your_path/silence.prof"

#add only the path
f = 'your_path/{0}.wav'.format(n)

#add only the path
out_file = 'your_path/{0}1.wav'.format(n)

#add only the path
mp3_file = 'your_path/{0}.mp3'.format(n)


###############################################################################################################
########                           FUNCTIONS                                      #########################
###############################################################################################################
def find_silence(f):
    sound1 = AudioSegment.from_file(f, format="wav")
    ms = 0
    current_silence = 0
    longuest_time = 700
    longuest_val = None
    for i in sound1:
        if i.dBFS > -38.0:
            length = ms - current_silence
            if length > longuest_time:
                longuest_val = sound1[current_silence : ms]
                longuest_time = length
            current_silence = ms + 1
        ms += 1
    longuest_val[250:1500].export(SILENCE_FILE, format="wav")           

def cleanup():
    os.remove(SILENCE_FILE)
    os.remove(SILENCE_PROFILE)
    os.remove(f)
    
def mp3_cleanup():
    os.remove(mp3_file)
    
def e_cleanup():
    os.remove(out_file)
    
def sox_denoise(f):
    
    #use SoX to find the noise profile
    sound1 = AudioSegment.from_file(SILENCE_FILE, format="wav")
    segment_length_sec = len(sound1) / 1000.0
    command ='sox {wav_in} -n trim 0 {silence_len} noiseprof {prof_out}'.format(wav_in=SILENCE_FILE, silence_len=segment_length_sec, prof_out=SILENCE_PROFILE)
    os.system(command)
    
    #use SoX to denoise sound file
    command ='sox {wav_in} {wav_out} noisered {prof_in} 0.2'.format(wav_in=f, wav_out=out_file, prof_in=SILENCE_PROFILE)
    os.system(command)
    
###############################################################################################################
########                                MAIN                                         #########################
###############################################################################################################    
#import audio in .aac format
f_aac = '{f_n}.aac'
f_m = f_aac.format(f_n=n)
sound_aac = AudioSegment.from_file(f_m)

#export audio in .wav format
f_wav = '{f_n}.wav'
f_m = f_wav.format(f_n=n)
sound_wav = sound_aac.export(f_m, format="wav")

print('.aac to .wav -> done')

#do our functions
find_silence(f)
print('find silence -> done')
sox_denoise(f)
print('noise reduction -> done')
cleanup()
print('cleanup -> done')


denoised_file = AudioSegment.from_wav(out_file)
#headroom is how close to the maximum volume to boost
#the signal up to (specified in dB)
sound_norm = normalize(denoised_file, headroom=2.3)
print('normalization -> done')

#Frequency (in Hz) where lower frequency signal will begin to
#be reduced by 6dB per octave (doubling in frequency) below this point
sound_norm_hpf = high_pass_filter(sound_norm, 120)
print('high pass filter -> done')

#export audio in .mp3 format
f_mp3 = '{f_n}.mp3'
f_e = f_mp3.format(f_n=n)
sound_norm_hpf.export(f_e, format="mp3", bitrate="64k")
print('.wav processed file to .mp3 64k -> done')

e_cleanup()
print('e_cleanup -> done')

#add only the path
os.mkdir("your_path/{0}".format(n))
print('create folder -> done')

#import .mp3
f_mp3 = '{f_n}.mp3'
f_e = f_mp3.format(f_n=n)
sound_mp3 = AudioSegment.from_file(f_e)
#read general delimited file into DataFrame
df = pd.read_table("{0}.txt".format(n), delimiter="|", header=None, names=["index", "word"])

#check number of rows in .txt
num_rows = df.shape[0]

print('Number of Rows in {0}.txt :'.format(n),num_rows)
audio_chunks = split_on_silence(sound_mp3, 
    # must be silent for at least 300 ms 
    min_silence_len=400,

    # consider it silent if quieter than -30 dBFS
    silence_thresh=-35,
                                
    # size of the step for checking for silence in milliseconds                            
    #seek_step=1,
            
    #leave some silence at the beginning and end of the chunks        
    keep_silence=200
                                                           
)


#cut audio file word by word and assign the appropriate name to each piece from the text file
for i, chunk in zip(df["index"], audio_chunks):
    
        
    chunk.export("{0}/{1}.mp3".format(n,i), format="mp3")
    
    print ('exporting', "{0}/{1}.mp3".format(n,i))  

mp3_cleanup()
print('mp3_cleanup -> done')

#check the number of lines again
num_rows = df.shape[0]

print('Number of Rows in {0}.txt :'.format(n),num_rows)