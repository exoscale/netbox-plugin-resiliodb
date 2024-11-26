# Technical Specification for NetBox ResilioDB Integration Plugin

## Overview

This plugin integrates NetBox with ResilioDB to calculate and display the environmental impact of devices managed within NetBox. It provides mechanisms for data mapping, parameter customization, data caching, and impact visualization.

---

## Data Models

### 1. **LCAType**

Represents different Life Cycle Assessment (LCA) types corresponding to ResilioDB endpoints.

```python
class LCAType(models.Model):
    name = models.CharField(max_length=100)
    resilio_endpoint = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    default_payload = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
```

- **Fields:**
  - `name`: Name of the LCA type (e.g., "Server", "Desktop").
  - `resilio_endpoint`: Corresponding endpoint in ResilioDB API.
  - `description`: Optional description.
  - `default_payload`: Default JSON payload with parameters for this LCA type.

### 2. **Indicator**

Represents environmental impact indicators used in the assessment.

```python
class Indicator(models.Model):
    code = models.CharField(max_length=10, unique=True)  # e.g., 'GWP', 'ADPe'
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)  # e.g., 'kg CO2 eq'
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.code} ({self.unit})'
```

- **Fields:**
  - `code`: Unique identifier.
  - `name`: Full name of the indicator.
  - `unit`: Unit of measurement.
  - `description`: Explanation of the indicator.

### 3. **DeviceRoleLCATypeMapping**

Maps NetBox Device Roles to LCA Types.

```python
class DeviceRoleLCATypeMapping(models.Model):
    device_role = models.ForeignKey('dcim.DeviceRole', on_delete=models.CASCADE)
    lca_type = models.ForeignKey('LCAType', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.device_role.name} mapped to {self.lca_type.name}'
```

- **Fields:**
  - `device_role`: Reference to NetBox `DeviceRole`.
  - `lca_type`: Reference to `LCAType`.

### 4. **SiteCountryMapping**

Maps NetBox Sites or Regions to countries for geography information.

```python
class SiteCountryMapping(models.Model):
    site = models.ForeignKey('dcim.Site', on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey('dcim.Region', on_delete=models.CASCADE, null=True, blank=True)
    country = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(site__isnull=False, region__isnull=True) |
                    models.Q(site__isnull=True, region__isnull=False)
                ),
                name='site_or_region_must_be_set',
            ),
        ]

    def __str__(self):
        if self.site:
            return f'{self.site.name} mapped to {self.country}'
        else:
            return f'{self.region.name} mapped to {self.country}'
```

- **Fields:**
  - `site`: Reference to NetBox `Site` (nullable).
  - `region`: Reference to NetBox `Region` (nullable).
  - `country`: Country name or code.

### 5. **LCAParams**

Stores LCA parameters at the DeviceType or Device level.

```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class LCAParams(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    parameters = models.JSONField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id')

    def __str__(self):
        return f'LCA Params for {self.content_object}'
```

- **Fields:**
  - `content_type`, `object_id`, `content_object`: Generic foreign key to either a `DeviceType` or a `Device`.
  - `parameters`: JSON storing LCA parameters.
  - `updated_at`: Timestamp of last update.

### 6. **LCACache**

Caches request payloads to avoid redundant API calls.

```python
class LCACache(models.Model):
    hash = models.CharField(max_length=64, unique=True)
    request_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hash
```

- **Fields:**
  - `hash`: SHA-256 hash of the request payload.
  - `request_payload`: The request payload sent to ResilioDB.
  - `created_at`: Timestamp when the cache entry was created.

### 7. **LCAImpactData**

Stores environmental impact data for devices.

```python
class LCAImpactData(models.Model):
    device = models.OneToOneField('dcim.Device', on_delete=models.CASCADE)
    calculated_at = models.DateTimeField(auto_now=True)
    cache_entry = models.ForeignKey('LCACache', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Impact Data for {self.device.name}'
```

- **Fields:**
  - `device`: Reference to NetBox `Device`.
  - `calculated_at`: Timestamp of the last calculation.
  - `cache_entry`: Reference to `LCACache` entry used for this calculation.

### 8. **LCAImpactIndicatorValue**

Stores indicator values per device, including per life cycle step.

```python
class LCAImpactIndicatorValue(models.Model):
    impact_data = models.ForeignKey('LCAImpactData', on_delete=models.CASCADE, related_name='indicator_values')
    indicator = models.ForeignKey('Indicator', on_delete=models.CASCADE)
    total_value = models.FloatField()

    # Values per life cycle step
    BLD = models.FloatField(null=True, blank=True)
    DIS = models.FloatField(null=True, blank=True)
    USE = models.FloatField(null=True, blank=True)
    EOL = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.indicator.code} for {self.impact_data.device.name}'
```

- **Fields:**
  - `impact_data`: Reference to `LCAImpactData`.
  - `indicator`: Reference to `Indicator`.
  - `total_value`: Total indicator value.
  - `BLD`, `DIS`, `USE`, `EOL`: Values per life cycle step.

### 9. **PluginSettings**

Stores global settings for the plugin.

```python
class PluginSettings(models.Model):
    api_url = models.URLField()
    api_key = models.CharField(max_length=255)
    api_version = models.CharField(max_length=20)
    default_usage_period_hours = models.FloatField(default=43800)  # e.g., 5 years × 365 days × 24 hours
    default_power_watts = models.FloatField(default=100)
    resync_on_api_version_change = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Plugin Settings'
        verbose_name_plural = 'Plugin Settings'

    def __str__(self):
        return 'ResilioDB Plugin Settings'
```

- **Fields:**
  - `api_url`: ResilioDB API base URL.
  - `api_key`: API key for authentication.
  - `api_version`: Version of the ResilioDB API to use.
  - `default_usage_period_hours`: Default usage period in hours.
  - `default_power_watts`: Default power consumption in watts.
  - `resync_on_api_version_change`: Flag to trigger resync when API version changes.

---

## Features

### 1. **Background Job for ResilioDB Sync**

#### Description

A background job that can be triggered to synchronize environmental impact data for devices with ResilioDB.

#### Functionality

- **Default Behavior:**
  - Synchronizes only devices that do not have existing impact data.
- **Force Resync:**
  - Option to force resynchronization for all devices.
- **API Version Handling:**
  - If the API version changes and `resync_on_api_version_change` is `True`, the job will resynchronize all devices.

#### Implementation Details

- **Task Queue:**
  - Use NetBox's built-in job scheduling or integrate with a task queue like Celery.
- **Job Steps:**
  1. **Identify Devices to Sync:**
     - Fetch devices based on criteria (e.g., missing impact data or force resync).
  2. **Build Payloads:**
     - For each device, merge LCA parameters and construct the request payload.
  3. **Cache Check:**
     - Compute hash of the payload and check if it exists in `LCACache`.
  4. **API Request:**
     - If cache miss, send request to ResilioDB and store response.
  5. **Parse Response:**
     - Extract indicator values and life cycle step data.
  6. **Store Impact Data:**
     - Update `LCAImpactData` and `LCAImpactIndicatorValue` for the device.

- **Logging and Error Handling:**
  - Log successes and failures.
  - Handle exceptions and retry logic if necessary.

### 2. **Plugin Pages and Views**

#### a. **LCAType Management**

- **Functionality:**
  - List, create, edit, and delete `LCAType` entries.
  - Edit `default_payload` for each LCA type.

- **Views:**
  - **List View:** Display all LCA types.
  - **Detail View:** Show details of an LCA type.
  - **Create/Edit View:** Form to create or edit LCA types, including `default_payload`.

#### b. **Indicator Management**

- **Functionality:**
  - List, create, edit, and delete `Indicator` entries.

- **Views:**
  - **List View:** Display all indicators.
  - **Detail View:** Show details of an indicator.
  - **Create/Edit View:** Form to create or edit indicators.

#### c. **SiteCountryMapping Management**

- **Functionality:**
  - Map sites or regions to countries.

- **Views:**
  - **List View:** Display all mappings.
  - **Create/Edit View:** Form to create or edit mappings.

#### d. **DeviceRoleLCATypeMapping Management**

- **Functionality:**
  - Map device roles to LCA types.

- **Views:**
  - **List View:** Display all mappings.
  - **Create/Edit View:** Form to create or edit mappings.

### 3. **LCA Parameters Editing**

#### a. **Device Types**

- **Functionality:**
  - Edit `LCAParams` for device types.

- **Implementation:**
  - Add a custom tab or section in the Device Type detail view.
  - Provide a form pre-populated with `default_payload` from associated `LCAType`.
  - Allow users to modify and save parameters.

#### b. **Devices**

- **Functionality:**
  - Edit `LCAParams` for individual devices.

- **Implementation:**
  - Add a custom tab or section in the Device detail view.
  - Provide a form pre-populated with parameters from the device type or `default_payload`.
  - Device-level parameters override device type parameters.

### 4. **Environmental Impact Widget on Device Page**

- **Functionality:**
  - Display a widget on the device detail page showing a summary of environmental impact.

- **Content:**
  - **GWP Total Value:** Display total Global Warming Potential.
  - **Life Cycle Steps Chart:** Visual representation (e.g., pie chart) of GWP distribution across life cycle steps (`BLD`, `DIS`, `USE`, `EOL`).
  - **Indicators Grid:** Table showing values of all indicators.

- **Implementation:**
  - Use JavaScript charting libraries (e.g., Chart.js) for visualizations.
  - Fetch data from `LCAImpactIndicatorValue` model.

### 5. **Plugin Actions**

#### a. **Clear Cache**

- **Functionality:**
  - Provide an option to clear the `LCACache`.

- **Implementation:**
  - Add a button or action in the plugin settings page.
  - Confirm action before clearing cache.
  - Delete all entries from `LCACache`.

#### b. **Download Devices Impact Data as CSV**

- **Functionality:**
  - Export environmental impact data for all devices into a CSV file.

- **Implementation:**
  - Provide a download button in the plugin interface.
  - Generate CSV with the following columns:
    - `Device Name`
    - `Device Type`
    - `Site`
    - `GWP Total`
    - `GWP BLD`
    - `GWP DIS`
    - `GWP USE`
    - `GWP EOL`
    - Additional indicators as columns.
  - Handle large datasets efficiently.

---

## Additional Details

### Data Handling

- **LCA Parameters Merging:**
  - When constructing request payloads, parameters are merged in the following order of precedence:
    1. Device-level `LCAParams`.
    2. DeviceType-level `LCAParams`.
    3. `default_payload` from `LCAType`.
  - This allows for granular control and sensible defaults.

- **Caching Mechanism:**
  - Request payloads are hashed using SHA-256.
  - Before making an API call, the plugin checks if the hash exists in `LCACache`.
  - If a cache entry exists, the plugin uses the existing data.
  - This reduces unnecessary API calls and improves performance.

### API Interaction

- **Authentication:**
  - Use `api_key` from `PluginSettings` for authenticating with ResilioDB.

- **API Version:**
  - Use `api_version` from `PluginSettings` in API calls.
  - If the API version changes, and `resync_on_api_version_change` is `True`, a resynchronization is triggered.

- **Error Handling:**
  - Handle HTTP errors, timeouts, and authentication failures gracefully.
  - Log errors for troubleshooting.

### User Interface Components

- **Forms:**
  - Use Django forms to handle creation and editing of models.
  - For JSON fields (`parameters`, `default_payload`), use a JSON editor widget to enhance usability.

- **Templates:**
  - Use NetBox's template inheritance to integrate plugin pages seamlessly.
  - Ensure that UI components are consistent with NetBox's design guidelines.

- **Navigation:**
  - Add plugin menu items for accessing management pages.


---

## Development Notes

- **Compatibility:**
  - Ensure the plugin is compatible with the target version of NetBox.
  - Test with different versions if necessary.

- **Testing:**
  - Write unit tests for models, views, and background tasks.
  - Test API interactions with ResilioDB, including edge cases.

- **Documentation:**
  - Provide clear documentation on how to install and configure the plugin.
  - Include instructions for setting up API credentials and default settings.

- **Internationalization:**
  - Consider internationalization (i18n) support for UI components.

---

## Summary

This technical specification outlines the data models and features required to develop a NetBox plugin that integrates with ResilioDB for environmental impact assessments. The plugin provides mechanisms for data mapping, parameter customization, data caching, impact data visualization, and administrative actions.

By following this specification, a developer should have all the necessary information to implement the plugin effectively, ensuring it meets the outlined requirements and integrates seamlessly with NetBox and ResilioDB.
