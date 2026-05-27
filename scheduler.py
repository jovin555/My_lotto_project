"""
Lotto Max Weekly Scheduler
Automatically runs predictions and sends to Telegram weekly
"""

import schedule
import time
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def run_weekly_prediction(telegram_chat_id=None):
    """Run the weekly prediction"""
    print(f"\n[{datetime.now()}] Starting weekly prediction run...")
    
    # Use env chat ID if not provided
    if not telegram_chat_id:
        telegram_chat_id = TELEGRAM_CHAT_ID
    
    try:
        from weekly_lotto_predictor import WeeklyLottoPredictor
        
        predictor = WeeklyLottoPredictor()
        result = predictor.run_weekly_prediction(telegram_chat_id)
        
        print(f"[{datetime.now()}] ✓ Weekly prediction completed successfully!")
        return True
    
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

def setup_scheduler(telegram_chat_id=None, day_of_week='monday', time_of_day='09:00'):
    """
    Setup scheduler to run weekly predictions
    
    Args:
        telegram_chat_id: Telegram chat ID for sending predictions
        day_of_week: Day to run prediction (monday-sunday)
        time_of_day: Time to run (HH:MM format)
    """
    
    # Use env chat ID if not provided
    if not telegram_chat_id:
        telegram_chat_id = TELEGRAM_CHAT_ID
    
    print("="*70)
    print("LOTTO MAX WEEKLY SCHEDULER")
    print("="*70)
    print(f"Scheduling weekly prediction for: {day_of_week.upper()} at {time_of_day}")
    
    if telegram_chat_id:
        print(f"✓ Telegram Chat ID: {telegram_chat_id}")
    else:
        print("⚠️  Telegram Chat ID not configured (predictions won't be auto-sent)")
    
    # Schedule the job
    schedule_func = getattr(schedule.every(), day_of_week)
    job = schedule_func.at(time_of_day).do(run_weekly_prediction, telegram_chat_id=telegram_chat_id)
    
    print("\n✓ Scheduler initialized and running...")
    print("📅 Next prediction will run at the scheduled time")
    print("📁 Predictions saved to: /home/eva/workspace/My_lotto_project/weekly_predictions/")
    print("📱 Messages sent to Telegram Chat ID: " + str(telegram_chat_id))
    print("\nPress Ctrl+C to stop scheduler\n")
    
    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    except KeyboardInterrupt:
        print("\n\n✓ Scheduler stopped")

if __name__ == "__main__":
    # Parse arguments
    telegram_chat_id = None
    day_of_week = 'monday'
    time_of_day = '09:00'
    
    if '--telegram-chat-id' in sys.argv:
        idx = sys.argv.index('--telegram-chat-id')
        if idx + 1 < len(sys.argv):
            telegram_chat_id = sys.argv[idx + 1]
    
    if '--day' in sys.argv:
        idx = sys.argv.index('--day')
        if idx + 1 < len(sys.argv):
            day_of_week = sys.argv[idx + 1].lower()
    
    if '--time' in sys.argv:
        idx = sys.argv.index('--time')
        if idx + 1 < len(sys.argv):
            time_of_day = sys.argv[idx + 1]
    
    setup_scheduler(telegram_chat_id, day_of_week, time_of_day)
