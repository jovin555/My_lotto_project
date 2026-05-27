"""
Lotto Max Data Analyzer
Fetches and analyzes Lotto Max winning numbers from public sources
"""

import pandas as pd
import numpy as np
from collections import Counter
import requests
from datetime import datetime, timedelta
import json

class LottoMaxAnalyzer:
    """Analyze Lotto Max winning numbers"""
    
    def __init__(self):
        self.data = None
        self.winning_numbers = []
        
    def fetch_lotto_data(self):
        """
        Load Lotto Max data from CSV file
        """
        try:
            csv_path = '/home/eva/workspace/My_lotto_project/LOTTOMAX.csv'
            df = pd.read_csv(csv_path)
            
            # Parse the CSV data
            self.data = df.copy()
            self.winning_numbers = []
            
            # Extract numbers from columns
            number_columns = [f'NUMBER DRAWN {i}' for i in range(1, 8)]
            
            for _, row in df.iterrows():
                for col in number_columns:
                    if col in df.columns and pd.notna(row[col]):
                        num = int(row[col])
                        if num > 0:  # Exclude zeros
                            self.winning_numbers.append(num)
            
            print(f"✓ Loaded {len(df)} draws from LOTTOMAX.csv")
            print(f"✓ Total {len(self.winning_numbers)} numbers analyzed")
            return True
        except FileNotFoundError:
            print(f"CSV file not found. Using sample data...")
            self.create_sample_data()
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Using sample data instead...")
            self.create_sample_data()
            return False
    
    def create_sample_data(self):
        """Create sample Lotto Max data for demonstration"""
        # Sample winning numbers from recent draws
        sample_draws = [
            {'date': '2026-05-22', 'numbers': [7, 15, 23, 34, 41, 48, 50]},
            {'date': '2026-05-20', 'numbers': [3, 12, 19, 28, 35, 42, 49]},
            {'date': '2026-05-18', 'numbers': [5, 14, 21, 31, 38, 44, 50]},
            {'date': '2026-05-15', 'numbers': [2, 11, 22, 29, 36, 45, 48]},
            {'date': '2026-05-13', 'numbers': [8, 16, 24, 32, 39, 46, 50]},
            {'date': '2026-05-11', 'numbers': [1, 13, 20, 27, 37, 43, 49]},
            {'date': '2026-05-08', 'numbers': [6, 17, 25, 33, 40, 47, 50]},
            {'date': '2026-05-06', 'numbers': [4, 10, 18, 30, 38, 44, 50]},
            {'date': '2026-05-04', 'numbers': [9, 15, 23, 28, 35, 42, 50]},
            {'date': '2026-04-29', 'numbers': [3, 11, 21, 31, 39, 45, 49]},
        ]
        self.data = pd.DataFrame(sample_draws)
        self.winning_numbers = []
        for nums in self.data['numbers']:
            self.winning_numbers.extend(nums)
    
    def analyze_frequency(self):
        """Analyze frequency of winning numbers"""
        if not self.winning_numbers:
            print("No data available")
            return None
        
        counter = Counter(self.winning_numbers)
        frequency_df = pd.DataFrame(
            counter.items(), 
            columns=['Number', 'Frequency']
        ).sort_values('Frequency', ascending=False)
        
        return frequency_df
    
    def analyze_statistics(self):
        """Provide statistical analysis of numbers"""
        if not self.winning_numbers:
            return None
        
        stats = {
            'Total Draws': len(self.data),
            'Total Numbers': len(self.winning_numbers),
            'Mean': np.mean(self.winning_numbers),
            'Median': np.median(self.winning_numbers),
            'Std Dev': np.std(self.winning_numbers),
            'Min': np.min(self.winning_numbers),
            'Max': np.max(self.winning_numbers),
            'Range': np.max(self.winning_numbers) - np.min(self.winning_numbers),
        }
        return stats
    
    def predict_next_numbers(self, num_predictions=5):
        """
        Predict next numbers based on frequency analysis
        NOTE: This is for statistical interest only. Lottery draws are random.
        """
        frequency_df = self.analyze_frequency()
        
        # Get top numbers by frequency
        top_numbers = frequency_df.head(num_predictions)['Number'].tolist()
        
        # Alternative: numbers that haven't appeared recently
        all_possible = set(range(1, 51))  # Lotto Max is 1-50
        appeared = set(self.winning_numbers)
        not_appeared = list(all_possible - appeared)
        
        return {
            'most_frequent': top_numbers,
            'not_appeared_recently': not_appeared[:num_predictions],
            'random_next': np.random.choice(50, 7, replace=False) + 1
        }
    
    def print_report(self):
        """Print comprehensive analysis report"""
        print("\n" + "="*60)
        print("LOTTO MAX ANALYSIS REPORT")
        print("="*60)
        
        # Statistics
        print("\n📊 STATISTICAL SUMMARY")
        print("-" * 60)
        stats = self.analyze_statistics()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key:.<40} {value:.2f}")
            else:
                print(f"{key:.<40} {value}")
        
        # Frequency Analysis
        print("\n📈 TOP 10 MOST FREQUENT NUMBERS")
        print("-" * 60)
        frequency_df = self.analyze_frequency()
        for idx, row in frequency_df.head(10).iterrows():
            print(f"Number {int(row['Number']):>2} │ Frequency: {int(row['Frequency']):>2} times")
        
        # Predictions
        print("\n🔮 PREDICTED NEXT NUMBERS")
        print("-" * 60)
        predictions = self.predict_next_numbers()
        
        print("Based on frequency analysis:")
        print(f"  Most Likely: {sorted(predictions['most_frequent'])}")
        
        print("\nNot appeared recently (long shots):")
        print(f"  {sorted(predictions['not_appeared_recently'])}")
        
        print("\nRandom prediction (for reference):")
        print(f"  {sorted(predictions['random_next'])}")
        
        print("\n⚠️  DISCLAIMER:")
        print("Lottery drawings are random events. Past frequency does NOT")
        print("predict future draws. Each number has an equal 1/50 chance.")
        print("This analysis is for statistical interest only.")
        print("="*60 + "\n")


if __name__ == "__main__":
    analyzer = LottoMaxAnalyzer()
    analyzer.fetch_lotto_data()
    analyzer.print_report()
    
    # Save frequency data to CSV
    frequency_df = analyzer.analyze_frequency()
    frequency_df.to_csv('/home/eva/workspace/My_lotto_project/frequency_analysis.csv', index=False)
    print("✓ Frequency analysis saved to frequency_analysis.csv")
