"""
Lotto Max Data Visualization
Updated with evidence-based plots from 1,212-draw analysis
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from collections import Counter
from itertools import combinations
from pathlib import Path

sns.set_style("whitegrid")
PLOTS_DIR = Path('/home/eva/workspace/My_lotto_project/plots')
PLOTS_DIR.mkdir(exist_ok=True)

# ── helpers ──────────────────────────────────────────────────────────────────

def load_main_draws():
    """Load only main draws (SEQUENCE NUMBER == 0) with valid numbers (1-50)."""
    draws = []
    with open(PLOTS_DIR / 'LOTTOMAX.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['SEQUENCE NUMBER'] != '0':
                continue
            nums = []
            for i in range(1, 8):
                v = int(row[f'NUMBER DRAWN {i}'])
                if 1 <= v <= 50:
                    nums.append(v)
            bonus = int(row['BONUS NUMBER'])
            if len(nums) == 7:
                draws.append({
                    'draw': int(row['DRAW NUMBER']),
                    'date': row['DRAW DATE'],
                    'nums': sorted(nums),
                    'bonus': bonus if 1 <= bonus <= 50 else None,
                })
    return draws


def freq_weights(draws):
    all_nums = [n for d in draws for n in d['nums']]
    return Counter(all_nums)


# ── plot functions ────────────────────────────────────────────────────────────

def plot_frequency_all(draws, freq):
    """Full frequency bar chart with expected line and anomaly highlights."""
    fig, ax = plt.subplots(figsize=(16, 6))
    total = len(draws)
    expected = total * 7 / 50

    numbers = list(range(1, 51))
    counts  = [freq.get(n, 0) for n in numbers]

    colors = []
    for n, c in zip(numbers, counts):
        if n == 50:
            colors.append('#e74c3c')      # red  – major outlier
        elif c >= expected * 1.1:
            colors.append('#2ecc71')      # green – above average
        elif c <= expected * 0.9:
            colors.append('#e67e22')      # orange – below average
        else:
            colors.append('#3498db')      # blue  – normal

    bars = ax.bar(numbers, counts, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(expected, color='red', linestyle='--', linewidth=1.5,
               label=f'Expected ({expected:.0f})')

    # Legend patches
    patches = [
        mpatches.Patch(color='#2ecc71', label='Above average (>10%)'),
        mpatches.Patch(color='#3498db', label='Normal range'),
        mpatches.Patch(color='#e67e22', label='Below average (>10%)'),
        mpatches.Patch(color='#e74c3c', label='#50 — major outlier'),
    ]
    ax.legend(handles=patches + [plt.Line2D([0],[0],color='red',linestyle='--',label=f'Expected ({expected:.0f})')],
              fontsize=9)

    ax.annotate(f'#50\n{freq.get(50,0)}x', xy=(50, freq.get(50,0)),
                xytext=(47, freq.get(50,0)+15),
                arrowprops=dict(arrowstyle='->', color='red'), color='red', fontweight='bold')

    ax.set_xlabel('Lottery Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Times Drawn', fontsize=12, fontweight='bold')
    ax.set_title(f'Frequency of All Numbers 1–50  ({total} main draws, Sep 2009–May 2026)',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(numbers)
    ax.set_xticklabels(numbers, fontsize=7, rotation=45)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'frequency_chart.png', dpi=300, bbox_inches='tight')
    print('✓ frequency_chart.png')
    plt.close()


def plot_top_vs_bottom(draws, freq):
    """Top 10 vs bottom 10 numbers horizontal bar chart."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    top10    = sorted_freq[:10]
    bottom10 = sorted_freq[-10:]

    labels_t, vals_t = zip(*top10)
    labels_b, vals_b = zip(*bottom10)

    ax1.barh([str(n) for n in labels_t], vals_t, color='#2ecc71', edgecolor='black')
    ax1.set_xlabel('Times Drawn', fontsize=11, fontweight='bold')
    ax1.set_title('Top 10 Most Frequent', fontsize=12, fontweight='bold')
    ax1.invert_yaxis()
    for i, v in enumerate(vals_t):
        ax1.text(v + 1, i, str(v), va='center', fontsize=9)

    ax2.barh([str(n) for n in labels_b], vals_b, color='#e74c3c', edgecolor='black')
    ax2.set_xlabel('Times Drawn', fontsize=11, fontweight='bold')
    ax2.set_title('Bottom 10 Least Frequent', fontsize=12, fontweight='bold')
    ax2.invert_yaxis()
    for i, v in enumerate(vals_b):
        ax2.text(v + 1, i, str(v), va='center', fontsize=9)

    plt.suptitle(f'Top vs Bottom Numbers  ({len(draws)} draws)', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'top_vs_bottom.png', dpi=300, bbox_inches='tight')
    print('✓ top_vs_bottom.png')
    plt.close()


def plot_numbers_over_time(draws):
    """Scatter: winning numbers over chronological draw index."""
    fig, ax = plt.subplots(figsize=(16, 6))
    xs, ys = [], []
    for i, d in enumerate(draws):
        for n in d['nums']:
            xs.append(i)
            ys.append(n)
    sc = ax.scatter(xs, ys, s=6, alpha=0.4, c=ys, cmap='viridis')
    plt.colorbar(sc, ax=ax, label='Number Value')
    ax.set_xlabel('Draw Index (oldest → newest)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Winning Number', fontsize=11, fontweight='bold')
    ax.set_title(f'Winning Numbers Over Time  ({len(draws)} draws)', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 51)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'numbers_over_time.png', dpi=300, bbox_inches='tight')
    print('✓ numbers_over_time.png')
    plt.close()


def plot_sum_distribution(draws):
    """Histogram of draw sums with sweet-spot band highlighted."""
    sums = [sum(d['nums']) for d in draws]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axvspan(156, 196, alpha=0.15, color='green', label='Sweet spot (156–196)')
    ax.hist(sums, bins=40, color='steelblue', edgecolor='black', alpha=0.8)
    ax.axvline(np.mean(sums), color='red', linestyle='--', linewidth=2,
               label=f'Mean: {np.mean(sums):.1f}')
    ax.axvline(156, color='green', linestyle=':', linewidth=1.5)
    ax.axvline(196, color='green', linestyle=':', linewidth=1.5)
    ax.set_xlabel('Sum of 7 Numbers', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Draws', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Draw Sums  (sweet spot: 156–196)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'sum_distribution.png', dpi=300, bbox_inches='tight')
    print('✓ sum_distribution.png')
    plt.close()


def plot_odd_even_distribution(draws):
    """Bar chart: how many draws had 0–7 odd numbers."""
    odd_counts = Counter(sum(1 for n in d['nums'] if n % 2 == 1) for d in draws)
    total = len(draws)
    fig, ax = plt.subplots(figsize=(10, 5))
    xs = list(range(8))
    ys = [odd_counts.get(x, 0) for x in xs]
    colors = ['#e74c3c' if x not in (3, 4) else '#2ecc71' for x in xs]
    bars = ax.bar(xs, ys, color=colors, edgecolor='black')
    for bar, y in zip(bars, ys):
        ax.text(bar.get_x() + bar.get_width()/2, y + 3,
                f'{y}\n({y/total*100:.1f}%)', ha='center', va='bottom', fontsize=9)
    ax.set_xlabel('Number of Odd Numbers in Draw', fontsize=12, fontweight='bold')
    ax.set_ylabel('Draw Count', fontsize=12, fontweight='bold')
    ax.set_title('Odd / Even Split Distribution  (green = recommended 3/4 or 4/3)',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(xs)
    ax.set_xticklabels([f'{x} odd\n{7-x} even' for x in xs], fontsize=9)
    patches = [mpatches.Patch(color='#2ecc71', label='Recommended (3/4 or 4/3)'),
               mpatches.Patch(color='#e74c3c', label='Avoid')]
    ax.legend(handles=patches)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'odd_even_distribution.png', dpi=300, bbox_inches='tight')
    print('✓ odd_even_distribution.png')
    plt.close()


def plot_hot_cold_comparison(draws):
    """Side-by-side: all-time frequency vs recent 50 draws frequency."""
    recent = draws[-50:]
    all_freq   = Counter(n for d in draws  for n in d['nums'])
    rec_freq   = Counter(n for d in recent for n in d['nums'])
    total_all  = len(draws)
    total_rec  = len(recent)

    numbers = list(range(1, 51))
    all_pct = [all_freq.get(n, 0) / total_all * 100 for n in numbers]
    rec_pct = [rec_freq.get(n, 0) / total_rec * 100 for n in numbers]

    fig, ax = plt.subplots(figsize=(16, 6))
    x = np.arange(len(numbers))
    w = 0.4
    ax.bar(x - w/2, all_pct, w, label='All-time (1,212 draws)', color='steelblue', alpha=0.8)
    ax.bar(x + w/2, rec_pct, w, label='Recent 50 draws',        color='#e74c3c',   alpha=0.8)
    ax.set_xlabel('Number', fontsize=11, fontweight='bold')
    ax.set_ylabel('Draw Appearance Rate (%)', fontsize=11, fontweight='bold')
    ax.set_title('Hot vs Cold: Recent 50 Draws vs All-Time Frequency',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(numbers, fontsize=7, rotation=45)
    ax.legend()
    ax.axhline(7/50*100, color='gray', linestyle='--', linewidth=1, label='Expected %')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'hot_cold_comparison.png', dpi=300, bbox_inches='tight')
    print('✓ hot_cold_comparison.png')
    plt.close()


def plot_pair_heatmap(draws):
    """Heatmap of how often each pair of numbers appears together."""
    matrix = np.zeros((50, 50), dtype=int)
    for d in draws:
        for a, b in combinations(d['nums'], 2):
            matrix[a-1][b-1] += 1
            matrix[b-1][a-1] += 1

    fig, ax = plt.subplots(figsize=(14, 12))
    mask = np.eye(50, dtype=bool)
    sns.heatmap(matrix, mask=mask, cmap='YlOrRd', ax=ax,
                xticklabels=range(1, 51), yticklabels=range(1, 51),
                cbar_kws={'label': 'Co-occurrence count'}, linewidths=0)
    ax.set_title('Number Pair Co-occurrence Heatmap  (how often each pair appears together)',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Number', fontsize=11)
    ax.set_ylabel('Number', fontsize=11)
    ax.tick_params(labelsize=7)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'pair_heatmap.png', dpi=300, bbox_inches='tight')
    print('✓ pair_heatmap.png')
    plt.close()


def plot_bonus_frequency(draws):
    """Bar chart of bonus number frequencies."""
    bonus_freq = Counter(d['bonus'] for d in draws if d['bonus'])
    numbers = list(range(1, 51))
    counts  = [bonus_freq.get(n, 0) for n in numbers]
    expected = len([d for d in draws if d['bonus']]) / 49

    fig, ax = plt.subplots(figsize=(16, 5))
    colors = ['#e74c3c' if bonus_freq.get(n,0) >= sorted(bonus_freq.values())[-5] else '#9b59b6'
              for n in numbers]
    ax.bar(numbers, counts, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(expected, color='gray', linestyle='--', linewidth=1.5,
               label=f'Expected ({expected:.1f})')
    ax.set_xlabel('Bonus Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Times Drawn as Bonus', fontsize=12, fontweight='bold')
    ax.set_title('Bonus Number Frequency  (red = top 5)', fontsize=13, fontweight='bold')
    ax.set_xticks(numbers)
    ax.set_xticklabels(numbers, fontsize=7, rotation=45)
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'bonus_frequency.png', dpi=300, bbox_inches='tight')
    print('✓ bonus_frequency.png')
    plt.close()


def plot_range_distribution(draws):
    """Stacked bar: low/mid/high number counts per draw, plus pie summary."""
    low_c  = Counter(sum(1 for n in d['nums'] if n <= 17)       for d in draws)
    mid_c  = Counter(sum(1 for n in d['nums'] if 18 <= n <= 33) for d in draws)
    high_c = Counter(sum(1 for n in d['nums'] if n >= 34)       for d in draws)

    total   = len(draws)
    avg_low  = sum(k*v for k,v in low_c.items())  / total
    avg_mid  = sum(k*v for k,v in mid_c.items())  / total
    avg_high = sum(k*v for k,v in high_c.items()) / total

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie of average range split
    ax1.pie([avg_low, avg_mid, avg_high],
            labels=[f'Low (1-17)\n{avg_low:.2f} avg', f'Mid (18-33)\n{avg_mid:.2f} avg',
                    f'High (34-50)\n{avg_high:.2f} avg'],
            colors=['#3498db', '#2ecc71', '#e74c3c'],
            autopct='%1.1f%%', startangle=90, textprops={'fontsize':11})
    ax1.set_title('Average Range Split per Draw', fontsize=12, fontweight='bold')

    # Bar: how often each count of low numbers appears
    xs = list(range(8))
    ax2.bar([str(x) for x in xs], [low_c.get(x, 0)/total*100 for x in xs],
            color='#3498db', label='Low (1-17)', alpha=0.8)
    ax2.bar([str(x) for x in xs], [high_c.get(x, 0)/total*100 for x in xs],
            color='#e74c3c', label='High (34-50)', alpha=0.8, bottom=[low_c.get(x, 0)/total*100 for x in xs])
    ax2.set_xlabel('Count of numbers in range per draw', fontsize=11, fontweight='bold')
    ax2.set_ylabel('% of Draws', fontsize=11, fontweight='bold')
    ax2.set_title('How Many Low vs High Numbers per Draw', fontsize=12, fontweight='bold')
    ax2.legend()

    plt.suptitle('Number Range Distribution Analysis', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'range_distribution.png', dpi=300, bbox_inches='tight')
    print('✓ range_distribution.png')
    plt.close()


def plot_rolling_frequency(draws, top_n=6):
    """Rolling 100-draw frequency for the top N numbers."""
    freq = Counter(n for d in draws for n in d['nums'])
    top_numbers = [n for n, _ in freq.most_common(top_n)]
    window = 100

    fig, ax = plt.subplots(figsize=(16, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, top_n))

    for num, color in zip(top_numbers, colors):
        presence = [1 if num in d['nums'] else 0 for d in draws]
        rolling  = [sum(presence[max(0,i-window):i]) / min(i, window) * 100
                    for i in range(1, len(draws)+1)]
        ax.plot(rolling, label=f'#{num}', color=color, linewidth=1.5, alpha=0.85)

    ax.axhline(7/50*100, color='black', linestyle='--', linewidth=1, label='Expected (14%)')
    ax.set_xlabel('Draw Index', fontsize=11, fontweight='bold')
    ax.set_ylabel('Appearance Rate (%, rolling 100 draws)', fontsize=11, fontweight='bold')
    ax.set_title(f'Rolling Frequency of Top {top_n} Numbers  (100-draw window)',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'rolling_frequency.png', dpi=300, bbox_inches='tight')
    print('✓ rolling_frequency.png')
    plt.close()


def plot_consecutive_trend(draws):
    """Rolling rate of draws containing at least one consecutive pair."""
    window = 100
    has_consec = [1 if any(d['nums'][i+1]-d['nums'][i]==1 for i in range(6)) else 0
                  for d in draws]
    rolling = [sum(has_consec[max(0,i-window):i]) / min(i, window) * 100
               for i in range(1, len(draws)+1)]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(rolling, color='steelblue', linewidth=1.5)
    ax.axhline(np.mean(has_consec)*100, color='red', linestyle='--', linewidth=1.5,
               label=f'Overall avg: {np.mean(has_consec)*100:.1f}%')
    ax.fill_between(range(len(rolling)), rolling, alpha=0.2, color='steelblue')
    ax.set_xlabel('Draw Index', fontsize=11, fontweight='bold')
    ax.set_ylabel('% Draws with Consecutive Pair (rolling 100)', fontsize=11, fontweight='bold')
    ax.set_title('Consecutive Pair Trend Over Time', fontsize=13, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'consecutive_trend.png', dpi=300, bbox_inches='tight')
    print('✓ consecutive_trend.png')
    plt.close()


def plot_overview_dashboard(draws, freq):
    """6-panel overview dashboard (replaces old lotto_analysis_plots.png)."""
    total    = len(draws)
    expected = total * 7 / 50
    sums     = [sum(d['nums']) for d in draws]
    odd_c    = Counter(sum(1 for n in d['nums'] if n % 2 == 1) for d in draws)
    bonus_f  = Counter(d['bonus'] for d in draws if d['bonus'])

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle(f'Lotto Max — Statistical Dashboard  ({total} draws, Sep 2009–May 2026)',
                 fontsize=15, fontweight='bold', y=1.01)

    # 1. Full frequency bar
    ax1 = fig.add_subplot(3, 3, 1)
    nums_list = list(range(1, 51))
    counts = [freq.get(n, 0) for n in nums_list]
    colors = ['#e74c3c' if n==50 else ('#2ecc71' if freq.get(n,0)>=expected*1.1 else '#3498db')
              for n in nums_list]
    ax1.bar(nums_list, counts, color=colors, edgecolor='none')
    ax1.axhline(expected, color='black', linestyle='--', linewidth=1)
    ax1.set_title('Number Frequency (all)', fontsize=10, fontweight='bold')
    ax1.set_xlabel('Number'); ax1.set_ylabel('Count')

    # 2. Sum distribution
    ax2 = fig.add_subplot(3, 3, 2)
    ax2.axvspan(156, 196, alpha=0.2, color='green')
    ax2.hist(sums, bins=35, color='steelblue', edgecolor='black', alpha=0.8)
    ax2.axvline(np.mean(sums), color='red', linestyle='--', linewidth=1.5,
                label=f'Mean: {np.mean(sums):.0f}')
    ax2.set_title('Draw Sum Distribution', fontsize=10, fontweight='bold')
    ax2.set_xlabel('Sum'); ax2.legend(fontsize=8)

    # 3. Odd/Even
    ax3 = fig.add_subplot(3, 3, 3)
    xs = list(range(8))
    ys = [odd_c.get(x, 0) for x in xs]
    bar_colors = ['#2ecc71' if x in (3,4) else '#e74c3c' for x in xs]
    ax3.bar(xs, ys, color=bar_colors, edgecolor='black')
    ax3.set_title('Odd/Even Split', fontsize=10, fontweight='bold')
    ax3.set_xlabel('# Odd Numbers'); ax3.set_ylabel('Draws')
    ax3.set_xticks(xs)

    # 4. Top 10 most frequent
    ax4 = fig.add_subplot(3, 3, 4)
    top10 = freq.most_common(10)
    labels, vals = zip(*top10)
    ax4.barh([str(l) for l in labels], vals, color='#2ecc71', edgecolor='black')
    ax4.set_title('Top 10 Numbers', fontsize=10, fontweight='bold')
    ax4.invert_yaxis()

    # 5. Bonus frequency
    ax5 = fig.add_subplot(3, 3, 5)
    b_nums = list(range(1, 51))
    b_vals = [bonus_f.get(n, 0) for n in b_nums]
    ax5.bar(b_nums, b_vals, color='#9b59b6', edgecolor='none')
    ax5.set_title('Bonus Number Frequency', fontsize=10, fontweight='bold')
    ax5.set_xlabel('Number')

    # 6. Range pie
    ax6 = fig.add_subplot(3, 3, 6)
    avg_l = sum(sum(1 for n in d['nums'] if n<=17)       for d in draws) / total
    avg_m = sum(sum(1 for n in d['nums'] if 18<=n<=33)   for d in draws) / total
    avg_h = sum(sum(1 for n in d['nums'] if n>=34)       for d in draws) / total
    ax6.pie([avg_l, avg_m, avg_h],
            labels=[f'Low\n1-17\n{avg_l:.2f}', f'Mid\n18-33\n{avg_m:.2f}', f'High\n34-50\n{avg_h:.2f}'],
            colors=['#3498db','#2ecc71','#e74c3c'], autopct='%1.1f%%', startangle=90)
    ax6.set_title('Avg Range Split', fontsize=10, fontweight='bold')

    # 7. Bottom 10 least frequent
    ax7 = fig.add_subplot(3, 3, 7)
    bot10 = freq.most_common()[:-11:-1]
    b_labels, b_vals2 = zip(*bot10)
    ax7.barh([str(l) for l in b_labels], b_vals2, color='#e74c3c', edgecolor='black')
    ax7.set_title('Bottom 10 Numbers', fontsize=10, fontweight='bold')
    ax7.invert_yaxis()

    # 8. Hot vs cold scatter (all-time % vs recent-50 %)
    ax8 = fig.add_subplot(3, 3, 8)
    rec_freq = Counter(n for d in draws[-50:] for n in d['nums'])
    all_pct  = [freq.get(n, 0)/total*100 for n in range(1,51)]
    rec_pct  = [rec_freq.get(n,0)/50*100  for n in range(1,51)]
    sc = ax8.scatter(all_pct, rec_pct, c=range(1,51), cmap='RdYlGn', s=60, edgecolors='black', linewidths=0.5)
    for n in range(1, 51):
        ax8.annotate(str(n), (all_pct[n-1], rec_pct[n-1]), fontsize=6, ha='center')
    ax8.set_xlabel('All-time rate (%)', fontsize=9)
    ax8.set_ylabel('Recent-50 rate (%)', fontsize=9)
    ax8.set_title('Hot vs Cold Scatter', fontsize=10, fontweight='bold')

    # 9. Stats table
    ax9 = fig.add_subplot(3, 3, 9)
    ax9.axis('off')
    table_data = [
        ['Metric', 'Value'],
        ['Total Draws', str(total)],
        ['Avg Sum', f'{np.mean(sums):.1f}'],
        ['Sum Range', f'{min(sums)}–{max(sums)}'],
        ['% with consec pair', f'{sum(1 for d in draws if any(d["nums"][i+1]-d["nums"][i]==1 for i in range(6)))/total*100:.1f}%'],
        ['Most frequent #', str(freq.most_common(1)[0][0])],
        ['Least frequent #', '50'],
        ['#50 draws', str(freq.get(50,0))],
        ['Expected per #', f'{expected:.0f}'],
        ['#50 deficit', f'{(expected-freq.get(50,0))/expected*100:.0f}%'],
    ]
    tbl = ax9.table(cellText=table_data, cellLoc='left', loc='center', colWidths=[0.6, 0.4])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.8)
    for j in range(2):
        tbl[(0,j)].set_facecolor('#2c3e50')
        tbl[(0,j)].set_text_props(color='white', weight='bold')
    for i in range(1, len(table_data)):
        for j in range(2):
            tbl[(i,j)].set_facecolor('#ecf0f1' if i%2==0 else 'white')
    ax9.set_title('Key Statistics', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'lotto_analysis_plots.png', dpi=300, bbox_inches='tight')
    print('✓ lotto_analysis_plots.png  (dashboard)')
    plt.close()


# ── main ──────────────────────────────────────────────────────────────────────

def create_visualizations():
    print('Loading data...')
    draws = load_main_draws()
    freq  = freq_weights(draws)
    print(f'  {len(draws)} main draws loaded\n')

    print('Generating plots:')
    plot_overview_dashboard(draws, freq)
    plot_frequency_all(draws, freq)
    plot_top_vs_bottom(draws, freq)
    plot_numbers_over_time(draws)
    plot_sum_distribution(draws)
    plot_odd_even_distribution(draws)
    plot_hot_cold_comparison(draws)
    plot_pair_heatmap(draws)
    plot_bonus_frequency(draws)
    plot_range_distribution(draws)
    plot_rolling_frequency(draws)
    plot_consecutive_trend(draws)

    print('\n✓ All plots saved:')
    plots = [
        ('lotto_analysis_plots.png',   'Overview dashboard (9 panels)'),
        ('frequency_chart.png',        'Full frequency with anomaly highlights'),
        ('top_vs_bottom.png',          'Top 10 vs Bottom 10'),
        ('numbers_over_time.png',      'Numbers over time scatter'),
        ('sum_distribution.png',       'Draw sum histogram + sweet spot'),
        ('odd_even_distribution.png',  'Odd/Even split bar chart'),
        ('hot_cold_comparison.png',    'Hot vs Cold (recent vs all-time)'),
        ('pair_heatmap.png',           'Pair co-occurrence heatmap'),
        ('bonus_frequency.png',        'Bonus number frequency'),
        ('range_distribution.png',     'Low/Mid/High range analysis'),
        ('rolling_frequency.png',      'Rolling frequency of top 6 numbers'),
        ('consecutive_trend.png',      'Consecutive pair trend over time'),
    ]
    for fname, desc in plots:
        print(f'  {fname:<35} — {desc}')


if __name__ == '__main__':
    create_visualizations()
