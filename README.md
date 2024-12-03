## Overview

`netbox-resiliodb` is a custom Netbox module designed for integrating environmental lifecycle analysis (LCA) data into Netbox’s device management system. It connects to the Resilio DB API to sync environmental impact data for datacenter equipment, allowing Exoscale to monitor and estimate the lifecycle impact of hardware assets. Additionally, it enables data export for cloud impact assessment.

This module extends Netbox’s functionality by adding custom models to manage LCA-related data and provides both a user interface and an API for managing and syncing the LCA data.

---

## Features

1. **Custom Models for LCA Data:**
   - **LCA Fields:** Adds the following custom fields to `device_type` and `module_type`:
     - `lca_type` (Text): Categorizes the LCA type for a device or module.
     - `lca_spec` (JSON): Stores detailed LCA specifications.
     - `lca_pool` (Text): Groups devices into LCA pools for analysis.
     - `lca_footprint` (JSON): Holds the environmental impact data fetched from Resilio DB.

2. **User Interface:**
   - A dedicated UI within Netbox for managing LCA data, displaying a list of devices (including both devices and module types) and their associated LCA values.
   - Editable fields for LCA data directly from the UI, with real-time updates and sync functionality.

3. **Sync with Resilio DB:**
   - A sync action that interacts with the Resilio DB API to fetch environmental footprint data for devices.
   - Maintains versioned data from Resilio DB, storing different versions of the `lca_footprint` field so that historic LCA data is retained for each version.

4. **API Integration:**
   - A matching API endpoint for external systems to interact with and manage LCA data, facilitating integration with automation tools.

5. **LCA Data Export (CloudAssess Integration):**
   - Generates a CSV file with LCA footprint data for selected devices, in a format that can be consumed by the CloudAssess tool.
   - Export options include downloading the CSV directly or uploading it to an S3 bucket for cloud storage integration.

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/exoscale/netbox-resiliodb.git
   ```

2. **Install the Module:**
   Navigate to the `netbox` environment and install the module by adding it to your `local_requirements.txt` or running:
   ```bash
   pip install /path/to/netbox-resiliodb
   ```

3. **Update Netbox Configuration:**
   - Add `netbox_resiliodb` to the `PLUGINS` setting in `configuration.py`:
     ```python
     PLUGINS = ['netbox_resiliodb']
     ```

4. **Run Migrations:**
   Run the following command to create the necessary database tables:
   ```bash
   python3 manage.py migrate netbox_resiliodb
   ```

5. **Restart Netbox:**
   Restart the Netbox service to apply changes.

---

## Usage

### User Interface

- Navigate to the `Netbox-ResilioDB` tab in the Netbox UI to view the list of `device_type` and `module_type` entries and their associated LCA data.
- The list displays columns for `lca_type`, `lca_spec`, `lca_pool`, and `lca_footprint`.
- You can edit each entry's LCA data directly from the UI or trigger a sync with Resilio DB to update footprint data.

### Syncing with Resilio DB

- To fetch environmental data from Resilio DB, select one or more devices from the UI and click the `Sync` button.
- This will query Resilio DB and update the LCA footprint values.
- The module stores different versions of the LCA footprint data for historical analysis.

### API Access

- The module exposes a custom API endpoint for interacting with LCA data.
- You can retrieve, edit, or sync the data programmatically through the API.

### Exporting LCA Data

- To export the LCA footprint data in a CSV format, use the export feature in the UI.
- You can either download the CSV file directly or configure the module to upload it to an S3 bucket.
- The CSV is formatted for compatibility with the CloudAssess tool, simplifying cloud environmental impact assessments.

---

## Configuration

The following options can be configured in the Netbox `configuration.py` file:

- **S3 Configuration:**
   If you plan to use the S3 upload feature for exporting CSV data, add your S3 credentials:
   ```python
   S3_BUCKET = 'your-s3-bucket-name'
   S3_ACCESS_KEY = 'your-access-key'
   S3_SECRET_KEY = 'your-secret-key'
   ```

---

## Cache Management

The module implements a persistent cache system within the Netbox database to avoid redundant queries to Resilio DB. Once a device type's footprint has been fetched from the API, it will be cached, and subsequent requests will retrieve it from the local cache.

To clear the cache manually, you can run the following management command:
```bash
python3 manage.py clear_resilio_cache
```

---

## License

This project is licensed under the MIT License.

---

## Contributing

Contributions to `netbox-resiliodb` are welcome! Please submit issues or pull requests on the [GitHub repository](https://github.com/exoscale/netbox-resiliodb).

---

This readme provides a comprehensive overview of how to install, configure, and use the `netbox-resiliodb` module, along with instructions for syncing data with Resilio DB and exporting it for cloud assessment tools.
# NetBox ResilioDB Plugin

A NetBox plugin for managing and collecting environmental impact data through ResilioDB integration. This plugin makes it easy to assess and track the environmental footprint of your infrastructure within NetBox.

[![License](https://img.shields.io/badge/License-BSD-blue.svg)](LICENSE)

## Overview

The NetBox ResilioDB plugin enables seamless integration between NetBox and ResilioDB to calculate and manage environmental impact data for your devices. It provides a robust framework for:

- Collecting and managing multicriteria impact data
- Caching ResilioDB responses to optimize performance
- Managing LCA (Life Cycle Assessment) parameters with an inheritance system
- Visualizing impact data directly in NetBox
- Exporting data in CloudAssess-compatible format

## Features

- **Multicriteria Impact Data Management**: Track multiple environmental impact indicators
- **Smart Caching**: Avoid redundant ResilioDB requests with an intelligent caching system
- **Hierarchical Parameter System**: Inherit and override LCA parameters at different levels
- **NetBox Integration**: View impact data directly in device details
- **CloudAssess Export**: Generate CSV exports compatible with [CloudAssess](https://cloudassess.org)
- **Background Processing**: Asynchronous data collection using NetBox's job system

## Installation

1. Install the package:
```bash
pip install netbox-resiliodb
```

2. Add the plugin to `PLUGINS` in `configuration.py`:
```python
PLUGINS = [
    'netbox_resiliodb'
]
```

3. Run migrations:
```bash
python netbox/manage.py migrate netbox_resiliodb
```

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

### 5. Pool Mappings (Optional)

For CloudAssess integration:
- Map NetBox Platforms to CloudAssess Pools
- Associate Device Roles with each mapping

## Background Worker

The plugin requires NetBox's background worker for ResilioDB interactions:

```bash
./manage.py rqworker high default low
```

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
