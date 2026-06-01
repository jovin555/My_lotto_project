"""
Weekly Lotto Max Predictor with DeepSeek AI Review & Telegram Integration
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from lotto_analyzer import LottoMaxAnalyzer

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DEEPSEEK_API_KEY = os.getenv('LLM_API_KEY')
DEEPSEEK_MODEL = os.getenv('LLM_MODEL', 'deepseek-chat')

class WeeklyLottoPredictor:
    """Generate and manage weekly Lotto Max predictions"""
    
    def __init__(self):
        self.analyzer = LottoMaxAnalyzer()
        self.analyzer.fetch_lotto_data()
        self.predictions_dir = Path('/home/eva/workspace/My_lotto_project/weekly_predictions')
        self.predictions_dir.mkdir(exist_ok=True)
    
    def predict_numbers(self, num_count=7):
        """Generate predicted numbers using evidence-based rules from 1,212-draw analysis:
        - Exclude #50 (drawn 42% below expected — strongest outlier)
        - 3 odd/4 even or 4 odd/3 even split (covers 58% of all historical draws)
        - At least one consecutive pair (present in 63% of draws)
        - Sum between 156–196 (central distribution sweet spot)
        - Spread across low (1-17), mid (18-33), high (34-50) ranges
        - Weighted by historical frequency
        """
        import random

        frequency_df = self.analyzer.analyze_frequency()

        # Build frequency weights; zero-out #50, reduce high-end numbers
        weights = {}
        for _, row in frequency_df.iterrows():
            n = int(row['Number'])
            if n == 50:
                weights[n] = 0          # exclude #50
            elif n > 48:
                weights[n] = int(row['Frequency']) * 0.3
            else:
                weights[n] = int(row['Frequency'])

        pool = [n for n in range(1, 50) if n != 50]  # 1-49

        def pick_weighted(exclude=set()):
            candidates = [n for n in pool if n not in exclude]
            w = [weights.get(n, 1) for n in candidates]
            return random.choices(candidates, weights=w, k=1)[0]

        def satisfies_rules(nums):
            s = sorted(nums)
            total = sum(s)
            odds = sum(1 for n in s if n % 2 == 1)
            has_consec = any(s[i+1] - s[i] == 1 for i in range(len(s)-1))
            low  = sum(1 for n in s if n <= 17)
            mid  = sum(1 for n in s if 18 <= n <= 33)
            high = sum(1 for n in s if n >= 34)
            spread_ok = low >= 1 and mid >= 1 and high >= 1
            odd_even_ok = odds in (3, 4)
            sum_ok = 156 <= total <= 196
            return has_consec and odd_even_ok and sum_ok and spread_ok

        # Try up to 50,000 times to find a valid combination
        for _ in range(50000):
            chosen = set()
            while len(chosen) < num_count:
                chosen.add(pick_weighted(chosen))
            if satisfies_rules(chosen):
                return sorted(chosen)

        # Fallback: relax sum constraint only if no valid set found
        for _ in range(10000):
            chosen = set()
            while len(chosen) < num_count:
                chosen.add(pick_weighted(chosen))
            s = sorted(chosen)
            odds = sum(1 for n in s if n % 2 == 1)
            has_consec = any(s[i+1] - s[i] == 1 for i in range(len(s)-1))
            if has_consec and odds in (3, 4):
                return s

        return sorted(random.sample(pool, num_count))

    def get_bonus_number(self, main_numbers):
        """Pick bonus from top-frequency numbers not in main set, avoiding #50"""
        import random
        frequency_df = self.analyzer.analyze_frequency()
        candidates = frequency_df[
            (~frequency_df['Number'].isin(main_numbers)) &
            (frequency_df['Number'] != 50)
        ].nlargest(15, 'Frequency')['Number'].tolist()
        return int(random.choice(candidates)) if candidates else random.randint(1, 49)
    
    def save_weekly_prediction(self, main_numbers, bonus_number):
        """Save prediction with timestamp"""
        week_date = datetime.now().strftime('%Y_Week_%U')
        filename = self.predictions_dir / f"prediction_{week_date}.json"
        
        prediction_data = {
            'week': week_date,
            'date_generated': datetime.now().isoformat(),
            'main_numbers': main_numbers,
            'bonus_number': bonus_number,
            'next_draw_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'statistics': {
                'total_draws_analyzed': len(self.analyzer.data),
                'total_numbers_analyzed': len(self.analyzer.winning_numbers),
                'mean': float(self.analyzer.analyze_statistics()['Mean']),
                'median': float(self.analyzer.analyze_statistics()['Median']),
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(prediction_data, f, indent=2)
        
        print(f"✓ Prediction saved to: {filename}")
        return prediction_data
    
    def get_deepseek_analysis(self, main_numbers, bonus_number):
        """Get DeepSeek AI analysis of the predictions"""
        
        prompt = f"""Analyze these Lotto Max predictions and provide insights:

Main Numbers: {main_numbers}
Bonus Number: {bonus_number}

Based on historical Lotto Max data (1,212 draws, Sep 2009 – May 2026):
- Number range: 1–50
- Average draw sum: 175.7 (sweet spot: 156–196)
- Most frequent numbers: 19, 28, 7, 39, 2, 30, 36, 22, 38, 18
- Least frequent: #50 (98x — major outlier, ~42% below expected), 49, 33
- 62.9% of draws contain at least one consecutive pair
- 58.4% of draws are 3-odd/4-even or 4-odd/3-even
- Top bonus numbers: 18, 10, 38, 46, 27
- Notable 6-combo that appeared twice: [7, 10, 11, 19, 34, 45]

Rules applied to generate this prediction:
✓ #50 excluded
✓ Odd/even balance enforced (3/4 or 4/3)
✓ At least one consecutive pair included
✓ Sum target: 156–196
✓ Spread across low (1-17), mid (18-33), high (34-50)
✓ Weighted by historical frequency

Please provide:
1. Brief assessment of how well this ticket follows the statistical rules
2. Confidence level (High/Medium/Low) and reasoning
3. Any notable patterns in this specific combination
4. One thing that could make this ticket stronger
5. Short recommendation for the player

Keep response concise and actionable."""

        try:
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                analysis = response.json()['choices'][0]['message']['content']
                print("✓ DeepSeek analysis received")
                return analysis
            else:
                print(f"✗ DeepSeek API error: {response.status_code}")
                return "Unable to get AI analysis at this time."
        
        except Exception as e:
            print(f"✗ Error connecting to DeepSeek: {e}")
            return "Unable to get AI analysis at this time."
    
    def send_to_telegram(self, chat_id, main_numbers, bonus_number, ai_analysis):
        """Send prediction to Telegram with AI analysis"""
        
        s = sorted(main_numbers)
        odds = sum(1 for n in s if n % 2 == 1)
        total_sum = sum(s)
        has_consec = any(s[i+1] - s[i] == 1 for i in range(len(s)-1))

        message = f"""<b>🎰 LOTTO MAX WEEKLY PREDICTION</b>
<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>

<b>📊 Predicted Numbers:</b>
<code>{' | '.join([str(n) for n in main_numbers])}</code>

<b>🎁 Bonus:</b> <code>{bonus_number}</code>

<b>✅ Rules Check (1,212-draw analysis):</b>
• #50 excluded: {'✓' if 50 not in main_numbers else '✗'}
• Odd/Even: {odds}/{7-odds} {'✓' if odds in (3,4) else '✗'}
• Consecutive pair: {'✓' if has_consec else '✗'}
• Sum {total_sum}: {'✓' if 156<=total_sum<=196 else '✗ (target 156-196)'}

<b>🤖 DeepSeek AI Analysis:</b>
<i>{ai_analysis[:500]}...</i>

<b>📈 Data:</b> 1,212 draws analyzed (Sep 2009 – May 2026)

⚠️ <i>Lottery is random. For entertainment only.</i>
<i>Gamble responsibly.</i>"""
        
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
                print(f"✗ Telegram error: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error sending to Telegram: {e}")
            return False
    
    def generate_full_report(self, main_numbers, bonus_number, ai_analysis):
        """Generate comprehensive weekly report"""
        
        week_date = datetime.now().strftime('%Y_Week_%U')
        report_filename = self.predictions_dir / f"report_{week_date}.txt"
        
        stats = self.analyzer.analyze_statistics()
        frequency_df = self.analyzer.analyze_frequency()
        top_10 = frequency_df.head(10)
        
        s = sorted(main_numbers)
        odds = sum(1 for n in s if n % 2 == 1)
        evens = 7 - odds
        total_sum = sum(s)
        has_consec = any(s[i+1] - s[i] == 1 for i in range(len(s)-1))
        low_count  = sum(1 for n in s if n <= 17)
        mid_count  = sum(1 for n in s if 18 <= n <= 33)
        high_count = sum(1 for n in s if n >= 34)

        report = f"""
{'='*70}
LOTTO MAX - WEEKLY PREDICTION REPORT
{'='*70}

📅 Report Date: {datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')}
📊 Week: {week_date}

{'='*70}
🎯 RECOMMENDED NUMBERS
{'='*70}

Main Numbers: {' | '.join([str(n) for n in main_numbers])}
Bonus Number: {bonus_number}

{'='*70}
✅ RULES VALIDATION (based on 1,212-draw analysis)
{'='*70}

  #50 excluded:           {'✓ Yes' if 50 not in main_numbers else '✗ No'}
  Odd/Even split:         {odds} odd / {evens} even  {'✓' if odds in (3,4) else '✗ (target: 3/4 or 4/3)'}
  Consecutive pair:       {'✓ Yes' if has_consec else '✗ None found'}
  Sum ({total_sum}):        {'✓ In range' if 156 <= total_sum <= 196 else f'✗ Outside 156-196'}
  Range spread:           Low={low_count} Mid={mid_count} High={high_count}  {'✓' if low_count>=1 and mid_count>=1 and high_count>=1 else '✗'}

{'='*70}
📈 STATISTICAL ANALYSIS
{'='*70}

Data Analyzed:
  - Total Draws: {stats['Total Draws']}
  - Total Numbers: {stats['Total Numbers']}
  - Mean: {stats['Mean']:.2f}
  - Median: {stats['Median']:.2f}
  - Std Dev: {stats['Std Dev']:.2f}
  - Range: {int(stats['Min'])} - {int(stats['Max'])}

Top 10 Most Frequent Numbers:
"""
        for idx, row in top_10.iterrows():
            report += f"  {int(row['Number']):>2}. Number {int(row['Number']):>2} - {int(row['Frequency']):>3} times\n"
        
        report += f"""
{'='*70}
🤖 DEEPSEEK AI EXPERT ANALYSIS
{'='*70}

{ai_analysis}

{'='*70}
⚠️ DISCLAIMER
{'='*70}

• Lottery drawings are completely RANDOM events
• Each number has equal probability (1/50) in every draw
• Past frequency does NOT predict future outcomes
• This prediction is for ENTERTAINMENT PURPOSES ONLY
• Please gamble responsibly
• Never spend more than you can afford to lose

{'='*70}

Generated by: Lotto Max AI Predictor v2.0
Next prediction will be generated next week.

"""
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"✓ Full report saved to: {report_filename}")
        return report
    
    def run_weekly_prediction(self, telegram_chat_id=None):
        """Run complete weekly prediction workflow"""
        
        # Use chat ID from env if not provided as argument
        if not telegram_chat_id:
            telegram_chat_id = TELEGRAM_CHAT_ID
        
        print("\n" + "="*70)
        print("🎰 WEEKLY LOTTO MAX PREDICTION ENGINE")
        print("="*70)
        
        # Generate predictions
        print("\n1️⃣ Generating predictions...")
        main_numbers = self.predict_numbers()
        bonus_number = self.get_bonus_number(main_numbers)
        print(f"   Main: {main_numbers}")
        print(f"   Bonus: {bonus_number}")
        
        # Save prediction
        print("\n2️⃣ Saving prediction data...")
        prediction_data = self.save_weekly_prediction(main_numbers, bonus_number)
        
        # Get AI analysis
        print("\n3️⃣ Getting DeepSeek AI analysis...")
        ai_analysis = self.get_deepseek_analysis(main_numbers, bonus_number)
        print(f"   Analysis length: {len(ai_analysis)} characters")
        
        # Generate full report
        print("\n4️⃣ Generating full report...")
        report = self.generate_full_report(main_numbers, bonus_number, ai_analysis)
        
        # Send to Telegram if chat_id provided
        if telegram_chat_id:
            print(f"\n5️⃣ Sending to Telegram (Chat ID: {telegram_chat_id})...")
            self.send_to_telegram(telegram_chat_id, main_numbers, bonus_number, ai_analysis)
        else:
            print("\n5️⃣ Telegram Chat ID not provided. Skipping Telegram send.")
            print("   To send predictions, run with --telegram-chat-id option")
        
        print("\n" + "="*70)
        print("✓ WEEKLY PREDICTION COMPLETE")
        print("="*70)
        
        return {
            'prediction': prediction_data,
            'analysis': ai_analysis,
            'report': report
        }


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    telegram_chat_id = None
    if '--telegram-chat-id' in sys.argv:
        idx = sys.argv.index('--telegram-chat-id')
        if idx + 1 < len(sys.argv):
            telegram_chat_id = sys.argv[idx + 1]
    
    predictor = WeeklyLottoPredictor()
    result = predictor.run_weekly_prediction(telegram_chat_id)
