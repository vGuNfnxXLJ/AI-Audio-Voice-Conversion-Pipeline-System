from SVS_ui import Ui_SVS
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage, QPixmap
import time
import os 
from pytubefix import YouTube
import pygame
from moviepy.editor import VideoFileClip
import subprocess
import shutil
from scipy.io import wavfile
import numpy as np
from spleeter.separator import Separator

class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        pygame.mixer.init()
        pygame.mixer.set_num_channels(6)
        self.ui = Ui_SVS()
        self.ui.setupUi(self)
        self.setup_control()

    
    def setup_control(self):
        self.ui.url_iuput.textChanged.connect(self.get_text)
        self.ui.url_confirm.clicked.connect(self.get_url)
        self.ui.url_reset.clicked.connect(self.reset)
        self.ui.wav_separate.clicked.connect(self.separate_wav)
        
        self.ui.play_vocal.clicked.connect(lambda: self.play_audio(track=1))
        self.ui.pause_vocal.clicked.connect(lambda: self.pause_audio(track=1))
        self.ui.resume_vocal.clicked.connect(lambda: self.resume_audio(track=1))
        
        self.ui.play_drums.clicked.connect(lambda: self.play_audio(track=2))
        self.ui.pause_drums.clicked.connect(lambda: self.pause_audio(track=2))
        self.ui.resume_drums.clicked.connect(lambda: self.resume_audio(track=2))
        
        self.ui.play_bass.clicked.connect(lambda: self.play_audio(track=3))
        self.ui.pause_bass.clicked.connect(lambda: self.pause_audio(track=3))
        self.ui.resume_bass.clicked.connect(lambda: self.resume_audio(track=3))
        
        self.ui.play_other.clicked.connect(lambda: self.play_audio(track=4))
        self.ui.pause_other.clicked.connect(lambda: self.pause_audio(track=4))
        self.ui.resume_other.clicked.connect(lambda: self.resume_audio(track=4))
        
        self.ui.play_vocal_convert.clicked.connect(lambda: self.play_audio(track=5))
        self.ui.pause_vocal_convert.clicked.connect(lambda: self.pause_audio(track=5))
        self.ui.resume_vocal_convert.clicked.connect(lambda: self.resume_audio(track=5))
        
        self.ui.checkBox_convert_vocal.toggled.connect(lambda checked: self.update_idx(checked, 1))
        self.ui.checkBox_drums.toggled.connect(lambda checked: self.update_idx(checked, 2))
        self.ui.checkBox_bass.toggled.connect(lambda checked: self.update_idx(checked, 3))
        self.ui.checkBox_other.toggled.connect(lambda checked: self.update_idx(checked, 4))
        self.ui.select_all.clicked.connect(self.all_idx)
        self.ui.clear_select.clicked.connect(self.clear_idx)
        self.ui.merge.clicked.connect(self.merge_wav)
        
        self.ui.play_merge.clicked.connect(lambda: self.play_audio(track=6))
        self.ui.pause_merge.clicked.connect(lambda: self.pause_audio(track=6))
        self.ui.resume_merge.clicked.connect(lambda: self.resume_audio(track=6))

        self.ui.voice_template.currentIndexChanged.connect(self.get_pth)
        self.ui.voice_template.addItems(['-', 'Donald Trump'])#########
        self.ui.convert.clicked.connect(self.vocal_convert)

        self.tracks = {
            1: {'file': 'vocals.wav', 'is_playing': False, 'is_paused': False, 'length': 0, 'progress': self.ui.vocal_track, 'start_time': 0, 'pause_offset': 0},
            2: {'file': 'drums.wav', 'is_playing': False, 'is_paused': False, 'length': 0, 'progress': self.ui.drums_track, 'start_time': 0, 'pause_offset': 0},
            3: {'file': 'bass.wav', 'is_playing': False, 'is_paused': False, 'length': 0, 'progress': self.ui.bass_track, 'start_time': 0, 'pause_offset': 0},
            4: {'file': 'other.wav', 'is_playing': False, 'is_paused': False, 'length': 0, 'progress': self.ui.other_track, 'start_time': 0, 'pause_offset': 0}
        }
        
        self.timers = {}
        for i in range(1, 7):
            self.timers[i] = QTimer(self)
            self.timers[i].timeout.connect(lambda track=i: self.update_progress(track))
            
        self.G_pths = {
            'Donald Trump' : 'G_Donald-Trump.pth'
        }
        
        self.select_idx = []

    def get_text(self, text):        
        if text:
            self.url = text
            
    def reset(self):
        self.ui.url_iuput.clear()
        self.url = None
        pygame.mixer.quit()
        for track_id, track_data in self.tracks.items():
            track_data['is_playing'] = False
            track_data['is_paused'] = False
            track_data['length'] = 0
            track_data['progress'].setValue(0)
            track_data['start_time'] = 0
            track_data['pause_offset'] = 0
            
        self.ui.url_status.setText("Status : ")
        
    def get_url(self):
        
        if self.url != None:
            self.download_mp4(self.url, download_path=os.path.join(os.getcwd(),'mp4'))
            self.convert_to_wav(os.path.join(os.getcwd(),'mp4'),os.path.join(os.getcwd(),'wav'))
            self.ui.url_status.setText("Status : Finished Downloading")
            
    def separate_wav(self):
        pygame.mixer.quit()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(6)
        input_wav = os.path.join(os.getcwd(), 'wav', os.listdir(os.path.join(os.getcwd(),'wav'))[0])
        if os.path.exists(os.path.join(os.getcwd(),'tracks')):
            self.delete_files_and_folders(os.path.join(os.getcwd(),'tracks'))
        self.separate_audio(input_wav, os.path.join(os.getcwd(),'tracks'))
        
        for i in range(1, 5):
            path = os.path.join(os.getcwd(), 'tracks', os.listdir(os.path.join(os.getcwd(), 'tracks'))[0], self.tracks[i]['file'])
            sound = pygame.mixer.Sound(path)
            self.tracks[i]['sound'] = sound
            self.tracks[i]['channel'] = pygame.mixer.Channel(i - 1)
        
        self.ui.url_status.setText("Status : Finished Tracks Separation")
        
    def play_audio(self, track):
        track_data = self.tracks[track]
        if not track_data['is_playing']:
            track_data['channel'].play(track_data['sound'])
            track_data['length'] = track_data['sound'].get_length()
            track_data['start_time'] = time.time()
            track_data['pause_offset'] = 0
            track_data['progress'].setMaximum(100)
            track_data['is_playing'] = True
            track_data['is_paused'] = False
            self.timers[track].start(100)

    def pause_audio(self, track):
        track_data = self.tracks[track]
        if track_data['is_playing'] and not track_data['is_paused']:
            track_data['channel'].pause()
            now = time.time()
            track_data['pause_offset'] += now - track_data['start_time']
            track_data['is_paused'] = True
            self.timers[track].stop()

    def resume_audio(self, track):
        track_data = self.tracks[track]
        if track_data['is_playing'] and track_data['is_paused']:
            track_data['channel'].unpause()
            track_data['start_time'] = time.time()
            track_data['is_paused'] = False
            self.timers[track].start(100)
            
    def update_progress(self, track):
        track_data = self.tracks[track]
        if track_data['is_playing'] and not track_data['is_paused']:
            now = time.time()
            elapsed = (now - track_data['start_time']) + track_data['pause_offset']
            if track_data['length'] > 0:
                progress = (elapsed / track_data['length']) * 100
                if progress >= 100:
                    progress = 100
                    self.timers[track].stop()
                    track_data['is_playing'] = False
                track_data['progress'].setValue(int(progress))
                
    def get_pth(self):
        self.name = self.ui.voice_template.currentText()
        if self.name != '-':
            self.G_pth = os.path.join(os.getcwd(), 'logs', '44k', self.G_pths[self.name])
            self.ui.pth_status.setText(f"{self.G_pths[self.name]} is selected")
            
        else:
            self.G_pth = 'Invalid pth'
            self.ui.pth_status.setText("Invalid pth !!")
            
    def vocal_convert(self):
        
        tracks_path = os.path.join(os.getcwd(), 'tracks', os.listdir(os.path.join(os.getcwd(), 'tracks'))[0], 'vocals.wav')
        raw_path = os.path.join(os.getcwd(),'raw')
        self.delete_files_and_folders(raw_path)
        self.delete_files_and_folders(os.path.join(os.getcwd(),'results'))
        shutil.copy(tracks_path, raw_path)
        
        command = [
        "python", "inference_main.py",
        "-m", f"logs/44k/{self.G_pths[self.name]}",
        "-c", "configs/config.json",
        "-n", "vocals.wav",
        "-t", "0",
        "-s", self.ui.voice_template.currentText()
        ]
        
        result = subprocess.run(command, check=True)
        
        if result.returncode == 0:
            self.ui.convert_status.setText("Convert Status : Success")
            convert_wav = os.listdir(os.path.join(os.getcwd(),'results'))[0]
            
            self.tracks[5] = {
                'file': f"{convert_wav}",
                'is_playing': False,
                'is_paused': False,
                'length': 0,
                'progress': self.ui.vocal_convert_track,
                'start_time': 0,
                'pause_offset': 0
                }
            
            path = os.path.join(os.getcwd(), 'results', self.tracks[5]['file'])
            sound = pygame.mixer.Sound(path)
            self.tracks[5]['sound'] = sound
            self.tracks[5]['channel'] = pygame.mixer.Channel(4)
            
        else:
            self.ui.convert_status.setText("Convert Status : Failed")
        
    def  update_idx(self, checked, idx):
        if checked:
            self.select_idx.append(idx)
            
        else:
            self.select_idx.remove(idx)
            
        
    def all_idx(self):
        self.ui.checkBox_convert_vocal.setChecked(True)
        self.ui.checkBox_drums.setChecked(True)
        self.ui.checkBox_bass.setChecked(True)
        self.ui.checkBox_other.setChecked(True)
        
    def clear_idx(self):
        self.ui.checkBox_convert_vocal.setChecked(False)
        self.ui.checkBox_drums.setChecked(False)
        self.ui.checkBox_bass.setChecked(False)
        self.ui.checkBox_other.setChecked(False)
        
    def merge_wav(self):
        
        output_directory = os.path.join(os.getcwd(),'merge')
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        wavs_list = []
        if len(self.select_idx) > 0:
            for idx in self.select_idx:
                if idx != 1:
                    path = os.path.join(os.getcwd(), 'tracks', os.listdir(os.path.join(os.getcwd(), 'tracks'))[0], self.tracks[idx]['file'])
                    
                else:
                    path = os.path.join(os.getcwd(), 'results', os.listdir(os.path.join(os.getcwd(), 'results'))[0])                    
                    
                wavs_list.append(path)
                
                
        output_file = os.path.join(os.getcwd(), 'merge', os.listdir(os.path.join(os.getcwd(), 'results'))[0])
        
        self.delete_files_and_folders(os.path.join(os.getcwd(),'merge'))
        self.overlay_wav(wavs_list, output_file)
        self.tracks[6] = {
            'file': 'merge',
            'is_playing': False,
            'is_paused': False,
            'length': 0,
            'progress': self.ui.merge_track,
            'start_time': 0,
            'pause_offset': 0
            }
        
        sound = pygame.mixer.Sound(output_file)
        self.tracks[6]['sound'] = sound
        self.tracks[6]['channel'] = pygame.mixer.Channel(5)
        
        self.ui.merge_status.setText("Merge Status : Completed")     
        
    ''' Backend '''
    def download_mp4(self, url, download_path='.'):
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            print(f"Created directory: {download_path}")
        
        else:
            files = os.listdir(download_path)
            if files:
                for filename in files:
                    file_path = os.path.join(download_path, filename)
                    os.remove(file_path)

        yt = YouTube(url)

        stream = (
            yt.streams
            .filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
            .first()
        )

        if stream is None:
            raise Exception("No suitable MP4 stream found")

        stream.download(output_path=download_path, filename='video.mp4')

        print("Download completed")
        
    def convert_to_wav(self, input_directory, output_directory):
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            print(f"Created directory: {output_directory}")
            
        else:
            files = os.listdir(output_directory)
            if files:
                for filename in files:
                    file_path = os.path.join(output_directory, filename)
                    os.remove(file_path)

        for filename in os.listdir(input_directory):
            if filename.endswith(".mp4"):
                mp4_file = os.path.join(input_directory, filename)
                wav_file = os.path.join(output_directory, f"{filename.split('.')[0]}.wav")

                try:
                    video = VideoFileClip(mp4_file)
                    audio = video.audio
                    audio.write_audiofile(wav_file)
                    print(f"Converted {mp4_file} to {wav_file}")
                    video.close()
                    
                except Exception as e:
                    print(f"Conversion failed for {mp4_file}: {e}")
                    
    def separate_audio(self, input_file, output_dir): 
        os.makedirs(output_dir, exist_ok=True)

        try:
            separator = Separator('spleeter:4stems')
            separator.separate_to_file(input_file, output_dir)
            print(f"Separation successful! Output files are located at {output_dir}")
        except Exception as e:
            print(f"Error occurred: {e}")
            
    def delete_files_and_folders(self, directory):
        if os.path.exists(directory) and os.path.isdir(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                
                elif os.path.isfile(item_path):
                    os.remove(item_path)

            print(f"{directory} : All subfolders and files have been deleted.")
        else:
            print(f"The directory {directory} does not exist or is not a valid directory.")
            
    def overlay_wav(self, files, output_file):
        max_length = 0
        audio_data_list = []
        sample_rate = None

        for file in files:
            rate, audio_data = wavfile.read(file)

            audio_data = audio_data.astype(np.float32) / 32768.0

            if audio_data.ndim == 1:
                audio_data = np.column_stack((audio_data, audio_data))

            if sample_rate is None:
                sample_rate = rate
            elif rate != sample_rate:
                raise ValueError(f"Sample rate mismatch: {file}")

            max_length = max(max_length, audio_data.shape[0])
            audio_data_list.append(audio_data)

        result = np.zeros((max_length, 2), dtype=np.float32)

        for audio_data in audio_data_list:
            result[:audio_data.shape[0]] += audio_data

        result /= len(audio_data_list)

        peak = np.max(np.abs(result))
        if peak > 0:
            result /= peak

        result_int16 = np.clip(result * 32767, -32768, 32767).astype(np.int16)

        wavfile.write(output_file, sample_rate, result_int16)
            
    def closeEvent(self, event):
        print("Window is closing, cleaning up pygame.mixer...")
        pygame.mixer.quit()
        event.accept()