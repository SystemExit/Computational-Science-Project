from network_model import NetworkModel

import customtkinter as ctk
import numpy as np
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
import csv
from pathlib import Path
from datetime import datetime

#===========================================================================================================================================
# GUI SIMULATION VARIABLES AND BUTTONS
#===========================================================================================================================================

# === VARIABLES ===

# NUMBER OF NODES: Sets the total population size within the network.
# DELAY: Time between each update
# INITIAL OUTBREAK PROPORTION: Sets the percentage of people who have HIV at t = 0
# MODEL SEED: Controls the randomness of virus transmission, state changes etc.
# USE MODEL SEED CHECKBOX:
#     - CHECKED: Uses the fixed "Model Seed" for 100% reproducible results.
#     - UNCHECKED: Interactions are fully randomized every time the model runs.
# NETWORK SEED: Generates a consistent, specific network structure (topology).
# MAX TIMESTEPS: Sets the amount of weeks the simulation will run.
# ITERATIONS: The number of separate simulation runs to perform for statistical calculations.
# STEPS PER UPDATE: How many weeks pass internally before the GUI redraws the visual.
# PREP AMOUNT: Adjusts the proportion of the population using preventative medication.
# MODES: Defines the targeting strategy (who will receive prep).

# === BUTTONS ===

# NETWORK VIEW: Switches to the node-link diagram showing the live state of individuals.
# STATS VIEW: Switches to the line charts showing the population trends over time.
# DEFAULT SETTINGS: Clears all current inputs and restores the original values.
# APPLY SETTINGS: Rebuilds the models and network layout using the current GUI values.
# EXPORT CSV: Saves the raw data from the current session for all iterations in a folder named "sim_results".
# START: Begins the automated animation loop.
# PAUSE: Freezes the simulation at the current timestep.
# STEP: Advances the simulation by exactly one week.
# BATCH CSV: Automates a massive data export across multiple PrEP levels and modes, 
#   users can set the modes and prep amounts in the function "batch_export()", results will be put in the "sim_results" folder.

#===========================================================================================================================================
# FUNCTIONS
#===========================================================================================================================================

def redraw():
    """
    Redraw the network visualization based on the current state of the model.

    It clears the existing network plot and draws all nodes and
    edges again using the current graph layout. Each node is colored according
    to its state (e.g. susceptible, acute, chronic, AIDS, etc.).
    The plot title is updated to show the current timestep and total number
    of nodes. After updating the network view, the statistics plots are
    refreshed to stay in sync with the model.
    """

    # Reset the plot before redrawing the network
    ax.clear()
    ax.set_axis_off()

    # Draw edges and nodes and legend with the correct state color
    nx.draw_networkx_edges(model.graph, pos, ax=ax, alpha=0.15, width=0.5)
    colors = [state_colors.get(model.graph.nodes[n]["state"], "lightgray") for n in model.graph.nodes]
    nx.draw_networkx_nodes(model.graph, pos, ax=ax, node_size=15, node_color=colors)
    ax.legend(
    handles=[Line2D([0],[0], marker='o', linestyle='None', markersize=6,
                    markerfacecolor=c, markeredgecolor='none', label=s.capitalize())
             for s, c in state_colors.items()],
    loc="upper right", fontsize=8, frameon=True
    )

    # Update the title so it has the correct timestep noted
    ax.set_title(f"t = {t}   |   nodes = {model.graph.number_of_nodes()}")

    # Refresh canvas and sync stats view if active
    canvas.draw_idle()
    if current_view == "stats":
        redraw_stats()

def step_once():
    """
    Advance the simulation by one timestep.

    If the maximum number of timesteps has not been reached, this function
    performs a single model update, increments the global timestep counter,
    and redraws the network and statistics plots to reflect the new state.
    """
    global t

    # Stop if max t has been reached
    if t >= int(max_t_input.get()):
        return

    # Step all models and update t
    for m in models:
        m.step()
    t += 1

    # Update GUI
    window.title(f"Network Model | t = {t}")
    if current_view == "network":
        redraw()
    else:
        redraw_stats()

def tick():
    """
    Advance the simulation repeatedly if the animation is running.

    If the simulation is currently running and the maximum number of
    timesteps has not been reached, this function performs one model
    update, increments the timestep counter, redraws the network and
    statistics plots, and then runs again after a specified delay. 
    """
    global running, t

    # Exit if paused or max timestep reached
    if not running or t >= int(max_t_input.get()):
        return

    # Determine how many steps to run this update
    max_t = int(max_t_input.get())
    steps_per_update = max(1, int(steps_per_update_input.get()))
    steps = min(steps_per_update, max_t - t)

    # Advance the model for the computed number of steps
    for _ in range(steps):
        for m in models:
            m.step()
        t += 1
        if not running:
            break

    # Update UI and redraw active view
    window.title(f"Network Model | t = {t}")
    if current_view == "network":
        redraw()
    else:
        redraw_stats()

    # Schedule the next tick
    window.after(int(delay_input.get()), tick)

def start_animation():
    """
    Start the simulation animation.

    If the animation is not already running, this function sets the
    running variable to true and starts the update loop by calling the tick function.
    """
    global running
    if running:
        return
    running = True
    tick()

def stop_animation():
    """
    Stop the simulation animation.

    Sets the running variable to False, which causes the animation loop
    to stop on the next tick.
    """
    global running
    running = False

def add_variable_block(
    parent,
    text,
    input_type,
    default,
    value_type,    
    label_row,
    label_col=0,
    slider_from=0,
    slider_to=1,
    slider_steps=100,
    slider_row=0,
    slider_col=1,
    entry_row=0,
    entry_col=2,
    padx=15,
    pady=5
):
    """
    Create a labeled input control for a simulation setting.

    Depending on input_type, this function creates either a slider with
    a linked entry field or an entry only input. The value and its default
    are stored so the setting can be reset later.
    
    parent: Parent widget that contains the input controls.
    text: Text displayed in the label for this setting.
    input_type: Type of input to create ("slider" for slider + entry, anything else for entry-only (e.g. "Number").
    default: Default numeric value for the setting.
    label_row: Grid row position of the label.
    label_col: Grid column position of the label.
    slider_from: Minimum value of the slider (slider input only).
    slider_to: Maximum value of the slider (slider input only).
    slider_steps: Number of discrete steps on the slider.
    slider_row: Grid row position of the slider (slider input only).
    slider_col: Grid column position of the slider (slider input only).
    entry_row: Grid row position of the entry field.
    entry_col: Grid column position of the entry field.
    padx: Horizontal padding applied to the widgets.
    pady: Vertical padding applied to the widgets.

    Copy blocks below to create one of 2 types of inputs:

    delay_input = add_variable_block(
        controls_frame,
        "Delay (ms):",
        "slider",
        50,

        label_row=2,

        slider_from=10,
        slider_to=500,
        slider_steps=49,
        slider_row=2,
        slider_col=1,

        entry_row=2,
        entry_col=2
    )

    seed_input = add_variable_block(
        controls_frame,
        "Seed:",
        "number",
        42,

        label_row=3,
        entry_row=3,
        entry_col=1
    )
    """
    # Create a variable to store the value (int or float) and remember its default so it can be reset if needed
    if value_type == "int":
        value = ctk.IntVar()
        value.set(int(default))
    else:
        value = ctk.DoubleVar()
        value.set(float(default))
    settings.append((text, value, default))

    # Create and place the label
    label = ctk.CTkLabel(parent, text=text)
    label.grid(row=label_row, column=label_col, padx=padx, pady=pady, sticky="w")

    # If the input type is a slider, create a slider and an entry field
    if input_type == "slider":
        slider_widget = ctk.CTkSlider(
            parent,
            from_=slider_from,
            to=slider_to,
            number_of_steps=slider_steps
        )
        slider_widget.grid(row=slider_row, column=slider_col, padx=padx, pady=pady)
        slider_widget.set(default)

        entry = ctk.CTkEntry(parent, width=70, textvariable=value)
        entry.grid(row=entry_row, column=entry_col, padx=padx, pady=pady)

        def slider_moved(val):
            """
            Update the stored value when the slider is moved,
            keeping the entry field in sync.
            """
            if value_type == "int":
                value.set(int(round(float(val))))
            else:
                value.set(round(float(val), 6))

        slider_widget.configure(command=slider_moved)

        def entry_changed(*args):
            """
            Update the slider position when the entry value changes.
            Ignores invalid or incomplete input.
            """
            try:
                slider_widget.set(float(value.get()))
            except ValueError:
                pass

        value.trace("w", entry_changed)
        
    # Otherwise, create only an entry field
    else:
        entry = ctk.CTkEntry(parent, width=70, textvariable=value)
        entry.grid(row=entry_row, column=entry_col, padx=padx, pady=pady, sticky="w")

    return value

def apply_settings():
    """
    Apply the current GUI settings and rebuild the simulation.

    Stops any running animation, resets the timestep counter, creates
    a new model using the current input values, recomputes the network
    layout, and redraws the visualization to reflect the updated settings.
    """
    global running, t, model, models, pos

    # Stop the animation and reset time
    running = False
    t = 0

    # Recreate the models using current input values
    models = create_models()
    model = models[0]

    # Recompute the network layout and redraw with the new settings
    pos = nx.random_layout(model.graph, seed=int(network_seed_input.get()))
    redraw()

def reset_model():
    """
    Reset the simulation and all GUI settings to their default values.

    Stops the animation, restores all input controls to their defaults,
    resets the timestep counter, rebuilds the model using those default
    values, recomputes the network layout, and redraws the visualization.
    """
    global running, t, model, models, pos

    # Stop animation
    running = False

    # Reset all variables to the default setting
    for name, var, default in settings:
        var.set(default)
    use_seed_var.set(False)

    # Reset time and recreate models
    t = 0
    models = create_models()
    model = models[0]

    # Recompute the network layout and redraw with the new settings
    pos = nx.random_layout(model.graph, seed=int(network_seed_input.get()))
    redraw()

def show_network_plot():
    """
    Switch the view to the network visualization.

    Hides the statistics frame and displays the network plot frame.
    """
    global current_view
    current_view = "network"
    stats_frame.grid_remove()
    plot_frame.grid()

def show_stats_plot():
    """
    Switch the view to the statistics plots.

    Hides the network plot frame, displays the statistics frame,
    and redraws the statistics to ensure they are up to date.
    """
    global current_view
    current_view = "stats"
    plot_frame.grid_remove()
    stats_frame.grid()
    redraw_stats()

def plot_states(ax, data, keys, colors=None):
    """
    Plots median line and Q1–Q3 band for each key per timestep.
    """
    ax.clear()
    if not data:
        return

    if isinstance(data[0], dict):
        runs = [data]
    else:
        runs = data

    T = min(len(r) for r in runs)
    if T == 0:
        return

    timesteps = np.arange(T)

    for key in keys:
        vals = np.array([[r[t][key] for t in range(T)] for r in runs], dtype=float)

        median = np.median(vals, axis=0) 
        q1 = np.quantile(vals, 0.25, axis=0)         
        q3 = np.quantile(vals, 0.75, axis=0)         

        color = colors.get(key) if colors else None

        ax.plot(timesteps, median, label=f"{key.capitalize()} (median)", color=color)
        ax.fill_between(timesteps, q1, q3, alpha=0.2, color=color)

    ax.legend()

def redraw_stats():
    """
    Update the statistics plots to reflect the current simulation state.

    Plots the time evolution of each epidemiological state using the
    stored state history, updates subplot titles and axis labels, sets
    a shared figure title with the current timestep and total number of
    nodes, and refreshes the statistics canvas.
    """
    plot_states(stats_ax_1, [m.states_per_time for m in models], PLOT_1_KEYS, colors=state_colors)
    plot_states(stats_ax_2, [m.states_per_time for m in models], PLOT_2_KEYS, colors=state_colors)
    plot_states(stats_ax_3, [m.states_per_time for m in models], PLOT_3_KEYS, colors=state_colors)
    plot_states(stats_ax_4, [m.states_per_time for m in models], PLOT_4_KEYS, colors=state_colors)

    n = model.graph.number_of_nodes()

    stats_ax_1.set_title("Susceptible")
    stats_ax_2.set_title("Acute")
    stats_ax_3.set_title("Chronic")
    stats_ax_4.set_title("AIDS / Dead")

    for ax in [stats_ax_1, stats_ax_2, stats_ax_3, stats_ax_4]:
        ax.set_xlabel("t (weeks)")
        ax.set_ylabel("People")

    stats_fig.suptitle(f"t = {t}   |   nodes = {n}")
    stats_canvas.draw_idle()

def export_csv_raw_runs(output_dir=None):
    """
    Export raw state counts for each iteration at each timestep.
    """
    if output_dir is None:
        data_dir = Path("sim_results")
    else:
        data_dir = Path(output_dir)

    data_dir.mkdir(parents=True, exist_ok=True)

    KEYS = ["susceptible", "acute", "chronic", "aids", "dead"]

    mode = mode_var.get()
    prep = float(prep_amount_input.get())
    max_week = t  
    prep_pct = int(prep * 100)
    nodes = int(num_nodes_input.get())
    net_seed = int(network_seed_input.get())
    iters = int(iterations_input.get())

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"{mode}"
        f"_prep{prep_pct}"
        f"_weeks{max_week}"
        f"_nodes{nodes}"
        f"_netseed{net_seed}"
        f"_iters{iters}"
        f"_RAW__{timestamp}.csv"
    )

    filepath = data_dir / filename

    runs = [m.states_per_time for m in models]
    num_runs = len(runs)
    T = max_week + 1

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        header = ["week", "mode", "prep"]
        for run_idx in range(num_runs):
            for k in KEYS:
                header.append(f"{k}_{run_idx+1}")
        writer.writerow(header)

        for week in range(T):
            row = [week, mode, prep]

            for r in runs:
                if week < len(r):
                    d = r[week]
                else:
                    d = {k: 0 for k in KEYS}

                for k in KEYS:
                    row.append(d.get(k, 0))

            writer.writerow(row)

    print(f"Raw per-run CSV exported to {filepath}")

def create_models():
    """
    Create a list of models for multiple iterations (runs).
    """
    k = int(iterations_input.get())

    models = []
    for i in range(k):
        window.title(f"Network Model | Creating model {i+1}/{k}")
        window.update()
        models.append(NetworkModel(
            seed=(int(seed_input.get()) + i) if use_seed_var.get() else None,
            network_seed=int(network_seed_input.get()),
            num_nodes=int(num_nodes_input.get()),
            initial_outbreak_proportion=float(initial_outbreak_prop_input.get()), 
            mode = mode_var.get(),
            prep_amount = float(prep_amount_input.get()),
        ))
    window.title(f"Network Model | Ready ({k} runs)")
    return models

def batch_export():
    """
    Loops over the the target modes in "modes" for each prep value in "prep_values" and exports it.
    """
    global running, t, models, model

    #===========================================================================================================================================    
    # EDIT THESE VALUES ONLY
    #===========================================================================================================================================

    prep_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    modes = [
        "standard"

        #targeted_m_homo",
        #targeted_m_hetero",
        #"targeted_m_bi",

        #"targeted_f_homo",
        #"targeted_f_hetero",
        #targeted_f_bi",

        # targeted_homosexual
        #"targeted_heterosexual",
        #"targeted_bisexual"

        #"targeted_male",
        #"targeted_female"

    ]

    max_t = 520
    iterations = 50
    num_nodes = 1000
    network_seed = 67

    #===========================================================================================================================================

    #===========================================================================================================================================

    running = False

    max_t_input.set(max_t)
    iterations_input.set(iterations)
    num_nodes_input.set(num_nodes)
    network_seed_input.set(network_seed)

    data_root = Path("data")
    data_root.mkdir(exist_ok=True)

    total_jobs = len(modes) * len(prep_values)
    job = 1

    for mode in modes:
        mode_var.set(mode)

        mode_dir = data_root / mode
        mode_dir.mkdir(exist_ok=True)

        for prep_val in prep_values:
            prep_val = float(prep_val)
            prep_amount_input.set(prep_val)
            t = 0

            window.title(
                f"Batch export {job}/{total_jobs} | mode={mode} | PrEP={prep_val}"
            )
            window.update_idletasks()

            try:
                models = create_models()
                model = models[0]

                while t < max_t:
                    for m in models:
                        m.step()
                    t += 1

                export_csv_raw_runs(output_dir=mode_dir)

            except ValueError as e:
                print(
                    f"Skipping mode={mode}, PrEP={prep_val} "
                    f"(reason: {e})"
                )

            job += 1

    window.title("Network Model | BATCH EXPORT DONE")

#===========================================================================================================================================
# GLOBAL SETTINGS
#===========================================================================================================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("red_theme.json")

window = ctk.CTk()
window.title("Network Model")
window.geometry("1920x1080")

controls_frame = ctk.CTkFrame(window, fg_color="transparent")
controls_frame.grid(row=0, column=0, sticky="nw", padx=15, pady=15)

plot_frame = ctk.CTkFrame(window, fg_color="transparent")
plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
plot_frame.grid_rowconfigure(0, weight=1)
plot_frame.grid_columnconfigure(0, weight=1)

stats_frame = ctk.CTkFrame(window, fg_color="transparent")
stats_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
stats_frame.grid_rowconfigure(0, weight=1)
stats_frame.grid_columnconfigure(0, weight=1)

stats_frame.grid_remove()
  
window.grid_columnconfigure(1, weight=1)  
window.grid_rowconfigure(0, weight=1)

fig = Figure(figsize=(6, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_axis_off()

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=10,
    pady=10
)

stats_fig = Figure(figsize=(6, 6), dpi=100)

stats_ax_1 = stats_fig.add_subplot(221)
stats_ax_2 = stats_fig.add_subplot(222)
stats_ax_3 = stats_fig.add_subplot(223)
stats_ax_4 = stats_fig.add_subplot(224)

stats_fig.subplots_adjust(hspace=0.4, wspace=0.4)

PLOT_1_KEYS = ["susceptible"]
PLOT_2_KEYS = ["acute"]
PLOT_3_KEYS = ["chronic"]
PLOT_4_KEYS = ["aids", "dead"]

stats_canvas = FigureCanvasTkAgg(stats_fig, master=stats_frame)
stats_canvas.get_tk_widget().grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=10,
    pady=10
)

state_colors = {
    "susceptible": "lightgray",
    "acute": "red",
    "chronic": "orange",
    "aids": "purple",
    "dead": "black",
}

reset_btn = ctk.CTkButton(
    controls_frame,
    text="Default Settings",
    command=reset_model,
    fg_color="black",
    hover_color="#333333",
    text_color="white"
)
reset_btn.grid(row=23, column=0, padx=15, pady=(10, 10), sticky="w")

start_btn = ctk.CTkButton(controls_frame, text="Start", command=start_animation)
start_btn.grid(row=24, column=0, padx=15, pady=(10, 10), sticky="w")

stop_btn = ctk.CTkButton(controls_frame, text="Pause", command=stop_animation)
stop_btn.grid(row=24, column=1, padx=15, pady=(10, 10), sticky="w")

step_btn = ctk.CTkButton(controls_frame, text="Step", command=step_once)
step_btn.grid(row=24, column=2, padx=15, pady=(10, 10), sticky="w")

apply_btn = ctk.CTkButton(
    controls_frame,
    text="Apply Settings",
    command=apply_settings,
    fg_color="black",
    hover_color="#333333",
    text_color="white"
)
apply_btn.grid(row=23, column=1, padx=15, pady=(10, 10), sticky="w")

export_btn = ctk.CTkButton(
    controls_frame,
    text="Export CSV",
    command=export_csv_raw_runs,   
    fg_color="black",
    hover_color="#333333",
    text_color="white"
)
export_btn.grid(row=23, column=2, padx=15, pady=(10, 10), sticky="w")

network_view_btn = ctk.CTkButton(
    controls_frame,
    text="Network view",
    command=show_network_plot,
    fg_color="white",
    border_color="black",
    border_width=2,
    text_color="black",
    hover_color="#f0f0f0"
)
network_view_btn.grid(row=0, column=0, padx=(15), pady=(5, 10), sticky="w")

stats_view_btn = ctk.CTkButton(
    controls_frame,
    text="Stats view",
    command=show_stats_plot,
    fg_color="white",
    border_color="black",
    border_width=2,
    text_color="black",
    hover_color="#f0f0f0"
)
stats_view_btn.grid(row=0, column=1, padx=(15), pady=(5, 10), sticky="w")

mode_var = ctk.StringVar(value="standard")

mode_menu = ctk.CTkOptionMenu(
    controls_frame,
    values=[
        "standard", "random",
        "targeted_m_homo", "targeted_m_hetero", "targeted_m_bi",
        "targeted_f_homo", "targeted_f_hetero", "targeted_f_bi",
        "targeted_homosexual", "targeted_heterosexual", "targeted_bisexual",
        "targeted_male", "targeted_female"
    ],
    variable=mode_var,

    fg_color="white",
    text_color="black",

    button_color="#e6e6e6",
    button_hover_color="#d9d9d9",

    dropdown_fg_color="white",
    dropdown_text_color="black",
    dropdown_hover_color="#f0f0f0",
)

settings = []

batch_btn = ctk.CTkButton(
    controls_frame,
    text="Batch CSV",
    command=batch_export,
    fg_color="#8B0000",
    hover_color="#5A0000",
    text_color="white"
)
batch_btn.grid(row=26, column=0, padx=15, pady=(10, 10), sticky="w")

#===========================================================================================================================================
# VARIABLE INPUT FIELDS
#===========================================================================================================================================

num_nodes_input = add_variable_block(
    controls_frame, "Number of nodes:", "slider", 1000, value_type="int",
    label_row=1, slider_from=0, slider_to=2000, slider_steps=100, slider_row=1, slider_col=1, entry_row=1, entry_col=2
)

delay_input = add_variable_block(
    controls_frame, "Delay (ms):", "slider", 50, value_type="int",
    label_row=2, slider_from=10, slider_to=500, slider_steps=49, slider_row=2, slider_col=1, entry_row=2, entry_col=2
)

initial_outbreak_prop_input = add_variable_block(
    controls_frame, "Initial outbreak proportion:", "slider", 0.11, value_type="float",
    label_row=3, slider_from=0.0, slider_to=0.5, slider_steps=50, slider_row=3, slider_col=1, entry_row=3, entry_col=2
)

seed_input = add_variable_block(
    controls_frame, "Model seed:", "number", 42, value_type="int",
    label_row=15, entry_row=15, entry_col=1
)

use_seed_var = ctk.BooleanVar(value=False) 

use_seed_chk = ctk.CTkCheckBox(
    controls_frame,
    text="Use model seed",
    variable=use_seed_var
)
use_seed_chk.grid(row=15, column=2, padx=15, pady=5, sticky="w")

network_seed_input = add_variable_block(
    controls_frame, "Network seed:", "number", 67, value_type="int",
    label_row=16, entry_row=16, entry_col=1
)

max_t_input = add_variable_block(
    controls_frame, "Max timesteps:", "number", 520, value_type="int",
    label_row=17, entry_row=17, entry_col=1
)

iterations_input = add_variable_block(
    controls_frame, "Iterations (runs):", "number", 3, value_type="int",
    label_row=18, entry_row=18, entry_col=1
)

steps_per_update_input = add_variable_block(
    controls_frame, "Steps per update:", "number", 10, value_type="int",
    label_row=19, entry_row=19, entry_col=1
)

prep_amount_input = add_variable_block(
    controls_frame, "Prep amount", "number", 0.1, value_type="float",
    label_row=20, entry_row=20, entry_col=1
)

ctk.CTkLabel(controls_frame, text="Mode:").grid(row=21, column=0, padx=15, pady=5, sticky="w")
mode_menu.grid(row=21, column=1, padx=15, pady=5, sticky="w")

#===========================================================================================================================================
# INITIAL MODEL CREATION
#===========================================================================================================================================

iter_stats = None 
current_view = "network"
running = False
t = 0

models = create_models()
model = models[0]  

pos = nx.random_layout(model.graph, seed=int(network_seed_input.get()))
#replace all instances with either random_layout or spring_layout for either speed or looks

redraw()


window.mainloop()



