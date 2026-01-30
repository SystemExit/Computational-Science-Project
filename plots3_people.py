import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

# Find files
csv_files = glob.glob("data/**/*.csv", recursive=True)
all_results = []

class_amounts = {'targeted_m_homo': 30, 'targeted_m_hetero': 431, 'targeted_m_bi': 21, 
                 'targeted_f_homo': 10, 'targeted_f_hetero': 468, 'targeted_f_bi': 40, 
                 'targeted_heterosexual': 899, 'targeted_homosexual': 40, 'targeted_bisexual': 61, 
                 'targeted_male': 482, 'targeted_female': 518, 'random': 1000}

for file in csv_files:
    if "~$" in file: continue

    try:
        df = pd.read_csv(file)
        if df.empty: continue

        # Last week of simulation (end results)
        last_week = df['week'].max()
        last_row = df[df['week'] == last_week]

        mode = str(last_row['mode'].iloc[0]).strip()
        prep_val = float(last_row['prep'].iloc[0])

        # Find susceptible columns
        susc_cols = [c for c in df.columns if c.startswith('susceptible_') and c.split('_')[-1].isdigit()]

        if susc_cols:
            vals = last_row[susc_cols].values[0]
            median_val = np.median(vals)
            q1_val = np.quantile(vals, 0.25)
            q3_val = np.quantile(vals, 0.75)
        elif 'susceptible_median' in df.columns:
            median_val = last_row['susceptible_median'].values[0]
            q1_val = last_row['susceptible_q1'].values[0]
            q3_val = last_row['susceptible_q3'].values[0]
        else:
            continue

        all_results.append({
            'mode': mode,
            'prep': prep_val,
            'people': prep_val * class_amounts[mode],
            'median': median_val,
            'q1': q1_val,
            'q3': q3_val
        })

    except Exception as e:
        print(f"Error for {file}: {e}")

summary_df = pd.DataFrame(all_results).sort_values(by='prep')

# Function to plot groups
def plot_group_with_bounds(modes_to_plot, title, filename, legend_outside=False):
    figsize = (14, 7) if legend_outside else (12, 7)
    plt.figure(figsize=figsize)

    colors = plt.cm.tab10.colors

    found_any = False
    for i, mode in enumerate(modes_to_plot):
        subset = summary_df[summary_df['mode'] == mode]

        if not subset.empty:
            found_any = True
            color = colors[i % len(colors)]
            label = mode.replace('targeted_', '').replace('_', ' ').title()
            if label == "Random": label = "Random"

            plt.fill_between(subset['people'], subset['q1'], subset['q3'],
                             color=color, alpha=0.15)
            plt.plot(subset['people'], subset['median'],
                     marker='o', markersize=7, linewidth=3,
                     label=label, color=color)

    if not found_any:
        plt.close()
        return

    plt.title(title, fontsize=18, fontweight='bold', pad=15)
    plt.xlabel('PrEP Coverage (Amount of people)', fontsize=14)
    plt.ylabel('Final Healthy Population (Susceptible Count)', fontsize=14)
    # plt.xticks(np.arange(0, 1000, 0.1))
    # plt.xlim(-0.02, 1.02)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper left', fontsize=12, frameon=True, shadow=True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Opgeslagen: {filename}")
    plt.show()

# Plot 1: Gender
# group_1 = ['random', 'targeted_male', 'targeted_female']
group_1 = ['random', 'targeted_heterosexual']
plot_group_with_bounds(group_1, "PrEP Effectiveness: Random vs. Heterosexual", "final_susc_large.png")

# Plot 2: Sexual Orientation
# group_2 = ['targeted_heterosexual', 'targeted_homosexual', 'targeted_bisexual']
group_2 = ['targeted_male', 'targeted_female', 'targeted_m_hetero', 'targeted_f_hetero']
plot_group_with_bounds(group_2, "PrEP Effectiveness: (heterosexual) male vs. female", "final_susc_medium.png")

# Plot 3: Six supgroups
# group_3 = ['targeted_m_homo', 'targeted_m_hetero', 'targeted_m_bi',
#            'targeted_f_homo', 'targeted_f_hetero', 'targeted_f_bi']
group_3 = ['targeted_m_homo', 'targeted_m_bi',
           'targeted_f_homo', 'targeted_f_bi',
           'targeted_homosexual', 'targeted_bisexual']
plot_group_with_bounds(group_3, "PrEP Effectiveness: bisexual vs. homosexual", "final_susc_small.png")
