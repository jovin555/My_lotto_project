"""
Lotto Max Data Visualization
Generate plots and charts for statistical analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from lotto_analyzer import LottoMaxAnalyzer

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

def create_visualizations():
    """Generate and save all visualization plots"""
    
    # Initialize analyzer and fetch data
    analyzer = LottoMaxAnalyzer()
    analyzer.fetch_lotto_data()
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Frequency Bar Chart
    ax1 = plt.subplot(2, 3, 1)
    frequency_df = analyzer.analyze_frequency()
    top_15 = frequency_df.head(15)
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_15)))
    bars = ax1.bar(top_15['Number'].astype(str), top_15['Frequency'], color=colors)
    ax1.set_xlabel('Number', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=10, fontweight='bold')
    ax1.set_title('Top 15 Most Frequent Numbers', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=8)
    
    # 2. Histogram of All Numbers
    ax2 = plt.subplot(2, 3, 2)
    ax2.hist(analyzer.winning_numbers, bins=25, color='steelblue', edgecolor='black', alpha=0.7)
    ax2.axvline(np.mean(analyzer.winning_numbers), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {np.mean(analyzer.winning_numbers):.1f}')
    ax2.axvline(np.median(analyzer.winning_numbers), color='green', linestyle='--', 
                linewidth=2, label=f'Median: {np.median(analyzer.winning_numbers):.1f}')
    ax2.set_xlabel('Number', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Count', fontsize=10, fontweight='bold')
    ax2.set_title('Distribution of All Winning Numbers', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Box Plot
    ax3 = plt.subplot(2, 3, 3)
    box = ax3.boxplot(analyzer.winning_numbers, vert=True, patch_artist=True,
                       widths=0.5, showmeans=True)
    box['boxes'][0].set_facecolor('lightblue')
    box['medians'][0].set_color('red')
    box['means'][0].set_marker('D')
    box['means'][0].set_markerfacecolor('green')
    ax3.set_ylabel('Number Value', fontsize=10, fontweight='bold')
    ax3.set_title('Box Plot - Statistical Distribution', fontsize=12, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    ax3.set_xticklabels(['Winning Numbers'])
    
    # Add statistics text
    stats = analyzer.analyze_statistics()
    stats_text = f"Min: {stats['Min']}\nQ1: {np.percentile(analyzer.winning_numbers, 25):.1f}\n"
    stats_text += f"Median: {stats['Median']:.1f}\nQ3: {np.percentile(analyzer.winning_numbers, 75):.1f}\nMax: {stats['Max']}"
    ax3.text(1.15, np.mean(analyzer.winning_numbers), stats_text, fontsize=9, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 4. Pie Chart - Numbers That Appeared vs Not Appeared
    ax4 = plt.subplot(2, 3, 4)
    all_numbers = set(range(1, 51))
    appeared = set(analyzer.winning_numbers)
    not_appeared = len(all_numbers - appeared)
    appeared_count = len(appeared)
    
    sizes = [appeared_count, not_appeared]
    labels = [f'Appeared\n({appeared_count} numbers)', f'Not Appeared\n({not_appeared} numbers)']
    colors_pie = ['#ff9999', '#66b3ff']
    explode = (0.05, 0)
    ax4.pie(sizes, explode=explode, labels=labels, colors=colors_pie, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
    ax4.set_title('Coverage Analysis', fontsize=12, fontweight='bold')
    
    # 5. Cumulative Frequency
    ax5 = plt.subplot(2, 3, 5)
    sorted_freq = frequency_df.sort_values('Frequency', ascending=False).reset_index(drop=True)
    cumulative = sorted_freq['Frequency'].cumsum()
    ax5.plot(range(len(cumulative)), cumulative.values, marker='o', linewidth=2, 
             markersize=4, color='darkblue')
    ax5.fill_between(range(len(cumulative)), cumulative.values, alpha=0.3, color='skyblue')
    ax5.set_xlabel('Number Rank', fontsize=10, fontweight='bold')
    ax5.set_ylabel('Cumulative Frequency', fontsize=10, fontweight='bold')
    ax5.set_title('Cumulative Frequency Distribution', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. Statistics Summary Table
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    stats = analyzer.analyze_statistics()
    table_data = [
        ['Metric', 'Value'],
        ['Total Draws', f"{stats['Total Draws']}"],
        ['Total Numbers', f"{stats['Total Numbers']}"],
        ['Mean', f"{stats['Mean']:.2f}"],
        ['Median', f"{stats['Median']:.2f}"],
        ['Std Dev', f"{stats['Std Dev']:.2f}"],
        ['Min', f"{int(stats['Min'])}"],
        ['Max', f"{int(stats['Max'])}"],
        ['Range', f"{int(stats['Range'])}"],
        ['Unique Numbers', f"{appeared_count}"],
        ['Coverage', f"{(appeared_count/50)*100:.1f}%"],
    ]
    
    table = ax6.table(cellText=table_data, cellLoc='left', loc='center',
                      colWidths=[0.5, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header row
    for i in range(2):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data)):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
            else:
                table[(i, j)].set_facecolor('#ffffff')
    
    ax6.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('/home/eva/workspace/My_lotto_project/lotto_analysis_plots.png', dpi=300, bbox_inches='tight')
    print("✓ Main analysis plots saved to: lotto_analysis_plots.png")
    
    # Create individual detailed plots
    create_detailed_plots(analyzer)

def create_detailed_plots(analyzer):
    """Create individual detailed plots for each analysis type"""
    
    frequency_df = analyzer.analyze_frequency()
    
    # Plot 1: Full frequency chart for all numbers
    fig, ax = plt.subplots(figsize=(14, 6))
    all_freq = frequency_df.sort_values('Number')
    colors_freq = plt.cm.RdYlGn(np.linspace(0, 1, len(all_freq)))
    ax.bar(all_freq['Number'].astype(str), all_freq['Frequency'], color=colors_freq, edgecolor='black')
    ax.set_xlabel('Lottery Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (Times Won)', fontsize=12, fontweight='bold')
    ax.set_title('Frequency of All Lottery Numbers (1-50)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    plt.savefig('/home/eva/workspace/My_lotto_project/frequency_chart.png', dpi=300, bbox_inches='tight')
    print("✓ Detailed frequency chart saved to: frequency_chart.png")
    plt.close()
    
    # Plot 2: Scatter plot of winning numbers over time
    fig, ax = plt.subplots(figsize=(14, 6))
    draw_number = []
    number_value = []
    
    # Handle both old format (with 'numbers' column) and new format (CSV columns)
    if 'numbers' in analyzer.data.columns:
        for idx, row in analyzer.data.iterrows():
            for num in row['numbers']:
                draw_number.append(idx + 1)
                number_value.append(num)
    else:
        # New CSV format
        number_columns = [f'NUMBER DRAWN {i}' for i in range(1, 8)]
        draw_idx = 0
        for _, row in analyzer.data.iterrows():
            for col in number_columns:
                if col in analyzer.data.columns and pd.notna(row[col]):
                    num = int(row[col])
                    if num > 0:
                        draw_number.append(draw_idx)
                        number_value.append(num)
            draw_idx += 1
    
    scatter = ax.scatter(draw_number, number_value, s=100, alpha=0.6, 
                        c=number_value, cmap='viridis', edgecolors='black', linewidth=1)
    ax.set_xlabel('Draw Number (Chronological Order)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Winning Number', fontsize=12, fontweight='bold')
    ax.set_title('Winning Numbers Over Time', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 51)
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Number Value', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/eva/workspace/My_lotto_project/numbers_over_time.png', dpi=300, bbox_inches='tight')
    print("✓ Numbers over time plot saved to: numbers_over_time.png")
    plt.close()
    
    # Plot 3: Top vs Bottom numbers
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    top_10 = frequency_df.head(10)
    bottom_10 = frequency_df.tail(10)
    
    ax1.barh(top_10['Number'].astype(str), top_10['Frequency'], color='#2ecc71', edgecolor='black')
    ax1.set_xlabel('Frequency', fontsize=11, fontweight='bold')
    ax1.set_title('Top 10 Most Frequent Numbers', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()
    
    ax2.barh(bottom_10['Number'].astype(str), bottom_10['Frequency'], color='#e74c3c', edgecolor='black')
    ax2.set_xlabel('Frequency', fontsize=11, fontweight='bold')
    ax2.set_title('Numbers Appearing Least Frequently', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig('/home/eva/workspace/My_lotto_project/top_vs_bottom.png', dpi=300, bbox_inches='tight')
    print("✓ Top vs Bottom numbers plot saved to: top_vs_bottom.png")
    plt.close()

if __name__ == "__main__":
    print("Generating Lotto Max visualizations...\n")
    create_visualizations()
    print("\n✓ All visualizations complete!")
    print("Generated files:")
    print("  - lotto_analysis_plots.png (comprehensive overview)")
    print("  - frequency_chart.png (detailed frequency)")
    print("  - numbers_over_time.png (temporal analysis)")
    print("  - top_vs_bottom.png (comparison chart)")
