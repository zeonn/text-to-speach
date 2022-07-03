# Text to Speach generator 
#### Use Google Text-To-Speach API to generate mp3 files from text files

---

### Requirements
1. Python 3.9+
2. Google cloud account

---

### Preparing
1. Install python requirements
```bash
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```
2. Setup configurations in the `config.py` file
3. Enable API in your Google cloud console https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/metrics
4. Save your Google credentials to `credentials.json` file

---

### Usage
1. Create text files with your text in the `data` directory
2. Run The script
```bash
python main.py
```
3. Your results will be stored in the `data` directory as mp3 files
4. Used chars counter will be stored in `usage_statistics.json` file to exceed the monthly limit of the free account
