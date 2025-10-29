# Auto TagAll Premium Bot v3.0

Bot Telegram Auto TagAll Premium siap pakai. Owner otomatis bisa akses penuh, seller bisa jalankan bot sendiri dengan token masing-masing. Bot berjalan 24 jam, auto/manual tagall, partner list tersimpan di database, dan logs otomatis.

---

## **Fitur Utama**
- Owner otomatis aktif tanpa `/addprem`.
- Seller bisa punya bot sendiri hanya dengan mengisi `BOT_TOKEN`.
- Auto TagAll:
  - Partner: 5 menit → stop otomatis
  - Non-partner: 2 menit → stop otomatis
- Manual TagAll: `/jalan` → pilih durasi (3,5,20,30,60,90,Unlimited menit)
- List partner tersimpan di database SQLite bot masing-masing.
- Logs aktivitas tagall otomatis tercatat di folder `logs/`.
- Limit partner 1x/hari, reset otomatis tiap hari.
- Bot dapat berjalan 24 jam menggunakan **screen** atau **systemd**.

---

## **Struktur Repository**
```
TagallPremiun/
│
├─ main.py            # Script utama bot
├─ config.py          # Setting bot (OWNER, BOT_TOKEN, API_ID, API_HASH)
├─ requirements.txt   # Library Python
├─ logs/              # Folder logs otomatis
├─ database.db        # SQLite database (akan otomatis dibuat saat pertama kali bot jalan)
└─ README.md          # Panduan deploy
```

---

## **1️⃣ Setup VPS (Pemula)**
1. Login ke VPS:
```bash
ssh user@ip_vps
```
2. Update & install tools:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip git screen -y
```
3. Clone repo:
```bash
cd ~
git clone https://github.com/garpil28/TagallPremiun.git
cd TagallPremiun
```

---

## **2️⃣ Buat Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## **3️⃣ Install Library**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## **4️⃣ Edit config.py**
Buka file `config.py` dan isi data:
```python
OWNER_ID = 6954401932
OWNER_USERNAME = "garfil28"
OWNER_NAME = "Garfield Store"
BOT_NAME = "Auto TagAll Premium"
VERSION = "3.0"
BOT_TOKEN = "MASUKKAN_BOT_TOKEN_DI_BOTFATHER"
API_ID = "MASUKKAN_API_ID"
API_HASH = "MASUKKAN_API_HASH"
```
> Owner otomatis bisa akses semua menu tanpa `/addprem`.  
> Seller cukup ganti `BOT_TOKEN` → bot siap jalan sendiri.

---

## **5️⃣ Jalankan Bot 24 Jam dengan Screen**
```bash
screen -S tagallbot
source venv/bin/activate
python3 main.py
```
- Detach screen: `Ctrl+A` → `D`  
- Bot tetap jalan 24 jam walau logout.

### Reattach screen:
```bash
screen -r tagallbot
```

---

## **6️⃣ Menggunakan Bot**
- `/start` → buka menu utama  
- **Set Partner List** → kirim chat_id/grup partner (1 baris per grup)  
- **Manual TagAll** → `/jalan` → pilih durasi

---

## **7️⃣ Logs**
Semua aktivitas tagall dicatat di folder `logs/`:
```bash
ls logs/
cat logs/log_YYYY-MM-DD.txt
```

---

## **8️⃣ Reset Limit Partner**
- Reset otomatis tiap hari pukul 00:00  
- Limit partner 1x/hari, otomatis berjalan di scheduler

---

## **9️⃣ Tips**
- Gunakan **screen** atau **systemd service** supaya bot berjalan 24 jam tanpa terganggu saat logout VPS.
- Pastikan `config.py` valid, semua tanda kutip lengkap dan token benar.
- Database `database.db` akan otomatis dibuat saat bot pertama kali dijalankan.
