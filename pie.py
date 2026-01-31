import matplotlib.pyplot as plt
import os

# make sure 'plots' directory exists to safe plots in
os.makedirs('plots', exist_ok=True)

# Create pie plot of class distribution in the network made with network_seed = 67
labels = ['m_homo', 'm_hetero', 'm_bi', 'f_homo', 'f_hetero', 'f_bi']
values = [30, 431, 21, 10, 468, 40] 

colors = [
    '#145f82',  # m_homo
    '#ff7f0e',  # m_hetero
    '#186c24',  # m_bi
    '#0f9ed5',  # f_homo
    '#a02b93',  # f_hetero
    '#4ea72e'   # f_bi
]

plt.figure(figsize=(6, 4))
plt.pie(values, colors=colors, startangle=90)
plt.title('Population Distribution')
plt.legend(labels, loc='lower center', ncol=6, bbox_to_anchor=(0.5, -0.15))
filename = 'plots/class_distribution.png'
plt.savefig(filename, dpi=300, bbox_inches='tight')
print(f"Saved: {filename}")
plt.show()


