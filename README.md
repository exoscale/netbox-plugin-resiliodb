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
