#!/usr/bin/env python3
"""
Interactive Telegram Setup for Lotto Max Predictions
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def test_telegram_connection():
    """Test if Telegram connection works"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            return True, bot_info['first_name']
        else:
            return False, None
    except Exception as e:
        return False, str(e)

def send_prediction_to_telegram(chat_id):
    """Send the weekly prediction to Telegram"""
    
    # Read the prediction data
    import json
    from pathlib import Path
    
    predictions_dir = Path('/home/eva/workspace/My_lotto_project/weekly_predictions')
    
    # Find the latest prediction
    prediction_files = sorted(predictions_dir.glob('prediction_*.json'))
    if not prediction_files:
        print("✗ No prediction files found!")
        return False
    
    latest_prediction = prediction_files[-1]
    
    with open(latest_prediction, 'r') as f:
        pred_data = json.load(f)
    
    # Read the report
    report_file = predictions_dir / f"report_{pred_data['week']}.txt"
    with open(report_file, 'r') as f:
        report_content = f.read()
    
    # Prepare message
    main_nums = pred_data['main_numbers']
    bonus = pred_data['bonus_number']
    
    message = f"""<b>🎰 LOTTO MAX WEEKLY PREDICTION</b>

<b>📊 Week:</b> {pred_data['week']}
<b>Generated:</b> {pred_data['date_generated'][:10]}

<b>🎯 Predicted Numbers:</b>
<code>{' | '.join([str(n) for n in main_nums])}</code>

<b>🎁 Bonus:</b> <code>{bonus}</code>

<b>📈 Data:</b> {pred_data['statistics']['total_draws_analyzed']} draws analyzed
<b>Mean:</b> {pred_data['statistics']['mean']:.2f} | <b>Median:</b> {pred_data['statistics']['median']:.1f}

<b>🤖 DeepSeek AI Analysis:</b>
Available in saved report file (full analysis included).

⚠️ <i>Lottery is random. Each number has equal 1/50 probability.</i>
<i>For entertainment only. Gamble responsibly.</i>"""

    # Send to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✓ Prediction sent to Telegram successfully!")
            return True
        else:
            print(f"✗ Failed to send. Telegram error: {response.status_code}")
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ Error sending message: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🤖 LOTTO MAX - TELEGRAM SETUP WIZARD")
    print("="*70)
    
    # Test connection
    print("\n1️⃣ Testing Telegram connection...")
    connected, bot_name = test_telegram_connection()
    
    if not connected:
        print(f"✗ Failed to connect to Telegram: {bot_name}")
        print("Please check your TELEGRAM_BOT_TOKEN in .env file")
        return
    
    print(f"✓ Connected! Bot: {bot_name}")
    
    # Get Chat ID
    print("\n2️⃣ Getting your Telegram Chat ID...")
    print("\nTo find your Chat ID:")
    print("  1. Open Telegram")
    print("  2. Search for @userinfobot")
    print("  3. Send /start")
    print("  4. Bot will show your Chat ID")
    
    chat_id = input("\nEnter your Telegram Chat ID: ").strip()
    
    if not chat_id:
        print("✗ Chat ID is required!")
        return
    
    # Send prediction
    print(f"\n3️⃣ Sending this week's prediction to {chat_id}...")
    if send_prediction_to_telegram(chat_id):
        print("\n✓ SUCCESS! You will now receive:")
        print("  • Weekly predictions every chosen day")
        print("  • DeepSeek AI analysis")
        print("  • Statistical insights")
        print("\nTo setup automatic weekly predictions, run:")
        print(f"  python scheduler.py --telegram-chat-id {chat_id}")
    else:
        print("\n✗ Failed to send prediction")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
