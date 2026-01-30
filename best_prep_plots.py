import pandas as pd
import matplotlib.pyplot as plt
import os

# make sure 'plots' directory exists to safe plots in
os.makedirs('plots', exist_ok=True)

# import data
df_st = pd.read_csv("data/results_standard_mode/standard_weeks520_nodes1000_netseed67_iters50_RAW__20260128_101939.csv")
df_mho = pd.read_csv("data/sim_results/targeted_m_homo/targeted_m_homo_prep100_weeks520_nodes1000_netseed67_iters50_RAW__20260127_215617.csv")

# susceptible for standard vs male homosexual mode
s_st = df_st[[c for c in df_st.columns if 'susceptible' in c]]
s_mho = df_mho[[c for c in df_mho.columns if 'susceptible' in c]]

plt.figure(figsize=(14, 7))

plt.plot(s_st.median(axis=1), color='gray', label='Standard: No specific group PrEP targeting')
plt.fill_between(s_st.index, s_st.quantile(0.25, axis=1), s_st.quantile(0.75, axis=1), color='gray', alpha=0.2)

plt.plot(s_mho.median(axis=1), color='#7b0306', label='Targeted: 100% PrEP coverage for Gay Men')
plt.fill_between(s_mho.index, s_mho.quantile(0.25, axis=1), s_mho.quantile(0.75, axis=1), color='#7b0306', alpha=0.2)

plt.title('Impact of PrEP Strategy on Susceptible Population\n(Standard vs. 100% Targeted Coverage for Gay Men)', fontsize=14, fontweight='bold')
plt.xlabel('t (weeks)', fontsize=12)
plt.ylabel('Susceptible people (Median & IQR)', fontsize=12)
plt.grid(True, alpha=0.5)
plt.legend()
filename = 'plots/susceptible-standard_vs_mhomo.png'
plt.savefig(filename, dpi=300, bbox_inches='tight')
print(f"Saved: {filename}")
plt.show()

# acute and chronic for standard mode
ac_st = df_st[[c for c in df_st.columns if 'acute' in c]]
c_st = df_st[[c for c in df_st.columns if 'chronic' in c]]

plt.figure(figsize=(14, 7))

plt.plot(ac_st.median(axis=1), color='gray', label='Acute')
plt.fill_between(ac_st.index, ac_st.quantile(0.25, axis=1), ac_st.quantile(0.75, axis=1), color='gray', alpha=0.2)

plt.plot(c_st.median(axis=1), color='#7b0306', label='Chronic')
plt.fill_between(c_st.index, c_st.quantile(0.25, axis=1), c_st.quantile(0.75, axis=1), color='#7b0306', alpha=0.2)

plt.title('Acute vs Chronic population (standard mode)', fontsize=14, fontweight='bold')
plt.xlabel('t (weeks)', fontsize=12)
plt.ylabel('People', fontsize=12)
plt.grid(True, alpha=0.5)
plt.legend()
filename = 'plots/acute-chronic_standard.png'
plt.savefig(filename, dpi=300, bbox_inches='tight')
print(f"Saved: {filename}")
plt.show()

# aids and dead for standard mode
ai_st = df_st[[c for c in df_st.columns if 'aids' in c]]
d_st = df_st[[c for c in df_st.columns if 'dead' in c]]

plt.figure(figsize=(14, 7))

plt.plot(ai_st.median(axis=1), color='gray', label='Aids')
plt.fill_between(ai_st.index, ai_st.quantile(0.25, axis=1), ai_st.quantile(0.75, axis=1), color='gray', alpha=0.2)

plt.plot(d_st.median(axis=1), color='#7b0306', label='Dead')
plt.fill_between(d_st.index, d_st.quantile(0.25, axis=1), d_st.quantile(0.75, axis=1), color='#7b0306', alpha=0.2)

plt.title('Aids vs Dead population (standard mode)', fontsize=14, fontweight='bold')
plt.xlabel('t (weeks)', fontsize=12)
plt.ylabel('People', fontsize=12)
plt.grid(True, alpha=0.5)
plt.legend()
filename = 'plots/aids-dead_standard.png'
plt.savefig(filename, dpi=300, bbox_inches='tight')
print(f"Saved: {filename}")
plt.show()
plt.show()




