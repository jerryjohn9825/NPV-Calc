import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_pv(rate, term, rental):
    # Calculate the monthly interest rate
    monthly_rate = rate / 12
    # Calculate Present Value (PV) using the provided formula
    pv = sum([rental / (1 + monthly_rate) ** i for i in range(1, term + 1)])
    return pv

def calculate_cbr(current_full_rental, remaining_term):
    # Calculate Contract Balance Residual (CBR)
    cbr = current_full_rental * remaining_term
    return cbr

def calculate_npv_sl_paydown_and_cbr(slc_securitized_rental, slc_interest_rate, inhouse_interest_rate, slc_nper, full_rental, full_term, start_date, rental_increase_percentage, rental_increase_month):
    # Initialize the monthly interest rate
    monthly_interest_rate = slc_interest_rate / 12
    inhouse_monthly_interest_rate = inhouse_interest_rate / 12
    
    # Initialize lists to store the SLC NPV, SLC Paydown, CBR, Inhouse PV values, cash collections, and dates
    slc_npv_values = []
    slc_paydown_values = []
    cbr_values = []
    inhouse_pv_values = []
    cash_collection_original_rental_values = []
    cash_collection_escalated_rental_values = []
    
    # Generate dates for the periods, now using the first of every month
    dates = pd.date_range(start=start_date, periods=full_term, freq='MS')  # 'MS' gives Month Start

    cumulative_rental = 0  # Initialize cumulative rental using full_rental
    cumulative_rental_with_increase = 0  # Initialize cumulative rental with increase using current_full_rental
    current_full_rental = full_rental  # Initialize the current full rental amount

    # Calculate the SLC NPV, SLC Paydown, CBR, Inhouse PV, and cash collections for each period
    for t in range(full_term):
        current_date = dates[t]
        
        # Apply the rental increase during the specified month based on the input parameter
        if current_date.month == rental_increase_month and t > 0:
            current_full_rental *= (1 + rental_increase_percentage / 100)
        
        if t < slc_nper:
            # SLC NPV calculation using slc_securitized_rental
            slc_npv = sum([slc_securitized_rental / (1 + monthly_interest_rate) ** i for i in range(1 + t, slc_nper)]) + slc_securitized_rental / (1 + monthly_interest_rate) ** t
        else:
            slc_npv = 0
        
        # SLC Paydown calculation using slc_securitized_rental (sum of rentals from period t+1 to the last period)
        slc_paydown = sum([slc_securitized_rental for _ in range(t, slc_nper)]) if t < slc_nper else 0
        
        # CBR calculation using the increased full rental (current_full_rental)
        cbr = calculate_cbr(current_full_rental, full_term - t)
        
        # Inhouse PV calculation using the full rental (without increase)
        inhouse_pv = calculate_pv(inhouse_interest_rate, full_term - t, full_rental)
        
        # Cash collection calculation without increase (using full rental)
        cumulative_rental += full_rental
        
        # Cash collection calculation with specified month increase (using current full rental)
        cumulative_rental_with_increase += current_full_rental
        
        slc_npv_values.append(slc_npv)
        slc_paydown_values.append(slc_paydown)
        cbr_values.append(cbr)
        inhouse_pv_values.append(inhouse_pv)
        cash_collection_original_rental_values.append(cumulative_rental)
        cash_collection_escalated_rental_values.append(cumulative_rental_with_increase)
    
    # Create a DataFrame to store the results
    results = pd.DataFrame({
        'Date': dates,
        'SLC NPV': slc_npv_values,
        'SLC Paydown': slc_paydown_values,
        'CBR': cbr_values,
        'Inhouse PV': inhouse_pv_values,
        'Cash Collection (@Original Rental)': cash_collection_original_rental_values,
        'Cash Collection (@Escalated Rental)': cash_collection_escalated_rental_values
    })

    # Truncate the SLC NPV and SLC Paydown values after they hit zero
    results['SLC NPV'] = results['SLC NPV'].where(results['SLC NPV'] > 0)
    results['SLC Paydown'] = results['SLC Paydown'].where(results['SLC Paydown'] > 0)
    
    return results

def plot_npv_sl_paydown_and_cbr(results):
    # Plotting the SLC NPV, SLC Paydown, CBR, Inhouse PV, and Cash Collections over periods
    plt.figure(figsize=(14, 8))  # Set the figure size
    plt.plot(results['Date'], results['SLC NPV'], marker='o', color='orange', label='SLC NPV')
    plt.plot(results['Date'], results['SLC Paydown'], marker='o', color='blue', label='SLC Paydown')
    plt.plot(results['Date'], results['CBR'], marker='o', color='green', label='CBR')
    plt.plot(results['Date'], results['Inhouse PV'], marker='o', color='red', label='Inhouse PV')
    plt.plot(results['Date'], results['Cash Collection (@Original Rental)'], marker='o', color='purple', label='Cash Collection (@Original Rental)')
    plt.plot(results['Date'], results['Cash Collection (@Escalated Rental)'], marker='o', color='brown', label='Cash Collection (@Escalated Rental)')
    plt.title('SLC NPV, SLC Paydown, CBR, Inhouse PV, and Cash Collections Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)

    # Set both x and y axes to start from zero at the same location
    plt.xlim(left=results['Date'].min())
    plt.ylim(bottom=0)

    # Collect first and last values for the legend
    first_last_labels = []
    for label in ['SLC NPV', 'SLC Paydown', 'CBR', 'Inhouse PV', 'Cash Collection (@Original Rental)', 'Cash Collection (@Escalated Rental)']:
        first_value = results[label].dropna().iloc[0]
        last_value = results[label].dropna().iloc[-1]
        first_last_labels.append(f'{label} (First: {first_value:.2f}, Last: {last_value:.2f})')

    # Add legend with first and last value
    plt.legend(first_last_labels, loc='upper left')

    plt.show()

# Example usage:
# Input Parameters
full_rental =  50  # Initial value for full rental
slc_securitized_rental = 0.96 * full_rental  # Rental is 96% of full rental
slc_interest_rate = 0.066
inhouse_interest_rate = 0.08  # Example Inhouse Interest Rate
slc_nper = 107
full_term = 180  # Full term for the calculation
start_date = '2024-09-01'  # Start date for the calculation
rental_increase_percentage = 3.99  # Rental increase percentage each year
rental_increase_month = 2  # Month when the rental increase occurs (e.g., 2 for February)

# Calculate SLC NPV, SLC Paydown, CBR, Inhouse PV, and Cash Collections
results = calculate_npv_sl_paydown_and_cbr(slc_securitized_rental, slc_interest_rate, inhouse_interest_rate, slc_nper, full_rental, full_term, start_date, rental_increase_percentage, rental_increase_month)

# Display the first result
print(results.head(20))

# Plot the SLC NPV, SLC Paydown, CBR, Inhouse PV, and Cash Collections over the full term
plot_npv_sl_paydown_and_cbr(results)
