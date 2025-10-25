# Secure Computation Dataset Selection Guide

## Overview

This document explains the purpose and process of selecting datasets during secure computation requests in the Health Data Exchange platform.

## Purpose of Dataset Selection

When creating a secure computation request, selecting the appropriate dataset is a critical step that determines:

1. **What data will be analyzed**: The dataset contains the specific health records or metrics that will be included in the computation.

2. **Which columns are available**: Each dataset has specific data columns (fields) that can be used in the computation.

3. **Data scope and relevance**: Selecting the right dataset ensures that the computation is performed on relevant and appropriate data for the specific analysis.

## How Dataset Selection Works

### In the Secure Computation Wizard

The dataset selection process in the Secure Computation Wizard follows these steps:

1. **Dataset Selection**: Users select from available datasets that have been previously uploaded to the platform.

2. **Column Selection**: Once a dataset is selected, the system displays the available columns (data fields) from that dataset.

3. **Computation Function**: Users choose a computation function (average, sum, count) that will be applied to the selected column.

### Technical Implementation

Behind the scenes, the system:

1. Fetches available datasets from the user's uploads via the API endpoint.

2. Dynamically updates the available columns based on the selected dataset's structure.

3. When the computation is created, it includes references to both the dataset and the specific column to be used.

## Security Considerations

The dataset selection process is designed with privacy and security in mind:

1. **Data Isolation**: Only the specific column selected is used in the computation, not the entire dataset.

2. **Secure Processing**: The actual data values are processed using secure computation methods (standard, homomorphic encryption, or hybrid approaches).

3. **Minimal Data Exposure**: Participating organizations only receive the final computation result, not the raw data from other participants.

## Best Practices

When selecting datasets for secure computation:

1. **Choose Recent Data**: Select the most up-to-date datasets for accurate analysis.

2. **Verify Column Types**: Ensure the selected column contains the appropriate data type for your chosen computation function.

3. **Consider Sample Size**: Be aware of the dataset size to ensure statistical significance in results.

4. **Document Purpose**: Clearly describe the purpose of the computation to help other organizations understand why they're being invited to participate.

## Troubleshooting

If you encounter issues with dataset selection:

1. **Empty Dataset List**: Ensure you have uploaded datasets to the platform.

2. **No Columns Available**: The selected dataset may be empty or improperly formatted.

3. **Computation Errors**: Verify that the selected column contains appropriate numerical data for the chosen computation function.