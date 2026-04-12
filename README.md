# AI Audio Voice Conversion Pipeline System

A GUI-based AI audio processing system that performs end-to-end voice conversion on music using source separation and voice conversion models.

The system integrates multiple external AI models into a unified pipeline with a PyQt5-based graphical interface, allowing users to transform singing voices through a fully automated workflow.

---

## Project Overview

This project builds a complete AI audio processing pipeline system that allows users to:

1. Download audio from a song URL  
2. Separate vocals and instrumental tracks using AI models  
3. Convert extracted vocals into a target speaker voice  
4. Recombine audio tracks into final output  
5. Preview and manage results via GUI  

---

## System Pipeline

Input YouTube URL
↓  
Audio Download Module  
↓  
Source Separation (Spleeter)  
↓  
Vocal Extraction  
↓  
Voice Conversion (so-vits-svc)  
↓  
Audio Re-synthesis  
↓  
Final Output Audio  

---

## AI Models Used

### Source Separation Model (Spleeter)
- Repository: https://github.com/deezer/spleeter  
- Installation: pip install spleeter  
- Purpose: Separate vocals and accompaniment tracks from audio  

---

### Voice Conversion Model (so-vits-svc)
- Repository: https://github.com/svc-develop-team/so-vits-svc  
- Integration method: cloned repository used as backend module  
- Purpose: Convert extracted vocals into target speaker voice  

---

## Integration Strategy

This project integrates external AI systems using two approaches:

- Library-level integration: Spleeter via pip  
- Repository-level integration: so-vits-svc as backend module  

A unified Python pipeline controller manages data flow between all components.

---

## UI Framework

The graphical user interface is built using PyQt5.

UI features include:

- Song input URL
- Audio separation control
- Voice conversion selection
- Track merging
- Playback controls
- Progress status display

---

## System Architecture

- UI Layer: PyQt5 interface  
- Pipeline Layer: Python orchestration engine  
- AI Layer: Spleeter + so-vits-svc  
- Audio Layer: librosa / ffmpeg / soundfile  

---

## Key Contributions

- Designed full AI audio processing pipeline system  
- Integrated multiple external AI models into unified workflow  
- Built GUI for non-technical users   
- Implemented pipeline execution flow and state control  

---

## Technical Challenges

- Handling mismatched audio formats between models  
- Ensuring synchronization between vocal and instrumental tracks  
- Managing long-running AI inference pipelines  
- Integrating repository-level backend dependencies    

---

## Requirements

### Core Environment
- Python 3.8  
- PyTorch 2.0.1 (CUDA 11.8)  
- PyQt5  

### AI Models
- Spleeter  
- so-vits-svc  

### Audio Processing Libraries
- librosa  
- ffmpeg-python  
- soundfile  
- numpy  
- scipy  

### UI / Utilities
- pygame (audio playback / progress feedback)  
- tqdm  
- requests  
- pyyaml  
- regex  

---

## Usage

### 1. Project Structure
Project/
```
|-- so-vits-svc-4.1-Stable
|   |-- SVS_ui.py
|   |-- SVS_contain.py
|   |-- SVS_start.py
|   |-- mp4
|   |-- wav
|   |-- tracks
|   |-- raw
|   |-- results
|   |-- merge
|   |-- logs
|   |   |-- 44k
|   |       |-- weight.pth
```
### 2. Run the application
```
cd code
python SVS_start.py
```
### 3. Workflow

1. Load song URL  
2. Run source separation  
3. Select target voice model  
4. Perform voice conversion  
5. Merge tracks  
6. Export or playback result  

---

## External Acknowledgements

This project uses the following open-source AI systems:

- Spleeter: https://github.com/deezer/spleeter  
- so-vits-svc: https://github.com/svc-develop-team/so-vits-svc  

All rights and credits belong to their respective authors.

---

## Notes

- This project is for research and educational purposes only  
- No original training of AI models was performed  
- Please respect all licenses of the used repositories  
