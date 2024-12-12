import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Generate sample data for 15 test cases
np.random.seed(42)
test_cases = [f'Case {i+1}' for i in range(15)]
rmse_values = np.random.uniform(0.55, 0.60, 15)
mae_values = np.random.uniform(0.45, 0.50, 15)
r_squared_values = np.random.uniform(0.38, 0.42, 15)

# Create a DataFrame
data = {
    'Test Case': test_cases,
    'RMSE': rmse_values,
    'MAE': mae_values,
    'R-squared': r_squared_values
}
df = pd.DataFrame(data)

# Plot the line chart
plt.figure(figsize=(12, 8))
sns.lineplot(x='Test Case', y='value', hue='variable',
             data=pd.melt(df, ['Test Case']), marker='o')

# Add titles and labels
plt.title('Model Performance Metrics Across Multiple Test Cases')
plt.xlabel('Test Case')
plt.ylabel('Metric Value')
plt.xticks(rotation=45)

# Save the plot as a PNG file
plt.tight_layout()
plt.legend(title='Metric')
plt.savefig('performance_metrics_plot.png')

# Display the plot
plt.show()