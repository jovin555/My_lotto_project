"""
Lotto Max Next Week Prediction
Generate 7 numbers + bonus based on statistical analysis
"""

import numpy as np
import pandas as pd
from lotto_analyzer import LottoMaxAnalyzer
from datetime import datetime, timedelta
import random

class LottoPredictor:
    """Generate predicted numbers for next Lotto Max draw"""
    
    def __init__(self):
        self.analyzer = LottoMaxAnalyzer()
        self.analyzer.fetch_lotto_data()
        self.frequency_df = self.analyzer.analyze_frequency()
        
    def predict_by_frequency(self, num_count=7):
        """Predict numbers based on frequency analysis"""
        # Get top numbers by frequency
        top_numbers = self.frequency_df.nlargest(num_count, 'Frequency')['Number'].tolist()
        return sorted([int(n) for n in top_numbers])
    
    def predict_by_complementary(self, num_count=7):
        """Predict numbers that haven't appeared recently (contrarian approach)"""
        all_numbers = set(range(1, 51))
        appeared = set(self.analyzer.winning_numbers)
        not_appeared = list(all_numbers - appeared)
        
        # Sort by least recent appearance for numbers that did appear
        recent_appeared = list(appeared)
        
        # Mix: some numbers that haven't appeared + some recent ones
        complement_count = min(len(not_appeared), num_count // 2)
        predictions = not_appeared[:complement_count]
        
        # Fill remaining with less frequent numbers
        least_frequent = self.frequency_df.nsmallest(num_count - complement_count, 'Frequency')['Number'].tolist()
        predictions.extend([int(n) for n in least_frequent[:num_count - complement_count]])
        
        return sorted(predictions[:num_count])
    
    def predict_by_middle_range(self, num_count=7):
        """Predict numbers around the statistical mean"""
        mean = self.analyzer.analyze_statistics()['Mean']
        std_dev = self.analyzer.analyze_statistics()['Std Dev']
        
        # Numbers within 1 standard deviation of mean
        lower = mean - std_dev
        upper = mean + std_dev
        
        candidates = [n for n in range(1, 51) if lower <= n <= upper]
        
        # Pick balanced distribution
        if len(candidates) >= num_count:
            # Take evenly spaced numbers from candidates
            step = len(candidates) // num_count
            predictions = [candidates[i * step] for i in range(num_count)]
        else:
            predictions = candidates + random.sample(
                [n for n in range(1, 51) if n not in candidates],
                num_count - len(candidates)
            )
        
        return sorted(predictions[:num_count])
    
    def predict_balanced_distribution(self, num_count=7):
        """Predict numbers with balanced distribution across ranges"""
        # Divide 1-50 into ranges and pick from each
        ranges = [
            (1, 10),
            (11, 20),
            (21, 30),
            (31, 40),
            (41, 50)
        ]
        
        predictions = []
        
        # Get frequency data for each range
        for start, end in ranges:
            range_freq = self.frequency_df[
                (self.frequency_df['Number'] >= start) & 
                (self.frequency_df['Number'] <= end)
            ].nlargest(2, 'Frequency')
            
            if len(range_freq) > 0:
                predictions.extend(range_freq['Number'].tolist()[:1])
        
        # Fill remaining slots with highest frequency overall
        while len(predictions) < num_count:
            top = self.frequency_df.nlargest(10, 'Frequency')['Number'].tolist()
            for num in top:
                if num not in predictions and len(predictions) < num_count:
                    predictions.append(num)
        
        return sorted([int(n) for n in predictions[:num_count]])
    
    def generate_bonus_number(self, main_numbers):
        """Generate bonus number (usually 1-50)"""
        # Pick from high frequency numbers but not in main set
        candidates = self.frequency_df[
            ~self.frequency_df['Number'].isin(main_numbers)
        ].nlargest(10, 'Frequency')['Number'].tolist()
        
        bonus = int(random.choice(candidates)) if candidates else random.randint(1, 50)
        while bonus in main_numbers:
            bonus = random.randint(1, 50)
        
        return bonus
    
    def generate_predictions(self):
        """Generate final prediction with multiple strategies"""
        print("\n" + "="*70)
        print("🎰 LOTTO MAX - NEXT WEEK'S PREDICTION")
        print("="*70)
        
        # Calculate next draw date (typically Tuesday and Friday)
        today = datetime.now()
        days_ahead = 1 - today.weekday()  # Tuesday is 1
        if days_ahead <= 0:
            days_ahead += 7
        
        next_draw = today + timedelta(days=days_ahead)
        print(f"\n📅 Predicted Draw Date: {next_draw.strftime('%A, %B %d, %Y')}")
        
        # Generate predictions using different methods
        predictions = {
            'Frequency-Based': self.predict_by_frequency(),
            'Balanced Distribution': self.predict_balanced_distribution(),
            'Contrarian (Not Appeared)': self.predict_by_complementary(),
            'Middle Range (Mean ± 1 SD)': self.predict_by_middle_range(),
        }
        
        # Primary prediction: use frequency-based (most statistical)
        primary = predictions['Frequency-Based']
        bonus = self.generate_bonus_number(primary)
        
        # Display predictions
        print("\n" + "-"*70)
        print("🎯 PRIMARY PREDICTION (RECOMMENDED)")
        print("-"*70)
        print(f"Main Numbers: {' | '.join([f'{n:>2}' for n in primary])}")
        print(f"Bonus Number: {bonus}")
        self.show_confidence_analysis(primary)
        
        print("\n" + "-"*70)
        print("📊 ALTERNATIVE STRATEGIES")
        print("-"*70)
        
        for strategy_name, numbers in predictions.items():
            if strategy_name != 'Frequency-Based':
                bonus_alt = self.generate_bonus_number(numbers)
                print(f"\n{strategy_name}:")
                print(f"  Main: {' | '.join([f'{n:>2}' for n in numbers])}")
                print(f"  Bonus: {bonus_alt}")
        
        # Statistics about the predictions
        print("\n" + "-"*70)
        print("📈 PREDICTION STATISTICS")
        print("-"*70)
        self.show_prediction_stats(primary)
        
        # Disclaimer
        print("\n" + "-"*70)
        print("⚠️  IMPORTANT DISCLAIMER")
        print("-"*70)
        print("• Lottery drawings are RANDOM events")
        print("• Each number has equal probability (1/50) regardless of history")
        print("• Past performance does NOT guarantee future results")
        print("• This is for entertainment purposes only")
        print("• Please gamble responsibly")
        print("="*70 + "\n")
        
        return primary, bonus, predictions
    
    def show_confidence_analysis(self, numbers):
        """Show confidence level for predicted numbers"""
        print("\n✓ Confidence Analysis:")
        total_freq = self.analyzer.analyze_statistics()['Total Numbers']
        
        for num in numbers:
            freq_row = self.frequency_df[self.frequency_df['Number'] == num]
            if not freq_row.empty:
                frequency = int(freq_row['Frequency'].values[0])
                percentage = (frequency / total_freq) * 100
                confidence = "★★★" if percentage > 5 else "★★" if percentage > 2 else "★"
                print(f"  Number {num:>2}: Appeared {frequency} times ({percentage:.1f}%) {confidence}")
    
    def show_prediction_stats(self, numbers):
        """Show statistics about the predicted numbers"""
        mean_pred = np.mean(numbers)
        median_pred = np.median(numbers)
        std_pred = np.std(numbers)
        
        stats = self.analyzer.analyze_statistics()
        
        print(f"Predicted Mean: {mean_pred:.1f} (Historical: {stats['Mean']:.1f})")
        print(f"Predicted Median: {median_pred:.1f} (Historical: {stats['Median']:.1f})")
        print(f"Predicted Range: {min(numbers)}-{max(numbers)} (Historical: {int(stats['Min'])}-{int(stats['Max'])})")
        print(f"\nPredicted numbers spread across all ranges:")
        
        # Show distribution
        ranges = [(1,10), (11,20), (21,30), (31,40), (41,50)]
        for start, end in ranges:
            count = sum(1 for n in numbers if start <= n <= end)
            bar = "█" * count + "░" * (max(0, 2-count))
            print(f"  {start:>2}-{end:<2}: {bar} ({count})")


if __name__ == "__main__":
    predictor = LottoPredictor()
    main_nums, bonus_num, all_predictions = predictor.generate_predictions()
    
    # Save prediction to file
    with open('/home/eva/workspace/My_lotto_project/next_week_prediction.txt', 'w') as f:
        f.write(f"LOTTO MAX - NEXT WEEK'S PREDICTION\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"RECOMMENDED NUMBERS:\n")
        f.write(f"Main: {' '.join([str(n) for n in main_nums])}\n")
        f.write(f"Bonus: {bonus_num}\n\n")
        f.write(f"ALTERNATIVE PREDICTIONS:\n")
        for strategy, numbers in all_predictions.items():
            f.write(f"{strategy}: {' '.join([str(n) for n in numbers])}\n")
    
    print("✓ Prediction saved to: next_week_prediction.txt")
