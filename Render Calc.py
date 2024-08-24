import numpy as np

def calculate_pv(rate, term, rental):
    # Calculate the monthly interest rate
    monthly_rate = rate / 12
    # Calculate Present Value (PV) using the provided formula
    pv = sum([rental / (1 + monthly_rate) ** i for i in range(1, term + 1)])
    return pv

def calculate_cbr(rental, term):
    # Calculate Contract Balance Residual (CBR)
    cbr = rental * term
    return cbr

def calculate_slc_npv(tranche_rate, securitized_term, funded_rental):
    monthly_tranche_rate = tranche_rate / 12
    
    # Correct NPV calculation over the desired range
    # Summing discounted cash flows from 2nd to the 87th term
    npv_sum = sum([funded_rental / (1 + monthly_tranche_rate) ** i for i in range(2, securitized_term + 1)]) 
    
    # Add the first term cash flow
    slc_npv = npv_sum + funded_rental / (1 + monthly_tranche_rate) ** 1
    
    return slc_npv

def main():
    # Assign initial values directly
    rate = 0.0660  # Annual interest rate (e.g., 6.6%)
    term = 87  # Term in months (e.g., 87 months)
    rental = 46.79  # Rental amount (e.g., $46.79)
    
    # New fields
    funded_rental = 0.96 * rental  # 96% of the rental amount
    tranche_rate = 0.0660  # Tranche rate (e.g., 6.6%)
    securitized_term = 87  # Highest securitized term in months (e.g., 87 months)

    # Calculations
    pv = calculate_pv(rate, term, rental)
    cbr = calculate_cbr(rental, term)
    slc_npv = calculate_slc_npv(tranche_rate, securitized_term, funded_rental)

    # Output results
    print(f"Present Value (PV): {pv:.2f}")
    print(f"Contract Balance Residual (CBR): {cbr:.2f}")
    print(f"Funded Rental (96% of Rental): {funded_rental:.2f}")
    print(f"SLC NPV: {slc_npv:.2f}")

if __name__ == "__main__":
    main()
