import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Fixed parameters
p = 0.03
qW = 0.9
qA = 0.35
m = 40001
CL = 1000
time_steps = 25  # Global definition to be used in the sidebar
p_bass = 0.03
q_bass = 0.35

st.title('Diffusion Model: SCARCITY PARADOX Simulation')

# Display fixed value parameters
st.sidebar.header('Fixed Model Parameters')
st.sidebar.markdown('''
- **p**: 0.03 (Innovation coefficient)
- **qW**: 0.9 (Imitation coefficient for word-of-mouth)
- **qA**: 0.35 (Imitation coefficient for advertising effect)
- **m**: 40,001 (Market potential)
- **CL**: 1,000 (Initial industry capacity)
- **Time Steps**: 25
- **p_bass**: 0.03 (Innovation coefficient for Bass model)
- **q_bass**: 0.35 (Imitation coefficient for Bass model)
''')

# Sidebar for user input parameters
st.sidebar.header('User Input Parameters')
TL = st.sidebar.number_input('TL (Time of Competitor Entry)', min_value=1, max_value=time_steps, value=4, step=1)
CE = st.sidebar.slider('CE (New Total Industry Capacity)', min_value=4000, max_value=12000, value=4000, step=1000)

# Simulation function
def simulate(TL, CE):

    # Initialize other variables for both models
    w_t_1 = 0
    N_t_1 = 0
    I_t_1 = 0
    N_t_1_bass = 0

    # Initialize variables to store special time periods for both models
    first_10_percent_time = None
    first_90_percent_time = None
    first_10_percent_time_bass = None
    first_90_percent_time_bass = None
    cwbm_crosses_bass = None

    # Lists to store results
    results_combined = []

    # Run the simulation for both models
    for t in range(1, time_steps + 1):
        # Stop the simulation if N(t-1) reached the market size 'm'
        if N_t_1 >= m:
            break

        # Update capacity for CWBM-2-STAGE
        capacity = CL if t < TL else CE

        # Calculate variables for CWBM-2-STAGE
        q1_m_w_t = (qW / m) * w_t_1
        q2_m_N_t = (qA / m) * N_t_1
        m_w_N_t_1 = m - w_t_1 - N_t_1
        s_prime_t = (p + q1_m_w_t + q2_m_N_t) * m_w_N_t_1
        D_t = s_prime_t + w_t_1
        s_t = min(capacity, D_t, m - N_t_1)
        end_inventory = max(0, (I_t_1 + D_t) - capacity) if t != 1 else 0
        w_t = max(0, D_t - s_t)
        N_t = N_t_1 + s_t

        # Calculate N(t) for Standard Bass Model
        N_t_bass = N_t_1_bass + (p_bass + (q_bass * N_t_1_bass / m)) * (m - N_t_1_bass)

        # Append results to the list
        results_combined.append([t, p, q1_m_w_t, q2_m_N_t, m_w_N_t_1, w_t_1, s_prime_t, D_t, I_t_1, s_t, end_inventory, w_t, N_t, capacity, N_t_bass])

        # Update special time periods for CWBM-2-STAGE
        if first_10_percent_time is None and 0.075 * m <= N_t:
            first_10_percent_time = t
        if first_90_percent_time is None and 0.875 * m <= N_t:
            first_90_percent_time = t

        # Update special time periods for Standard Bass Model
        if first_10_percent_time_bass is None and 0.075 * m <= N_t_bass:
            first_10_percent_time_bass = t
        if first_90_percent_time_bass is None and 0.875 * m <= N_t_bass:
            first_90_percent_time_bass = t

        # Update state variables for the next time step
        w_t_1 = w_t
        N_t_1 = N_t
        I_t_1 = end_inventory
        N_t_1_bass = N_t_bass

        # Update the time when CWBM-2-STAGE crosses the Standard Bass Model
        if cwbm_crosses_bass is None and N_t > N_t_bass:
            cwbm_crosses_bass = t

    # Convert the results list to a DataFrame
    df_combined = pd.DataFrame(results_combined, columns=['Time', 'p', 'q1/m*w(t)', 'q2/m*N(t)', 'm-w(t-1)-N(t-1)', 'W(t-1)', "s'(t)", "D(t)=s'(t)+w(t-1)", 'I(t-1)', 's(t)', 'End Inventory', 'w(t)', 'N(t)', 'Capacity', 'N(t)_Bass'])

    # Return the DataFrame and any other variables you need
    #return df_combined, first_10_percent_time, first_90_percent_time, first_10_percent_time_bass, first_90_percent_time_bass, cwbm_crosses_bass
    return df_combined, first_10_percent_time, first_90_percent_time, first_10_percent_time_bass, first_90_percent_time_bass, cwbm_crosses_bass

# Button to run simulation
if st.button('Run Simulation'):
    # Pass CL and CE to the simulate function
    df_combined, first_10, first_90, first_10_bass, first_90_bass, cwbm_crosses = simulate(TL, CE)
    
    st.write("Simulation Results")
    st.dataframe(df_combined)
    
    st.write(f"10% of N reached at time (CWBW-2-STAGE): {first_10}")
    st.write(f"90% of N reached at time (CWBW-2-STAGE): {first_90}")
    st.write(f"10% of N reached at time (Standard Bass): {first_10_bass}")
    st.write(f"90% of N reached at time (Standard Bass): {first_90_bass}")
    st.write(f"CWBW-2-STAGE crosses Bass at time: {cwbm_crosses}")

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(df_combined['Time'], df_combined['N(t)'], marker='o', label='CWBW-2-STAGE N(t)')
    ax.plot(df_combined['Time'], df_combined['N(t)_Bass'], marker='x', label='Standard Bass N(t)')
    ax.set_title('N(t) Over Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('N(t)')
    ax.legend()
    st.pyplot(fig)

