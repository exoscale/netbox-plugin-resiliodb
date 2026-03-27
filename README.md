# Netbox ResilioDB Plugin

[![License](https://img.shields.io/badge/License-BSD-blue.svg)](LICENSE)

A custom Netbox module designed for integrating environmental lifecycle analysis (LCA) data into Netbox. It connects to the ResilioDB API to sync environmental impact data for datacenter equipment, allowing your organization to monitor and estimate the lifecycle impact of hardware assets.

This module extends Netbox's functionality by adding custom models to manage LCA-related data and provides both a user interface and an API for managing and syncing the LCA data.

## Overview

The NetBox ResilioDB plugin adds integration between NetBox and ResilioDB to calculate and manage environmental impact data for your devices. Specifically:

- Collecting and managing multicriteria impact data
- Caching ResilioDB responses to optimize performance
- Managing LCA (Life Cycle Assessment) parameters with an inheritance system
- Visualizing impact data directly in NetBox

## Features

- **Multicriteria Impact Data Management**: Track multiple environmental impact indicators
- **Smart Caching**: Avoid redundant ResilioDB requests with an intelligent caching system
- **Hierarchical Parameter System**: Inherit and override LCA parameters at different levels
- **NetBox Integration**: View impact data directly in device details
- **Background Processing**: Asynchronous data collection using NetBox's job system

## Installation

For instructions on installing the plugin to Netbox, see the [official doc](https://netboxlabs.com/docs/netbox/plugins/installation/).

## Initial Setup

### 1. Required Tags

Create the following tags in NetBox (Customization > Tags):

- CPU
- GPU
- HDD
- RAM
- SSD

### 2. Plugin Settings

Configure the plugin settings:

- API URL (e.g., https://db.resilio.tech/)
- API Key
- API Version
- Default Usage Period (hours) - typically 43800.0 (5 years)
- Default Power (watts) - typically 100.0
- Resync on API Version Change

### 3. LCA Type Mappings

Map NetBox Device Roles to ResilioDB LCA Types to define how different devices should be assessed.

### 4. Country Mappings

Configure geography mappings for accurate USE phase calculations:
- Map regions or sites to specific countries
- This affects power consumption impact calculations

## Usage

### Basic Operation

Once configured, the plugin can retrieve impact data for any mapped device. However, for best results:

1. Configure LCA Parameters at either:
   - Device level (most precise)
   - Device Type level (efficient for identical models)

### Server Configuration

For servers, the plugin can automatically build accurate payloads if:

1. Modules are properly installed and tagged:
   - CPU modules (tagged 'CPU')
   - RAM modules (tagged 'RAM')
   - Storage modules (tagged 'SSD' or 'HDD')
   - GPU modules (tagged 'GPU')

2. Module types have appropriate parameters:
   - CPU: Automatically detected for common models
   - RAM: Size detected from module name (e.g., "32GB")
   - SSD: Requires manual parameter setup
   - GPU: Requires manual parameter setup
   - HDD: No special parameters needed

Example server payload:

```json
{
  "cpus": [
    {
      "name": "Xeon Gold 6246R",
      "litho_nm": 14,
      "die_surface_mm2": 126
    }
  ],
  "rams": [
    {"size_gb": 32}
  ],
  "usage": {
    "geography": "Switzerland",
    "power_watt": 400,
    "duration_of_use_hour": 43800.0
  },
  "hdd_disks": {"quantity": 2},
  "rack_unit": 1,
  "ssd_disks": [
    {
      "casing": "casing_M2",
      "size_gb": 1920,
      "technology": "TLC"
    }
  ]
}
```

## Data Quality

ResilioDB provides estimates based on input parameters. The quality of these estimates depends on:

- Precision of input parameters
- Completeness of device configuration
- Accuracy of power consumption data
- Correct geographical mapping

Generic data typically results in higher impact estimates due to safety margins used in LCA practices.

## License

This project is licensed under the BSD License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
