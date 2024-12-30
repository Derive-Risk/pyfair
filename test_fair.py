from pyfair import FairModel

# Create a simple FAIR model
model = FairModel(name="Basic Model", n_simulations=10000)

# Set parameters
model.input_data("Loss Event Frequency", mean=0.3, stdev=0.1)
model.input_data("Loss Magnitude", constant=5000000)

# Calculate and display results
model.calculate_all()

# Get results and print summary statistics
results = model.export_results()
print("\nModel Results Summary:")
print("-" * 20)
print(f"Risk Statistics:")
print(f"Mean: ${results['Risk'].mean():,.2f}")
print(f"Median: ${results['Risk'].median():,.2f}")
print(f"95th Percentile: ${results['Risk'].quantile(0.95):,.2f}")
