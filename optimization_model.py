"""
Micron Product Mix Optimization Model
ISE 530: Optimization Methods for Analytics
Spring 2026

This model determines the optimal allocation of Micron's fab capacity
across product types to maximize profit, subject to manufacturing and
market constraints.

Author: Preet Patel
"""

import cvxpy as cp
import numpy as np
import pandas as pd
import os

# =============================================================================
# 1. LOAD DATA
# =============================================================================

data_path = os.path.join(os.path.dirname(__file__), 'data')

# Load all data files
products_df = pd.read_csv(os.path.join(data_path, 'product_data.csv'))
constraints_df = pd.read_csv(os.path.join(data_path, 'capacity_constraints.csv'))
demand_df = pd.read_csv(os.path.join(data_path, 'demand_forecast.csv'))
costs_df = pd.read_csv(os.path.join(data_path, 'cost_structure.csv'))

# Merge product and cost data
df = products_df.merge(costs_df[['product_id', 'variable_cost_per_gb_usd', 'yield_rate_pct', 'wafer_utilization_factor']], 
                       on='product_id')
df = df.merge(demand_df[['product_id', 'demand_fy2026_baseline_billion', 'market_tam_2026_billion']], 
              on='product_id')

print("="*60)
print("MICRON PRODUCT MIX OPTIMIZATION MODEL")
print("="*60)
print(f"\nLoaded {len(df)} products for optimization\n")

# =============================================================================
# 2. DEFINE PARAMETERS
# =============================================================================

n_products = len(df)

# Revenue per unit capacity ($ billion per % capacity)
# This represents how much revenue each 1% of capacity generates
revenue_per_capacity = df['revenue_fy2025_billion'].values / df['capacity_share_pct_current'].values

# Gross margin by product
gross_margin = df['gross_margin_pct'].values / 100

# Profit per unit capacity (revenue × margin)
profit_per_capacity = revenue_per_capacity * gross_margin

# Current allocation (for comparison)
current_allocation = df['capacity_share_pct_current'].values

# Demand ceiling (can't sell more than market demands)
# Convert demand to capacity equivalent
demand_ceiling = (df['demand_fy2026_baseline_billion'].values / revenue_per_capacity) 
demand_ceiling = np.minimum(demand_ceiling, 100)  # Cap at 100%

print("Parameters Loaded:")
print("-"*60)
print(f"{'Product':<20} {'Rev/Cap':<12} {'Margin':<10} {'Profit/Cap':<12}")
print("-"*60)
for i, row in df.iterrows():
    print(f"{row['product_name']:<20} ${revenue_per_capacity[i]:.3f}B      {gross_margin[i]*100:.1f}%      ${profit_per_capacity[i]:.3f}B")

# =============================================================================
# 3. DEFINE DECISION VARIABLES
# =============================================================================

# x[i] = percentage of total capacity allocated to product i
x = cp.Variable(n_products, nonneg=True)

print("\n" + "="*60)
print("OPTIMIZATION FORMULATION")
print("="*60)

# =============================================================================
# 4. DEFINE OBJECTIVE FUNCTION
# =============================================================================

# Objective: Maximize total gross profit
# Profit = Σ (revenue_per_capacity[i] × margin[i] × x[i])
objective = cp.Maximize(profit_per_capacity @ x)

print("\nObjective Function:")
print("  Maximize: Σ (profit_per_capacity[i] × x[i])")
print("  Where profit_per_capacity = revenue_per_capacity × gross_margin")

# =============================================================================
# 5. DEFINE CONSTRAINTS
# =============================================================================

constraints = []

# Constraint 1: Total capacity must equal 100%
constraints.append(cp.sum(x) == 100)

# Constraint 2: HBM maximum capacity (manufacturing complexity limit)
# HBM is product index 0
hbm_idx = 0
constraints.append(x[hbm_idx] <= 25)

# Constraint 3: Minimum DRAM allocation (60%)
# DRAM products are indices 0-4
dram_indices = [0, 1, 2, 3, 4]
constraints.append(cp.sum(x[dram_indices]) >= 60)

# Constraint 4: Minimum NAND allocation (15%)
# NAND products are indices 5-7
nand_indices = [5, 6, 7]
constraints.append(cp.sum(x[nand_indices]) >= 15)

# Constraint 5: Minimum PC DRAM allocation (8%)
# DDR5_PC is index 2
pc_idx = 2
constraints.append(x[pc_idx] >= 8)

# Constraint 6: Minimum Mobile allocation (5%)
# LPDDR5_Mobile is index 3, NAND_Mobile is index 7
mobile_indices = [3, 7]
constraints.append(cp.sum(x[mobile_indices]) >= 5)

# Constraint 7: Minimum Data Center allocation (35%)
# HBM (0), DDR5_Server (1), LPDDR5_Server (4), NAND_DataCenter_SSD (5)
datacenter_indices = [0, 1, 4, 5]
constraints.append(cp.sum(x[datacenter_indices]) >= 35)

# Constraint 8: Demand ceiling - can't allocate more than market demands
for i in range(n_products):
    constraints.append(x[i] <= demand_ceiling[i])

# Constraint 9: Non-negativity (already handled by nonneg=True)

print("\nConstraints:")
print("  1. Σ x[i] = 100%  (total capacity)")
print("  2. x[HBM] ≤ 25%   (manufacturing limit)")
print("  3. Σ x[DRAM] ≥ 60%  (market position)")
print("  4. Σ x[NAND] ≥ 15%  (customer commitments)")
print("  5. x[PC] ≥ 8%     (OEM relationships)")
print("  6. Σ x[Mobile] ≥ 5%  (smartphone OEMs)")
print("  7. Σ x[DataCenter] ≥ 35%  (strategic priority)")
print("  8. x[i] ≤ demand_ceiling[i]  (market demand limits)")
print("  9. x[i] ≥ 0  (non-negativity)")

# =============================================================================
# 6. SOLVE THE PROBLEM
# =============================================================================

problem = cp.Problem(objective, constraints)

print("\n" + "="*60)
print("SOLVING OPTIMIZATION PROBLEM")
print("="*60)

# Solve using default solver (ECOS, OSQP, or SCS)
problem.solve(verbose=False)

print(f"\nSolver Status: {problem.status}")
print(f"Optimal Value (Total Profit): ${problem.value:.3f} Billion")

# =============================================================================
# 7. DISPLAY RESULTS
# =============================================================================

print("\n" + "="*60)
print("OPTIMAL ALLOCATION RESULTS")
print("="*60)

# Create results dataframe
results = pd.DataFrame({
    'Product': df['product_name'],
    'Category': df['product_category'],
    'Current_Allocation_%': current_allocation,
    'Optimal_Allocation_%': np.round(x.value, 2),
    'Change_%': np.round(x.value - current_allocation, 2),
    'Gross_Margin_%': gross_margin * 100,
    'Revenue_Contribution_$B': np.round(revenue_per_capacity * x.value, 3),
    'Profit_Contribution_$B': np.round(profit_per_capacity * x.value, 3)
})

print("\nDetailed Results:")
print("-"*100)
print(f"{'Product':<18} {'Category':<8} {'Current%':<10} {'Optimal%':<10} {'Change%':<10} {'Margin%':<10} {'Revenue$B':<12} {'Profit$B':<10}")
print("-"*100)

for _, row in results.iterrows():
    change_str = f"+{row['Change_%']:.1f}" if row['Change_%'] > 0 else f"{row['Change_%']:.1f}"
    print(f"{row['Product']:<18} {row['Category']:<8} {row['Current_Allocation_%']:<10.1f} {row['Optimal_Allocation_%']:<10.1f} {change_str:<10} {row['Gross_Margin_%']:<10.1f} {row['Revenue_Contribution_$B']:<12.3f} {row['Profit_Contribution_$B']:<10.3f}")

print("-"*100)

# Summary statistics
total_revenue = np.sum(revenue_per_capacity * x.value)
total_profit = problem.value
current_profit = np.sum(profit_per_capacity * current_allocation)

print(f"\n{'SUMMARY':<30}")
print(f"{'='*40}")
print(f"{'Total Optimal Revenue:':<30} ${total_revenue:.3f} Billion")
print(f"{'Total Optimal Profit:':<30} ${total_profit:.3f} Billion")
print(f"{'Current Allocation Profit:':<30} ${current_profit:.3f} Billion")
print(f"{'Profit Improvement:':<30} ${total_profit - current_profit:.3f} Billion ({((total_profit/current_profit)-1)*100:.1f}%)")

# =============================================================================
# 8. CONSTRAINT ANALYSIS (Shadow Prices / Dual Values)
# =============================================================================

print("\n" + "="*60)
print("CONSTRAINT ANALYSIS (Sensitivity)")
print("="*60)

constraint_names = [
    "Total Capacity = 100%",
    "HBM ≤ 25%",
    "DRAM ≥ 60%",
    "NAND ≥ 15%",
    "PC ≥ 8%",
    "Mobile ≥ 5%",
    "DataCenter ≥ 35%"
]

print("\nShadow Prices (value of relaxing each constraint by 1 unit):")
print("-"*60)
for i, name in enumerate(constraint_names):
    if constraints[i].dual_value is not None:
        dual = constraints[i].dual_value
        binding = "BINDING" if abs(dual) > 0.001 else "Not binding"
        print(f"{name:<25} Dual: ${dual:>8.4f}B  [{binding}]")

# =============================================================================
# 9. SAVE RESULTS
# =============================================================================

results_path = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(results_path, exist_ok=True)

results.to_csv(os.path.join(results_path, 'optimal_allocation.csv'), index=False)
print(f"\nResults saved to: {results_path}/optimal_allocation.csv")

# =============================================================================
# 10. KEY INSIGHTS
# =============================================================================

print("\n" + "="*60)
print("KEY INSIGHTS")
print("="*60)

# Find biggest increases and decreases
max_increase_idx = results['Change_%'].idxmax()
max_decrease_idx = results['Change_%'].idxmin()

print(f"""
1. INCREASE HBM ALLOCATION
   - Optimal: {results.loc[0, 'Optimal_Allocation_%']:.1f}% (from {results.loc[0, 'Current_Allocation_%']:.1f}%)
   - HBM has the highest margin ({results.loc[0, 'Gross_Margin_%']:.0f}%) and is constrained by manufacturing capacity
   - Recommendation: Invest in expanding HBM manufacturing capability

2. BIGGEST SHIFT
   - Increase: {results.loc[max_increase_idx, 'Product']} (+{results.loc[max_increase_idx, 'Change_%']:.1f}%)
   - Decrease: {results.loc[max_decrease_idx, 'Product']} ({results.loc[max_decrease_idx, 'Change_%']:.1f}%)

3. STRATEGIC IMPLICATIONS
   - Data center focus is validated (high-margin products)
   - Maintain minimum presence in PC/Mobile for customer relationships
   - NAND margins are lower; allocate minimum required

4. PROFIT IMPACT
   - Optimal allocation improves profit by ${total_profit - current_profit:.3f}B
   - This represents a {((total_profit/current_profit)-1)*100:.1f}% improvement
""")

print("="*60)
print("MODEL EXECUTION COMPLETE")
print("="*60)
