"""
Micron Product Mix Optimization - Visualization
ISE 530: Optimization Methods for Analytics
Spring 2026

Creates visualizations for the optimization results.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Load results
results_path = os.path.join(os.path.dirname(__file__), 'results')
output_path = os.path.join(os.path.dirname(__file__), 'visualizations')
os.makedirs(output_path, exist_ok=True)

optimal_df = pd.read_csv(os.path.join(results_path, 'optimal_allocation.csv'))
scenario_df = pd.read_csv(os.path.join(results_path, 'scenario_comparison.csv'))
allocation_df = pd.read_csv(os.path.join(results_path, 'allocation_by_scenario.csv'), index_col=0)
hbm_sens_df = pd.read_csv(os.path.join(results_path, 'hbm_sensitivity.csv'))

# =============================================================================
# CHART 1: Current vs Optimal Allocation (Bar Chart)
# =============================================================================

fig, ax = plt.subplots(figsize=(14, 7))

products = optimal_df['Product']
x = np.arange(len(products))
width = 0.35

bars1 = ax.bar(x - width/2, optimal_df['Current_Allocation_%'], width, 
               label='Current Allocation', color='#3498db', alpha=0.8)
bars2 = ax.bar(x + width/2, optimal_df['Optimal_Allocation_%'], width, 
               label='Optimal Allocation', color='#2ecc71', alpha=0.8)

ax.set_xlabel('Product')
ax.set_ylabel('Capacity Allocation (%)')
ax.set_title('Micron Capacity Allocation: Current vs Optimal\n(Based on Profit Maximization)', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(products, rotation=45, ha='right')
ax.legend()

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(output_path, '01_current_vs_optimal.png'), dpi=150, bbox_inches='tight')
plt.close()

print("Created: 01_current_vs_optimal.png")

# =============================================================================
# CHART 2: Profit Contribution by Product (Pie Chart)
# =============================================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Current allocation profit
current_profit = optimal_df['Current_Allocation_%'] * optimal_df['Gross_Margin_%'] / 100
current_profit = current_profit * (optimal_df['Revenue_Contribution_$B'] / optimal_df['Optimal_Allocation_%'].replace(0, 1))

# Optimal profit
optimal_profit = optimal_df['Profit_Contribution_$B']

colors = ['#e74c3c', '#3498db', '#9b59b6', '#f39c12', '#1abc9c', '#34495e', '#e67e22', '#95a5a6']

# Filter out zero values for pie chart
mask_optimal = optimal_profit > 0.01
labels_opt = optimal_df.loc[mask_optimal, 'Product']
values_opt = optimal_profit[mask_optimal]
colors_opt = [colors[i] for i in range(len(optimal_df)) if mask_optimal.iloc[i]]

axes[1].pie(values_opt, labels=labels_opt, autopct='%1.1f%%', colors=colors_opt, startangle=90)
axes[1].set_title('Optimal Allocation\nProfit Distribution', fontsize=14, fontweight='bold')

# For current, calculate from original data
current_rev_per_cap = optimal_df['Revenue_Contribution_$B'] / optimal_df['Optimal_Allocation_%'].replace(0, 1)
current_profit_calc = optimal_df['Current_Allocation_%'] * current_rev_per_cap * optimal_df['Gross_Margin_%'] / 100
mask_current = current_profit_calc > 0.01
labels_curr = optimal_df.loc[mask_current, 'Product']
values_curr = current_profit_calc[mask_current]
colors_curr = [colors[i] for i in range(len(optimal_df)) if mask_current.iloc[i]]

axes[0].pie(values_curr, labels=labels_curr, autopct='%1.1f%%', colors=colors_curr, startangle=90)
axes[0].set_title('Current Allocation\nProfit Distribution', fontsize=14, fontweight='bold')

plt.suptitle('Profit Contribution by Product Category', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(output_path, '02_profit_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()

print("Created: 02_profit_distribution.png")

# =============================================================================
# CHART 3: Scenario Comparison (Horizontal Bar Chart)
# =============================================================================

fig, ax = plt.subplots(figsize=(12, 6))

scenarios = scenario_df['Scenario']
profits = scenario_df['Total_Profit_$B']

colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12']
bars = ax.barh(scenarios, profits, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

ax.set_xlabel('Total Profit ($ Billion)')
ax.set_title('Profit Comparison Across Scenarios\n', fontsize=16, fontweight='bold')
ax.axvline(x=profits.iloc[1], color='black', linestyle='--', alpha=0.5, label='Baseline')

# Add value labels
for bar, profit in zip(bars, profits):
    ax.text(profit + 0.2, bar.get_y() + bar.get_height()/2, f'${profit:.2f}B', 
            va='center', fontsize=11, fontweight='bold')

ax.set_xlim(0, max(profits) * 1.15)
plt.tight_layout()
plt.savefig(os.path.join(output_path, '03_scenario_comparison.png'), dpi=150, bbox_inches='tight')
plt.close()

print("Created: 03_scenario_comparison.png")

# =============================================================================
# CHART 4: HBM Sensitivity Analysis
# =============================================================================

fig, ax1 = plt.subplots(figsize=(10, 6))

x = hbm_sens_df['HBM_Max_Capacity_%']
y1 = hbm_sens_df['Total_Profit_$B']

ax1.plot(x, y1, 'b-o', linewidth=2, markersize=10, label='Total Profit')
ax1.fill_between(x, y1, alpha=0.3, color='blue')
ax1.set_xlabel('HBM Maximum Capacity Constraint (%)')
ax1.set_ylabel('Total Profit ($ Billion)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Add annotations for key points
ax1.annotate('Current Limit\n(25%)', xy=(25, y1.iloc[2]), xytext=(27, y1.iloc[2]-0.8),
             arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')
ax1.annotate('Demand Saturation\n(~34%)', xy=(35, y1.iloc[4]), xytext=(37, y1.iloc[4]-0.5),
             arrowprops=dict(arrowstyle='->', color='green'), fontsize=10, color='green')

ax1.set_title('Value of Expanding HBM Manufacturing Capacity\n(Aggressive Demand Scenario)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_path, '04_hbm_sensitivity.png'), dpi=150, bbox_inches='tight')
plt.close()

print("Created: 04_hbm_sensitivity.png")

# =============================================================================
# CHART 5: Allocation Heatmap by Scenario
# =============================================================================

fig, ax = plt.subplots(figsize=(12, 8))

# Prepare data
heatmap_data = allocation_df.T

im = ax.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')

# Set ticks
ax.set_xticks(np.arange(len(heatmap_data.columns)))
ax.set_yticks(np.arange(len(heatmap_data.index)))
ax.set_xticklabels(heatmap_data.columns, rotation=45, ha='right')
ax.set_yticklabels(heatmap_data.index)

# Add colorbar
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel('Allocation %', rotation=-90, va="bottom")

# Add text annotations
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        value = heatmap_data.iloc[i, j]
        color = 'white' if value > 15 else 'black'
        text = ax.text(j, i, f'{value:.1f}%', ha='center', va='center', color=color, fontsize=9)

ax.set_title('Product Allocation by Scenario (%)\n', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(output_path, '05_allocation_heatmap.png'), dpi=150, bbox_inches='tight')
plt.close()

print("Created: 05_allocation_heatmap.png")

# =============================================================================
# CHART 6: Margin vs Revenue Bubble Chart
# =============================================================================

fig, ax = plt.subplots(figsize=(12, 8))

# Load original product data for this chart
data_path = os.path.join(os.path.dirname(__file__), 'data')
products_df = pd.read_csv(os.path.join(data_path, 'product_data.csv'))

x = products_df['revenue_fy2025_billion']
y = products_df['gross_margin_pct']
sizes = optimal_df['Optimal_Allocation_%'] * 30  # Scale for visibility

colors = ['#e74c3c', '#3498db', '#9b59b6', '#f39c12', '#1abc9c', '#34495e', '#e67e22', '#95a5a6']

scatter = ax.scatter(x, y, s=sizes, c=colors, alpha=0.7, edgecolors='black', linewidth=2)

# Add labels
for i, row in products_df.iterrows():
    ax.annotate(row['product_name'], (x[i], y[i]), 
                xytext=(5, 5), textcoords='offset points', fontsize=9)

ax.set_xlabel('FY2025 Revenue ($ Billion)')
ax.set_ylabel('Gross Margin (%)')
ax.set_title('Product Portfolio: Revenue vs Margin\n(Bubble Size = Optimal Allocation %)', fontsize=14, fontweight='bold')

# Add quadrant lines
ax.axhline(y=35, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=4, color='gray', linestyle='--', alpha=0.5)

# Add quadrant labels
ax.text(7, 50, 'STARS\n(High Revenue, High Margin)', ha='center', fontsize=10, style='italic', alpha=0.7)
ax.text(1.5, 50, 'NICHE\n(Low Revenue, High Margin)', ha='center', fontsize=10, style='italic', alpha=0.7)
ax.text(7, 22, 'VOLUME\n(High Revenue, Low Margin)', ha='center', fontsize=10, style='italic', alpha=0.7)
ax.text(1.5, 22, 'QUESTION MARKS\n(Low Revenue, Low Margin)', ha='center', fontsize=10, style='italic', alpha=0.7)

ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_path, '06_margin_revenue_bubble.png'), dpi=150, bbox_inches='tight')
plt.close()

print("Created: 06_margin_revenue_bubble.png")

# =============================================================================
# CHART 7: Summary Dashboard
# =============================================================================

fig = plt.figure(figsize=(16, 12))

# Create grid
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Title
fig.suptitle('MICRON PRODUCT MIX OPTIMIZATION - EXECUTIVE SUMMARY', 
             fontsize=20, fontweight='bold', y=0.98)

# KPI Box 1: Profit Improvement
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.text(5, 7, '+20.4%', fontsize=36, ha='center', va='center', fontweight='bold', color='#2ecc71')
ax1.text(5, 3, 'Profit\nImprovement', fontsize=14, ha='center', va='center')
ax1.axis('off')
ax1.set_facecolor('#f8f9fa')
for spine in ax1.spines.values():
    spine.set_visible(True)
    spine.set_color('#dee2e6')

# KPI Box 2: HBM Allocation
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.text(5, 7, '25%', fontsize=36, ha='center', va='center', fontweight='bold', color='#e74c3c')
ax2.text(5, 3, 'Optimal HBM\nAllocation', fontsize=14, ha='center', va='center')
ax2.axis('off')

# KPI Box 3: Total Profit
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.text(5, 7, '$16.8B', fontsize=36, ha='center', va='center', fontweight='bold', color='#3498db')
ax3.text(5, 3, 'Optimal\nTotal Profit', fontsize=14, ha='center', va='center')
ax3.axis('off')

# Allocation comparison (bottom left)
ax4 = fig.add_subplot(gs[1, :2])
products = optimal_df['Product']
x = np.arange(len(products))
width = 0.35
ax4.bar(x - width/2, optimal_df['Current_Allocation_%'], width, label='Current', color='#3498db', alpha=0.8)
ax4.bar(x + width/2, optimal_df['Optimal_Allocation_%'], width, label='Optimal', color='#2ecc71', alpha=0.8)
ax4.set_ylabel('Allocation (%)')
ax4.set_title('Capacity Allocation: Current vs Optimal', fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(products, rotation=45, ha='right', fontsize=9)
ax4.legend(loc='upper right')

# Scenario comparison (bottom right)
ax5 = fig.add_subplot(gs[1, 2])
scenarios_short = ['Conservative', 'Baseline', 'Aggressive', 'HBM+', 'AI Winter']
profits = scenario_df['Total_Profit_$B'].values
colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12']
ax5.barh(scenarios_short, profits, color=colors, alpha=0.8)
ax5.set_xlabel('Profit ($B)')
ax5.set_title('Scenario Analysis', fontweight='bold')
ax5.axvline(x=profits[1], color='black', linestyle='--', alpha=0.5)

# Key recommendations (bottom)
ax6 = fig.add_subplot(gs[2, :])
ax6.axis('off')
recommendations = """
KEY STRATEGIC RECOMMENDATIONS:

1. MAXIMIZE HBM: Increase allocation from 15% to 25% (manufacturing limit) — adds $2.85B in profit
2. INVEST IN HBM CAPACITY: Each 1% capacity increase = ~$0.18B additional profit  
3. REDUCE COMMODITY NAND: Exit Client/Mobile NAND segments (18-22% margins vs 55% HBM)
4. MAINTAIN DATA CENTER FOCUS: 60%+ of optimal allocation is data center products
5. HEDGE RISK: Keep minimum PC/Mobile presence to preserve customer relationships
"""
ax6.text(0.05, 0.95, recommendations, transform=ax6.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#dee2e6'))

plt.savefig(os.path.join(output_path, '07_executive_summary.png'), dpi=150, bbox_inches='tight')
plt.close()

print("Created: 07_executive_summary.png")

# =============================================================================
# COMPLETION
# =============================================================================

print("\n" + "="*60)
print("VISUALIZATION COMPLETE")
print("="*60)
print(f"\nAll charts saved to: {output_path}/")
print("\nFiles created:")
print("  1. 01_current_vs_optimal.png")
print("  2. 02_profit_distribution.png")
print("  3. 03_scenario_comparison.png")
print("  4. 04_hbm_sensitivity.png")
print("  5. 05_allocation_heatmap.png")
print("  6. 06_margin_revenue_bubble.png")
print("  7. 07_executive_summary.png")
