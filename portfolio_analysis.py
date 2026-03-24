# Financial Portfolio Analysis
# Modern Portfolio Theory (MPT)
# Author: Supriya Busa

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

# ================================
# STEP 1 - LOAD DATA
# ================================
df = pd.read_csv('portfolio_data.csv')
print("Data loaded successfully!")
print(f"Total rows: {len(df)}")
print(df.head())

# ================================
# STEP 2 - CLEAN DATA
# ================================
df['Date'] = pd.to_datetime(df['Date'])
df = df.dropna()
print("\nData cleaned successfully!")
print(df.dtypes)

# ================================
# STEP 3 - PORTFOLIO RETURNS
# ================================
# Average return per strategy
strategy_returns = df.groupby('Strategy')['Portfolio_Return(%)'].mean().round(2)
print("\nAverage Portfolio Returns by Strategy:")
print(strategy_returns)

# ================================
# STEP 4 - RISK ANALYSIS
# ================================
# Average volatility per strategy
strategy_volatility = df.groupby('Strategy')['Portfolio_Volatility(%)'].mean().round(2)
single_asset_volatility = df.groupby('Strategy')['SingleAsset_Volatility(%)'].mean().round(2)

print("\nPortfolio Volatility vs Single Asset:")
comparison = pd.DataFrame({
    'Portfolio_Volatility': strategy_volatility,
    'SingleAsset_Volatility': single_asset_volatility
})
comparison['Reduction(%)'] = (
    (comparison['SingleAsset_Volatility'] - comparison['Portfolio_Volatility'])
    / comparison['SingleAsset_Volatility'] * 100
).round(2)
print(comparison)

# ================================
# STEP 5 - SHARPE RATIO
# ================================
sharpe_ratio = df.groupby('Strategy')['Sharpe_Ratio'].mean().round(2)
print("\nAverage Sharpe Ratio by Strategy:")
print(sharpe_ratio)


# ================================
# STEP 5 - ADVANCED RISK METRICS
# ================================

def get_advanced_metrics(series):
    # 1. Max Drawdown (The 'Pain' Factor)
    nav = (1 + series / 100).cumprod()
    running_max = nav.cummax()
    drawdown = (nav - running_max) / running_max
    mdd = drawdown.min() * 100

    # 2. Calmar Ratio (Return / Max Drawdown)
    # A Calmar > 0.5 is usually considered good.
    avg_annual_return = series.mean() * 252  # Annualized (approx 252 trading days)
    calmar = abs(avg_annual_return / mdd) if mdd != 0 else 0

    return pd.Series({
        'Max_Drawdown(%)': round(mdd, 2),
        'Calmar_Ratio': round(calmar, 2)
    })


# Apply to each strategy
advanced_stats = df.groupby('Strategy')['Portfolio_Return(%)'].apply(get_advanced_metrics).unstack()

print("\nAdvanced Risk Metrics (MDD & Calmar):")
print(advanced_stats)

# ================================
# STEP 6 - CONSOLIDATE RESULTS (Fixed Names)
# ================================
results = pd.concat([
    strategy_returns.rename('Avg_Return(%)'),
    strategy_volatility.rename('Portfolio_Volatility(%)'), # Kept original name for charts
    single_asset_volatility.rename('SingleAsset_Volatility(%)'),
    sharpe_ratio.rename('Sharpe_Ratio'),
    advanced_stats
], axis=1).reset_index()

results.to_csv('portfolio_results_comprehensive.csv', index=False)
print("\nFinal Comprehensive Results Saved!")

# ================================
# STEP 7 - CHARTS
# ================================
sns.set_style("whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Financial Portfolio Analysis 2022-2023',
             fontsize=16, fontweight='bold', color='#1F4E79')

# Chart 1 - Returns by Strategy
axes[0,0].bar(results['Strategy'],
              results['Avg_Return(%)'],
              color=['#1F4E79','#2E75B6','#4472C4','#70AD47','#FFC000'])
axes[0,0].set_title('Average Return by Strategy', fontweight='bold')
axes[0,0].set_xlabel('Strategy')
axes[0,0].set_ylabel('Return (%)')
axes[0,0].tick_params(axis='x', rotation=15)

# Chart 2 - Volatility Comparison
x = np.arange(len(results['Strategy']))
width = 0.35
axes[0,1].bar(x - width/2, results['Portfolio_Volatility(%)'],
              width, label='Diversified Portfolio', color='#1F4E79')
axes[0,1].bar(x + width/2, results['SingleAsset_Volatility(%)'],
              width, label='Single Asset', color='#FF6B6B')

# Chart 3 - Sharpe Ratio
axes[1,0].bar(results['Strategy'],
              results['Sharpe_Ratio'],
              color='#70AD47')
axes[1,0].set_title('Sharpe Ratio by Strategy', fontweight='bold')
axes[1,0].set_xlabel('Strategy')
axes[1,0].set_ylabel('Sharpe Ratio')
axes[1,0].tick_params(axis='x', rotation=15)

# Chart 4 - Risk vs Return
axes[1,1].scatter(results['Portfolio_Volatility(%)'],
                  results['Avg_Return(%)'],
                  s=200, color='#1F4E79', zorder=5)
for i, row in results.iterrows():
    axes[1,1].annotate(row['Strategy'],
                       (row['Portfolio_Volatility(%)'],
                        row['Avg_Return(%)']),
                       textcoords="offset points",
                       xytext=(5,5), fontsize=9)
axes[1,1].set_title('Risk vs Return', fontweight='bold')
axes[1,1].set_xlabel('Volatility (Risk %)')
axes[1,1].set_ylabel('Return (%)')

plt.tight_layout()
plt.savefig('portfolio_charts.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nCharts saved as portfolio_charts.png!")
print("\nAnalysis Complete!")

# ================================
# PHASE 3 - MONTE CARLO SIMULATION
# ================================
print("\nStarting Monte Carlo Simulation (1,000 paths)...")

# 1. Get parameters from your 'Balanced' strategy
balanced_stats = results[results['Strategy'] == 'Balanced'].iloc[0]
mu = balanced_stats['Avg_Return(%)'] / 100  # Mean return
sigma = balanced_stats['Portfolio_Volatility(%)'] / 100  # Volatility

# 2. Simulation Settings
start_price = 10000  # Starting with $10,000
days = 252 * 5       # 5 years of trading days
simulations = 1000

# 3. Run Simulation
# We generate random daily returns based on a normal distribution
daily_returns = np.random.normal(mu/252, sigma/np.sqrt(252), (days, simulations))
price_paths = start_price * (1 + daily_returns).cumprod(axis=0)

# 4. Visualization of Simulation
plt.figure(figsize=(10, 6))
plt.plot(price_paths[:, :50], color='#2E75B6', alpha=0.1) # Plot first 50 paths
plt.plot(price_paths.mean(axis=1), color='red', linewidth=2, label='Average Path')
plt.title('5-Year Monte Carlo Projection (Balanced Strategy)', fontweight='bold')
plt.xlabel('Trading Days')
plt.ylabel('Portfolio Value ($)')
plt.legend()
plt.savefig('monte_carlo_projection.png', dpi=150)
print("Monte Carlo chart saved as monte_carlo_projection.png!")

# 5. Probability of Success
final_values = price_paths[-1, :]
prob_gain = (final_values > start_price).sum() / simulations * 100
print(f"Probability of making a profit after 5 years: {prob_gain}%")
print(f"Expected median value: ${np.median(final_values):,.2f}")

# ================================
# PHASE 4 - EXECUTIVE SUMMARY
# ================================
print("\nGenerating Executive Summary...")

# Find the best strategy based on Sharpe Ratio
best_sharpe = results.loc[results['Sharpe_Ratio'].idxmax()]
# Find the safest strategy based on Volatility
safest_strat = results.loc[results['Portfolio_Volatility(%)'].idxmin()]

summary_text = f"""
=========================================
FINANCIAL PORTFOLIO ANALYSIS REPORT
=========================================
Project Author: Supriya Busa
Analysis Period: 2022-2023

KEY PERFORMANCE INSIGHTS:
-------------------------
* Best Risk-Adjusted Strategy: {best_sharpe['Strategy']} 
  (Sharpe Ratio: {best_sharpe['Sharpe_Ratio']})

* Safest Investment Path: {safest_strat['Strategy']} 
  (Volatility: {safest_strat['Portfolio_Volatility(%)']}%)

* Diversification Benefit: Your portfolio reduced 
  single-asset risk by an average of {comparison['Reduction(%)'].mean():.2f}%.

FUTURE PROJECTION (5-Year Forecast):
------------------------------------
Based on a $10,000 starting investment in the Balanced Strategy:
* Probability of Profit: {prob_gain}%
* Expected Median Outcome: ${np.median(final_values):,.2f}

CONCLUSION:
The {best_sharpe['Strategy']} strategy provides the most efficient 
returns relative to risk. However, the {safest_strat['Strategy']} 
approach is recommended for risk-averse investors.
=========================================
"""

# Save the summary to a text file
with open("Executive_Summary.txt", "w") as f:
    f.write(summary_text)

print(summary_text)
print("\nProject Complete! Check your folder for all 4 output files.")


# ================================
# FINAL STEP - THE MASTER DASHBOARD
# ================================
print("\nCreating Master Dashboard...")

from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(16, 10), facecolor='#F4F4F4')
gs = GridSpec(2, 2, figure=fig)

# Top Left: The Executive Summary Text
ax_text = fig.add_subplot(gs[0, 0])
ax_text.axis('off')
ax_text.text(0.05, 0.95, summary_text, transform=ax_text.transAxes,
             fontsize=12, family='monospace', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

# Top Right: Risk vs Return Scatter
ax_scatter = fig.add_subplot(gs[0, 1])
ax_scatter.scatter(results['Portfolio_Volatility(%)'], results['Avg_Return(%)'],
                   s=300, c='#1F4E79', alpha=0.7)
for i, txt in enumerate(results['Strategy']):
    ax_scatter.annotate(txt, (results['Portfolio_Volatility(%)'][i], results['Avg_Return(%)'][i]),
                        xytext=(10,10), textcoords='offset points')
ax_scatter.set_title('Strategic Risk vs. Return', fontweight='bold')
ax_scatter.set_xlabel('Volatility (%)')
ax_scatter.set_ylabel('Avg Return (%)')

# Bottom: The Monte Carlo Future Projection
ax_mc = fig.add_subplot(gs[1, :])
ax_mc.plot(price_paths[:, :50], color='#2E75B6', alpha=0.1)
ax_mc.plot(price_paths.mean(axis=1), color='red', linewidth=3, label='Mean Projection')
ax_mc.set_title(f'Future Projection: {prob_gain}% Probability of Profit', fontweight='bold')
ax_mc.set_ylabel('Projected Value ($)')
ax_mc.legend()

plt.tight_layout(pad=3.0)
plt.savefig('FINAL_INVESTOR_REPORT.png', dpi=200)
print("Master Dashboard saved as FINAL_INVESTOR_REPORT.png!")
print("\nPROJECT COMPLETE. EXCELLENT WORK!")