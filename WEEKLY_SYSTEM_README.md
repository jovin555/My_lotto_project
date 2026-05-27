# Weekly Lotto Max Prediction System

## 🎯 System Overview

Automated system that:
1. **Generates weekly Lotto Max predictions** based on 1,013+ historical draws
2. **Analyzes predictions with DeepSeek AI** for expert insights
3. **Saves weekly reports** with statistics and recommendations
4. **Sends to Telegram** automatically
5. **Schedules weekly runs** at your preferred day/time

## 📊 Generated Files

Each week generates:
- **`prediction_YYYY_Week_##.json`** - Prediction data in JSON format
- **`report_YYYY_Week_##.txt`** - Full analysis report with AI insights

## 🚀 Usage

### Run One-Time Prediction

```bash
cd /home/eva/workspace/My_lotto_project
source venv/bin/activate

# Generate prediction only
python weekly_lotto_predictor.py

# Generate and send to Telegram
python weekly_lotto_predictor.py --telegram-chat-id YOUR_CHAT_ID
```

### Setup Automatic Weekly Scheduler

```bash
# Run scheduler (generates prediction every Monday at 09:00)
python scheduler.py --telegram-chat-id YOUR_CHAT_ID

# Custom day and time
python scheduler.py --telegram-chat-id YOUR_CHAT_ID --day tuesday --time 15:30
```

**Available days:** monday, tuesday, wednesday, thursday, friday, saturday, sunday

## 📱 Finding Your Telegram Chat ID

1. Open Telegram and search for `@userinfobot`
2. Send `/start` message
3. Bot will reply with your Chat ID
4. Use this ID to receive predictions

## 📊 This Week's Prediction

**Week:** 2026 - Week 21  
**Generated:** Wednesday, May 27, 2026

### 🎯 Main Numbers
```
3 | 6 | 8 | 12 | 17 | 20 | 28
```

**Bonus Number:** 18

### 🤖 DeepSeek AI Analysis

**Confidence Level:** Low (as with all lottery predictions)

**Key Insights:**
- Heavily based on historical frequency (4 of top 5 numbers included)
- Low-number cluster (all ≤28, below mean of 24.86)
- Even-heavy bias (5 even, 2 odd)
- Avoids 30-50 range entirely

**AI Recommendation:** Play if you enjoy frequency-based strategy, but understand it's not more likely than random. Consider adding numbers from 30-50 range for balance.

### 📈 Data Used
- Total Draws Analyzed: 1,013
- Total Numbers: 7,091
- Mean: 24.86
- Median: 25.00
- Range: 1-49

## ⚠️ Important Disclaimer

- Lottery drawings are **COMPLETELY RANDOM**
- Each number has an **equal 1/50 probability** every draw
- Past frequency **DOES NOT** predict future outcomes
- This system is for **ENTERTAINMENT PURPOSES ONLY**
- **Gamble responsibly** - never spend more than you can afford to lose

## 🔄 Files Structure

```
My_lotto_project/
├── weekly_predictions/          # Weekly prediction storage
│   ├── prediction_2026_Week_21.json
│   ├── report_2026_Week_21.txt
│   ├── prediction_2026_Week_22.json
│   └── ...
├── weekly_lotto_predictor.py    # Main prediction engine
├── scheduler.py                 # Automatic weekly runner
├── lotto_analyzer.py            # Analysis core
├── LOTTOMAX.csv                 # Historical data
└── requirements.txt             # Dependencies
```

## 🛠️ Technical Details

- **Backend:** Python 3.13
- **Data Source:** 1,013 draws from LOTTOMAX.csv
- **AI Analysis:** DeepSeek Chat API
- **Messaging:** Telegram Bot API
- **Scheduling:** APSchedule library

## 📝 Next Steps

1. **Get your Telegram Chat ID** (instructions above)
2. **Run first prediction with Telegram:**
   ```bash
   python weekly_lotto_predictor.py --telegram-chat-id YOUR_CHAT_ID
   ```
3. **Setup automatic weekly scheduler:**
   ```bash
   python scheduler.py --telegram-chat-id YOUR_CHAT_ID --day friday --time 18:00
   ```

## 🤔 FAQ

**Q: Why are these numbers more likely to win?**  
A: They're not. Each number has equal probability. These are based on historical frequency, which is entertaining but not predictive.

**Q: Should I spend money on these numbers?**  
A: Only if you enjoy playing the lottery. Treat it as entertainment, not investment.

**Q: How often are predictions generated?**  
A: Weekly (configurable). Default is Monday at 09:00.

**Q: Can I change the prediction criteria?**  
A: Yes, edit `weekly_lotto_predictor.py` - modify the `predict_numbers()` method.

---

**Last Updated:** 2026-05-27  
**System Status:** ✅ Active and Running
