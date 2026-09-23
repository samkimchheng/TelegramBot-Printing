# 🖨️ Telegram Printing Bot (Windows)

ប្រព័ន្ធគ្រប់គ្រងការបោះពុម្ពឯកសារ និងរូបភាពស្វ័យប្រវត្តិ តាមរយៈ **Telegram Bot** សម្រាប់ Windows PC។

---

## 📌 មុខងារសំខាន់ៗ (Features)

- 📥 **ទទួលឯកសារ**: គាំទ្រឯកសារប្រភេទ PDF និង រូបភាព (JPG, PNG)។
- 🎨 **ជ្រើសរើសការកំណត់**: ជ្រើសរើសចំនួនចម្លង (Copies) និង ប្រភេទពណ៌ (ស/ខ្មៅ ឬ ពណ៌) តាមរយៈប៊ូតុង Inline Keyboards។
- 💰 **គណនាប្រាក់ស្វ័យប្រវត្តិ**: បង្ហាញតម្លៃសរុប (រៀល) ភ្លាមៗ មុនពេលចុចបញ្ជូនទៅព្រីន។
- 🖨️ **ការបោះពុម្ពលើ Windows**: បញ្ជូនទៅកាន់ Windows Default Printer ឬ Printer ដែលបានកំណត់ក្នុង `.env` ដោយស្វ័យប្រវត្តិ។

---

## 🚀 របៀបដំឡើង និងដំណើការ (Setup & Installation)

### ជំហានទី ១: យក Telegram Bot Token ពី @BotFather
1. បើកកម្មវិធី Telegram ហើយស្វែងរក `@BotFather`
2. ផ្ញើពាក្យបញ្ជា `/newbot`
3. ដាក់ឈ្មោះ Bot និង Username (ឧទាហរណ៍៖ `MyPrintShop_bot`)
4. អ្នកនឹងទទួលបាន **HTTP API Token** (ឧទាហរណ៍៖ `123456789:ABCdefGhIJKlmNoPQrsTUVwxyZ`)

### ជំហានទី ២: កំណត់ទិន្នន័យក្នុង `.env`
1. បើកឯកសារ [.env](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/.env)
2. ជំនួស `YOUR_TELEGRAM_BOT_TOKEN_HERE` ដោយ Bot Token របស់អ្នក៖
   ```env
   BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQrsTUVwxyZ
   PRINTER_NAME=
   PRICE_PER_PAGE_BW=200
   PRICE_PER_PAGE_COLOR=500
   ```

### ជំហានទី ៣: ដំណើរការ Bot (Run Bot)
បើក Command Prompt / Terminal ក្នុង folder នេះ រួចវាយ៖
```bash
py bot.py
```

---

## 📁 រចនាសម្ព័ន្ធ Folder (Project Architecture)

- [bot.py](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/bot.py) - កម្មវិធី Bot មេ (Telegram Interface & Flow)
- [printer.py](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/printer.py) - ប្រព័ន្ធគ្រប់គ្រង Windows Printer
- [config.py](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/config.py) - ការកំណត់ទូទៅ & `.env` Loader
- [requirements.txt](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/requirements.txt) - Python Packages ដែលត្រូវប្រើ
- [.env](file:///d:/NUBB%20DOCUMENTARY/TelegramBot%20Printing/.env) - កន្លែងទុក Bot Token & Config
