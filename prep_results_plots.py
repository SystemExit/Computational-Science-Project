import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

# make sure 'plots' directory exists to safe plots in
os.makedirs('plots', exist_ok=True)

# Find files
csv_files = glob.glob("data/sim_results/**/*.csv", recursive=True)
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
def plot_group_with_bounds(modes_to_plot, title, x_name, x_value, filename, legend_outside=False):
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

            plt.fill_between(subset[x_value], subset['q1'], subset['q3'],
                             color=color, alpha=0.15)
            plt.plot(subset[x_value], subset['median'],
                     marker='o', markersize=7, linewidth=3,
                     label=label, color=color)

    if not found_any:
        plt.close()
        return

    plt.title(title, fontsize=18, fontweight='bold', pad=15)
    plt.xlabel(x_name, fontsize=14)
    plt.ylabel('Final Healthy Population (Susceptible Count)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper left', fontsize=12, frameon=True, shadow=True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Saved: {filename}")
    plt.show()


# Plot 1: Gender
group_1 = ['random', 'targeted_male', 'targeted_female']
plot_group_with_bounds(group_1, title="PrEP Effectiveness: Gender vs. Baseline Distribution", x_name='PrEP Coverage (Proportion of Group)',
                       x_value='prep', filename="plots/final_susc_gender.png")

# Plot 2: Sexual Orientation
group_2 = ['targeted_heterosexual', 'targeted_homosexual', 'targeted_bisexual']
plot_group_with_bounds(group_2, title="PrEP Effectiveness by Sexual Orientation", x_name='PrEP Coverage (Proportion of Group)',
                       x_value='prep', filename="plots/final_susc_orientation.png")

# Plot 3: Six supgroups
group_3 = ['targeted_m_homo', 'targeted_m_hetero', 'targeted_m_bi',
           'targeted_f_homo', 'targeted_f_hetero', 'targeted_f_bi']
plot_group_with_bounds(group_3, title="PrEP Effectiveness: Detailed Sub-group Analysis", x_name='PrEP Coverage (Proportion of Group)',
                       x_value='prep', filename="plots/final_susc_six_groups.png")


# Same plots with different x-axis value, grouped by scale of x-axis
# Plot 1:
group_4 = ['random', 'targeted_heterosexual']
plot_group_with_bounds(group_4, title="PrEP Effectiveness: Random vs. Heterosexual", x_name='PrEP Coverage (Amount of people)',
                       x_value='people', filename="plots/prep_effect_largest_scale.png")

# Plot 2: 
group_5 = ['targeted_male', 'targeted_female', 'targeted_m_hetero', 'targeted_f_hetero']
plot_group_with_bounds(group_5, title="PrEP Effectiveness: (heterosexual) male vs. female", x_name='PrEP Coverage (Amount of people)',
                       x_value='people', filename="plots/prep_effect_medium_scale.png")

# Plot 3:
group_6 = ['targeted_m_homo', 'targeted_m_bi',
           'targeted_f_homo', 'targeted_f_bi',
           'targeted_homosexual', 'targeted_bisexual']
plot_group_with_bounds(group_6, title="PrEP Effectiveness: bisexual vs. homosexual", x_name='PrEP Coverage (Amount of people)',
                       x_value='people', filename="plots/prep_effect_small_scale.png")





