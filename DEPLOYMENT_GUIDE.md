# ☁️ សៀវភៅណែនាំ៖ របៀបដាក់ Telegram Bot ឱ្យដើរលើ Cloud 24/7 (ឥតគិតថ្លៃ)

ឯកសារ និង Config សម្រាប់ការដាក់លើ Cloud ត្រូវបានរៀបចំរួចរាល់ក្នុង Folder នេះ៖
- [Procfile](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/Procfile)
- [render.yaml](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/render.yaml)
- [runtime.txt](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/runtime.txt)

---

## 🚀 វិធីសាស្ត្រទី ១៖ ដាក់លើ Render.com (Free 24/7 - ណែនាំ)

**Render.com** គឺជាសេវាកម្ម Cloud ដែលអនុញ្ញាតឱ្យ Telegram Bot របស់អ្នកដំណើរការ ២៤ម៉ោង/៧ថ្ងៃ ឥតគិតថ្លៃ ទោះបីជាកុំព្យូទ័ររបស់អ្នកបិទក៏ដោយ។

### ជំហានអនុវត្ត៖
១. ចូលទៅកាន់គេហទំព័រ **[Render.com](https://render.com)** រួចចុះឈ្មោះគណនី (Sign Up) ឥតគិតថ្លៃ។
២. ចុចប៊ូតុង **"New +"** (នៅខាងលើស្តាំ) ➔ ជ្រើសរើស **"Background Worker"**។
៣. ភ្ជាប់គណនី **GitHub** របស់អ្នក រួចជ្រើសរើស Repository គម្រោងនេះ (ឬបង្កើត repo ថ្មីលើ GitHub)។
៤. កំណត់ព័ត៌មានដូចខាងក្រោម៖
   - **Name**: `telegram-invitation-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
៥. ត្រង់កន្លែង **Environment Variables**:
   - Add Variable: `BOT_TOKEN`
   - Value: `8557950565:AAGfn9VhJ3FxIVTx3q-_c7Z-grMhhH1CJSM`
៦. ចុចប៊ូតុង **"Create Background Worker"**!

🎉 *ឥឡូវនេះ Render នឹងដំណើរការ Bot របស់អ្នក ២៤ម៉ោង/៧ថ្ងៃ ដោយស្វ័យប្រវត្តិ!*

---

## 🚀 វិធីសាស្ត្រទី ២៖ ដាក់លើ PythonAnywhere.com (Free Python Hosting)

១. ចូលទៅកាន់គេហទំព័រ **[PythonAnywhere.com](https://www.pythonanywhere.com)** រួចបង្កើត **Create a Beginner Account** (Free)។
២. ចូលទៅកាន់ Tab **Files** ➔ បង្កើត Folder ឈ្មោះ `TelegramBot` ➔ Upload ឯកសារ `bot.py`, `config.py`, `catalog.json`, `.env`, `requirements.txt` ចូល។
៣. ចូលទៅ Tab **Consoles** ➔ បើក **Bash Console** ➔ វាយពាក្យបញ្ជា៖
   ```bash
   pip install -r requirements.txt
   python bot.py
   ```

---

## 💡 សម្រួលការងារ៖
ប្រសិនបើលោកអ្នកមានគណនី **GitHub** ស្រាប់ ខ្ញុំអាចជួយ Upload Code នេះទៅកាន់ GitHub របស់អ្នកភ្លាមៗ ដើម្បីភ្ជាប់ជាមួយ Render.com បានយ៉ាងលឿនបំផុត!
