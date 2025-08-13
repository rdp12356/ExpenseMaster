import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CHART_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'charts')
os.makedirs(CHART_DIR, exist_ok=True)

def plot_spend_by_category(expenses, outname='spend_by_category.png'):
    agg = {}
    for e in expenses:
        cat = e.get('category') or 'Other'
        amt = float(e.get('amount') or 0)
        agg[cat] = agg.get(cat, 0) + amt
    labels = list(agg.keys())
    sizes = [agg[k] for k in labels]
    if not sizes:
        sizes = [1]
        labels = ['No Data']
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    outpath = os.path.join(CHART_DIR, outname)
    fig.savefig(outpath, bbox_inches='tight', dpi=120)
    plt.close(fig)
    return outpath

def plot_time_series(months, amounts, outname='time_series.png'):
    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(months, amounts, marker='o')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount')
    ax.set_title('Spending Over Time')
    ax.grid(True, linestyle='--', alpha=0.4)
    outpath = os.path.join(CHART_DIR, outname)
    fig.savefig(outpath, bbox_inches='tight', dpi=120)
    plt.close(fig)
    return outpath
