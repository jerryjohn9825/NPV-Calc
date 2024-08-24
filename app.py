from flask import Flask, request, render_template
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Existing functions go here
def calculate_pv(rate, term, rental):
    monthly_rate = rate / 12
    pv = sum([rental / (1 + monthly_rate) ** i for i in range(1, term + 1)])
    return pv

def calculate_cbr(current_full_rental, remaining_term):
    cbr = current_full_rental * remaining_term
    return cbr

def calculate_npv_sl_paydown_and_cbr(slc_securitized_rental, slc_interest_rate, inhouse_interest_rate, slc_nper, full_rental, full_term, start_date, rental_increase_percentage, rental_increase_month):
    monthly_interest_rate = slc_interest_rate / 12
    inhouse_monthly_interest_rate = inhouse_interest_rate / 12
    
    slc_npv_values = []
    slc_paydown_values = []
    cbr_values = []
    inhouse_pv_values = []
    cash_collection_original_rental_values = []
    cash_collection_escalated_rental_values = []
    
    dates = pd.date_range(start=start_date, periods=full_term, freq='MS')

    cumulative_rental = 0
    cumulative_rental_with_increase = 0
    current_full_rental = full_rental

    for t in range(full_term):
        current_date = dates[t]
        
        if current_date.month == rental_increase_month and t > 0:
            current_full_rental *= (1 + rental_increase_percentage / 100)
        
        if t < slc_nper:
            slc_npv = sum([slc_securitized_rental / (1 + monthly_interest_rate) ** i for i in range(1 + t, slc_nper)]) + slc_securitized_rental / (1 + monthly_interest_rate) ** t
        else:
            slc_npv = 0
        
        slc_paydown = sum([slc_securitized_rental for _ in range(t, slc_nper)]) if t < slc_nper else 0
        
        cbr = calculate_cbr(current_full_rental, full_term - t)
        
        inhouse_pv = calculate_pv(inhouse_interest_rate, full_term - t, full_rental)
        
        cumulative_rental += full_rental
        cumulative_rental_with_increase += current_full_rental
        
        slc_npv_values.append(slc_npv)
        slc_paydown_values.append(slc_paydown)
        cbr_values.append(cbr)
        inhouse_pv_values.append(inhouse_pv)
        cash_collection_original_rental_values.append(cumulative_rental)
        cash_collection_escalated_rental_values.append(cumulative_rental_with_increase)
    
    results = pd.DataFrame({
        'Date': dates,
        'SLC NPV': slc_npv_values,
        'SLC Paydown': slc_paydown_values,
        'CBR': cbr_values,
        'Inhouse PV': inhouse_pv_values,
        'Cash Collection (@Original Rental)': cash_collection_original_rental_values,
        'Cash Collection (@Escalated Rental)': cash_collection_escalated_rental_values
    })

    results['SLC NPV'] = results['SLC NPV'].where(results['SLC NPV'] > 0)
    results['SLC Paydown'] = results['SLC Paydown'].where(results['SLC Paydown'] > 0)
    
    return results

def plot_npv_sl_paydown_and_cbr(results):
    plt.figure(figsize=(14, 8))
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

    plt.xlim(left=results['Date'].min())
    plt.ylim(bottom=0)

    first_last_labels = []
    for label in ['SLC NPV', 'SLC Paydown', 'CBR', 'Inhouse PV', 'Cash Collection (@Original Rental)', 'Cash Collection (@Escalated Rental)']:
        first_value = results[label].dropna().iloc[0]
        last_value = results[label].dropna().iloc[-1]
        first_last_labels.append(f'{label} (First: {first_value:.2f}, Last: {last_value:.2f})')

    plt.legend(first_last_labels, loc='upper left')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        full_rental = float(request.form['full_rental'])
        slc_securitized_rental = 0.96 * full_rental
        slc_interest_rate = float(request.form['slc_interest_rate'])
        inhouse_interest_rate = float(request.form['inhouse_interest_rate'])
        slc_nper = int(request.form['slc_nper'])
        full_term = int(request.form['full_term'])
        start_date = request.form['start_date']
        rental_increase_percentage = float(request.form['rental_increase_percentage'])
        rental_increase_month = int(request.form['rental_increase_month'])
        
        results = calculate_npv_sl_paydown_and_cbr(
            slc_securitized_rental,
            slc_interest_rate,
            inhouse_interest_rate,
            slc_nper,
            full_rental,
            full_term,
            start_date,
            rental_increase_percentage,
            rental_increase_month
        )
        
        plot_url = plot_npv_sl_paydown_and_cbr(results)
        
        return render_template('index.html', plot_url=plot_url, tables=[results.to_html(classes='data')], titles=results.columns.values)
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
