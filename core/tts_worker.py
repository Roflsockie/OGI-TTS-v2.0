import sys
import os
import asyncio
import tempfile
import subprocess
import edge_tts
from PyQt5.QtCore import QThread, pyqtSignal

# Try to import optional modules
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# FFMPEG is optional for edge-tts
pass

class TTSWorker(QThread):
    """Worker thread for TTS processing"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self, text, voice, output_file, speed=1.0, volume=100, pitch=0, play_only=False, model="Edge TTS"):
        super().__init__()
        self.text = text
        self.voice = voice
        self.output_file = output_file
        self.speed = speed
        self.volume = volume
        self.pitch = pitch
        self.play_only = play_only
        self.model = model

    def run(self):
        print("Starting TTS...")
        self.progress.emit(10)
        self.log_signal.emit("Starting TTS... 10%")
        try:
            self.run_edge_tts()
        except Exception as e:
            print(f"TTS Error: {e}")
            self.finished.emit(f"Error: {e}")

    def run_edge_tts(self):
        print("Using Edge TTS")
        self.progress.emit(20)
        self.log_signal.emit("Initializing Edge TTS... 20%")
        async def generate_tts():
            self.progress.emit(30)
            self.log_signal.emit("Preparing voice... 30%")
            # Adjust voice settings with validation
            kwargs = {"voice": self.voice}

            # Validate and set speed (rate) - Edge TTS accepts -100% to +100%
            if self.speed != 1.0:
                rate_value = int((self.speed - 1) * 100)
                # Clamp rate to valid range
                rate_value = max(-100, min(100, rate_value))
                kwargs["rate"] = f"{rate_value:+d}%"  # Always include sign

            # Validate and set volume - Edge TTS accepts -100% to +100%
            if self.volume != 100:
                if self.volume == 0:
                    kwargs["volume"] = "+0%"
                else:
                    # Clamp volume to valid range
                    volume_value = max(-100, min(100, self.volume - 100))
                    kwargs["volume"] = f"{volume_value:+d}%"

            # Validate and set pitch - Edge TTS accepts -50Hz to +50Hz
            if self.pitch != 0:
                # Clamp pitch to valid range
                pitch_value = max(-50, min(50, self.pitch))
                kwargs["pitch"] = f"{pitch_value:+d}Hz"

            communicate = edge_tts.Communicate(self.text, **kwargs)
            self.progress.emit(50)
            self.log_signal.emit("Generating speech... 50%")

            if self.play_only:
                # Create file in tts_audio directory with unique name
                import uuid
                tts_dir = os.path.dirname(self.output_file) if hasattr(self, 'output_file') and self.output_file else os.path.join(os.path.dirname(__file__), '..', 'tts_audio')
                os.makedirs(tts_dir, exist_ok=True)
                
                # Generate unique filename to avoid conflicts
                unique_id = str(uuid.uuid4())[:8]
                temp_path = os.path.join(tts_dir, f"play_temp_{unique_id}.wav")
                
                await communicate.save(temp_path)
                
                # Check if file was created and has content
                if os.path.exists(temp_path):
                    file_size = os.path.getsize(temp_path)
                    self.log_signal.emit(f"Audio file created: {file_size} bytes")
                    if file_size == 0:
                        self.log_signal.emit("Error: Audio file is empty!")
                        played = False
                    else:
                        self.progress.emit(90)
                        self.log_signal.emit("Playing audio... 90%")
                        # Play the file
                        played = False
                        
                # Try different playback methods (reordered by priority)
                playback_methods = []
                method_names = []
                
                # Method 1: PowerShell with .NET MediaPlayer (background playback)
                def powershell_play():
                    ps_command = f'Add-Type -AssemblyName presentationCore; $player = New-Object System.Windows.Media.MediaPlayer; $player.Open("{temp_path}"); $player.Play(); Start-Sleep 10; $player.Stop()'
                    subprocess.run(['powershell', '-Command', ps_command], shell=True)
                
                playback_methods.append(powershell_play)
                method_names.append("powershell_media")
                
                # Method 2: PowerShell with SoundPlayer (simpler)
                def powershell_sound():
                    ps_command = f'$player = New-Object System.Media.SoundPlayer "{temp_path}"; $player.PlaySync()'
                    subprocess.run(['powershell', '-Command', ps_command], shell=True)
                
                playback_methods.append(powershell_sound)
                method_names.append("powershell_sound")
                
                # Method 3: System default player with shell=True
                playback_methods.append(lambda: subprocess.run(['cmd', '/c', 'start', '', temp_path], shell=True))
                method_names.append("cmd_start")
                
                # Method 4: os.startfile (opens in associated app)
                playback_methods.append(lambda: os.startfile(temp_path))
                method_names.append("os_startfile")
                
                # Method 5: pygame mixer
                if PYGAME_AVAILABLE:
                    playback_methods.append(lambda: (pygame.mixer.music.load(temp_path), pygame.mixer.music.play(), pygame.time.wait(int(pygame.mixer.music.get_length() * 1000)))[2])
                    method_names.append("pygame")
                
                # Method 6: winsound (last resort)
                if WINSOUND_AVAILABLE:
                    playback_methods.append(lambda: winsound.PlaySound(temp_path, winsound.SND_FILENAME))
                    method_names.append("winsound")
                
                for i, method in enumerate(playback_methods):
                    try:
                        method()
                        played = True
                        self.log_signal.emit(f"Audio played successfully using {method_names[i]}")
                        break
                    except Exception as e:
                        self.log_signal.emit(f"{method_names[i]} failed: {e}")
                        continue
                
                if not played:
                    self.log_signal.emit("Could not play audio - all methods failed")
                    # Save file for debugging
                    debug_file = os.path.join(os.path.dirname(self.output_file), "debug_tts_audio.wav")
                    try:
                        import shutil
                        shutil.copy2(temp_path, debug_file)
                        self.log_signal.emit(f"Debug file saved: {debug_file}")
                    except Exception as e:
                        self.log_signal.emit(f"Could not save debug file: {e}")
                
                # Clean up with delay to allow player to open file
                if played:
                    # If playback was successful, wait a bit before cleanup
                    from PyQt5.QtCore import QTimer
                    def cleanup_temp_file():
                        try:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                        except:
                            pass
                    
                    # Schedule cleanup after 10 seconds
                    timer = QTimer()
                    timer.timeout.connect(cleanup_temp_file)
                    timer.setSingleShot(True)
                    timer.start(10000)  # 10 seconds
                else:
                    # If playback failed, cleanup immediately
                    try:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    except:
                        pass
            else:
                await communicate.save(self.output_file)
                self.progress.emit(90)
                self.log_signal.emit("Saving audio... 90%")

        asyncio.run(generate_tts())
        self.progress.emit(100)
        self.log_signal.emit("TTS completed 100%")
        self.finished.emit("TTS completed")
        print("TTS finished successfully")