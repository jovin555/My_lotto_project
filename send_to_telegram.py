"""
Send Lotto Max Prediction to Telegram
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def send_telegram_message(chat_id, message):
    """Send message to Telegram using bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✓ Message sent to Telegram successfully!")
            return True
        else:
            print(f"✗ Failed to send message. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error sending message: {e}")
        return False

def read_prediction():
    """Read the prediction from file"""
    try:
        with open('/home/eva/workspace/My_lotto_project/next_week_prediction.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("Prediction file not found. Generate prediction first.")
        return None

def format_telegram_message(prediction_text):
    """Format prediction into a nice Telegram message"""
    lines = prediction_text.split('\n')
    
    # Parse the prediction data
    message = "<b>🎰 LOTTO MAX - NEXT WEEK'S PREDICTION</b>\n"
    message += f"<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n\n"
    
    # Extract recommended numbers
    for i, line in enumerate(lines):
        if 'RECOMMENDED NUMBERS:' in line:
            main_line = lines[i+1]
            bonus_line = lines[i+2]
            
            if 'Main:' in main_line:
                numbers = main_line.replace('Main: ', '').strip()
                message += f"<b>Main Numbers:</b>\n<code>{numbers}</code>\n\n"
            
            if 'Bonus:' in bonus_line:
                bonus = bonus_line.replace('Bonus: ', '').strip()
                message += f"<b>Bonus:</b> <code>{bonus}</code>\n\n"
            break
    
    # Add disclaimer
    message += "⚠️ <i>Lottery draws are random. Each number has equal probability.</i>\n"
    message += "<i>For entertainment purposes only. Gamble responsibly.</i>"
    
    return message

def main():
    """Main function"""
    print("="*60)
    print("TELEGRAM LOTTO PREDICTION SENDER")
    print("="*60)
    
    # Check if bot token exists
    if not BOT_TOKEN:
        print("✗ TELEGRAM_BOT_TOKEN not found in .env file")
        return
    
    print("✓ Bot token found")
    
    # Read prediction
    prediction_text = read_prediction()
    if not prediction_text:
        return
    
    # Format message
    message = format_telegram_message(prediction_text)
    
    print("\n📝 Message to be sent:")
    print("-" * 60)
    print(message)
    print("-" * 60)
    
    # Get chat ID from user
    chat_id = input("\nEnter your Telegram Chat ID (or @username): ").strip()
    
    if not chat_id:
        print("✗ Chat ID is required")
        return
    
    # Send message
    print("\nSending to Telegram...")
    if send_telegram_message(chat_id, message):
        print("\n✓ Prediction sent successfully!")
    else:
        print("\n✗ Failed to send prediction")

if __name__ == "__main__":
    main()
