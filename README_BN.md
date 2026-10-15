# CYBER NEXUS v3 — Setup guide (Bangla)

## Token কোন ফাইলে বসাবেন?
1. ZIP extract করুন।
2. `.env.example` ফাইলের একটি copy বানিয়ে নাম দিন `.env`।
3. `.env` ফাইল খুলে `BOT_TOKEN=`-এর পরে BotFather token বসান।
   উদাহরণ: `BOT_TOKEN=123456:ABC...` — এটি শুধু উদাহরণ; নিজের token ব্যবহার করবেন।
4. token কাউকে পাঠাবেন না, public code-এ রাখবেন না।

## Facebook links
- Page/profile link is configured in `FACEBOOK_PAGE_URL`.
- Support link is configured in `SUPPORT_FACEBOOK_URL`.
- দুটো লিংক `.env.example`-এ আপনার দেওয়া লিংক দিয়ে আগে থেকেই বসানো আছে।
- Facebook URL দেখে Telegram bot নিজে নিশ্চিত করতে পারে না যে user follow করেছে।
  তাই bot verification request admin-কে পাঠায়; admin নিজে যাচাই করে `/approve USER_ID`
  দিলে চলমান bot process-এ access মেলে। এই simple version-এ approval persistent নয়।

## School information flow
1. User taps `🏫 স্কুলের তথ্য`
2. First sends the school name
3. Then sends the EIIN/small code (4–8 digits)
4. Bot displays the submitted name/code and explains that verified full details require
   an official/authorized school data API. API is not connected yet.

## Run
- Python 3.10+
- `pip install -r requirements.txt`
- Run `python bot.py`
- User sends `/id` to get their numeric Telegram ID.
- Put your ID in `ADMIN_IDS` in `.env`, restart bot.
- Keep `.env` private.

## Status/limitations
This is a working starter structure, not an all-features production service. Video/audio
downloading, QR image generation, IP lookup, public channel analytics, and verified school
records require integrations. No private phone-owner lookup or unauthorized personal-data
search is included. Free hosting availability/limits depend on the provider.
