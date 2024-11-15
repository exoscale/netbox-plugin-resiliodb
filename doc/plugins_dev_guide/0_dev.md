# NetBox Plugin Development

NetBox can be extended to support additional data models and functionality through the use of plugins. A plugin is essentially a self-contained Django app installed alongside NetBox to provide custom functionality. Multiple plugins can be installed in a single NetBox instance, and each plugin can be enabled and configured independently.

## Getting Started

For those new to plugin development, the [NetBox Plugin Tutorial](https://netboxlabs.com/blog/netbox-plugin-development-tutorial/) on GitHub offers an in-depth guide to creating a plugin from scratch. It includes a companion demo plugin repository to facilitate learning at any step.

NetBox Labs also offers a [Plugin Certification Program](https://netboxlabs.com/netbox-plugins/) for developers interested in establishing a co-maintainer relationship. The program aims to ensure ongoing compatibility, maintainability, and commercial supportability of key plugins.

## Plugin Capabilities

Plugins can:

- Create Django models to store data in the database.
- Provide their own views in the web user interface.
- Inject template content and navigation links.
- Extend NetBox's REST and GraphQL APIs.
- Load additional Django apps.
- Add custom request/response middleware.

Each piece of functionality is optional. For example, if your plugin only adds middleware or an API endpoint for existing data, there's no need to define new models.

**Warning:** The NetBox plugins API is necessarily limited in its scope. Any part of the NetBox code base not documented here is not part of the supported plugins API and should not be employed by a plugin. Internal elements of NetBox are subject to change at any time and without warning. Plugin authors are strongly encouraged to develop plugins using only the officially supported components discussed here and those provided by the underlying Django framework to avoid breaking changes in future releases.

## Plugin Structure

Although the specific structure of a plugin is largely left to the discretion of its authors, a typical NetBox plugin might look something like this:

```
project-name/
    plugin_name/
        api/
            __init__.py
            serializers.py
            urls.py
            views.py
        migrations/
            __init__.py
            0001_initial.py
            ...
        templates/
            plugin_name/
                *.html
        __init__.py
        filtersets.py
        graphql.py
        jobs.py
        models.py
        middleware.py
        navigation.py
        signals.py
        tables.py
        template_content.py
        urls.py
        views.py
    pyproject.toml
    README.md
```

The top level is the project root, which can have any name. Within the root, include:

- `pyproject.toml`: Configuration file used to install the plugin package within the Python environment.
- `README.md`: Introduction to your plugin, installation and configuration instructions, and other pertinent information.

The plugin source directory (`plugin_name`) contains all the actual Python code and other resources used by your plugin. Its structure is left to the author's discretion, but it's recommended to follow best practices as outlined in the Django documentation. At a minimum, this directory must contain an `__init__.py` file with an instance of NetBox's `PluginConfig` class.

**Note:** The [Cookiecutter NetBox Plugin](https://github.com/netbox-community/cookiecutter-netbox-plugin) can be used to auto-generate all the needed directories and files for a new plugin.

## PluginConfig

The `PluginConfig` class is a NetBox-specific wrapper around Django's built-in `AppConfig` class. It's used to declare NetBox plugin functionality within a Python package. Each plugin should provide its own subclass, defining its name, metadata, and default and required configuration parameters.

Example:

```python
from netbox.plugins import PluginConfig

class FooBarConfig(PluginConfig):
    name = 'foo_bar'
    verbose_name = 'Foo Bar'
    description = 'An example NetBox plugin'
    version = '0.1'
    author = 'Your Name'
    author_email = 'author@example.com'
    base_url = 'foo-bar'
    required_settings = []
    default_settings = {
        'baz': True
    }
    django_apps = ["foo", "bar", "baz"]

config = FooBarConfig
```

NetBox looks for the `config` variable within a plugin's `__init__.py` to load its configuration. Typically, this will be set to the `PluginConfig` subclass, but you may wish to dynamically generate a `PluginConfig` class based on environment variables or other factors.

### PluginConfig Attributes

- `name`: Raw plugin name; same as the plugin's source directory.
- `verbose_name`: Human-friendly name for the plugin.
- `version`: Current release (semantic versioning is encouraged).
- `description`: Brief description of the plugin's purpose.
- `author`: Name of the plugin's author.
- `author_email`: Author's public email address.
- `base_url`: Base path to use for plugin URLs (optional). If not specified, the project's name will be used.
- `required_settings`: A list of any configuration parameters that must be defined by the user.
- `default_settings`: A dictionary of configuration parameters and their default values.
- `django_apps`: A list of additional Django apps to load alongside the plugin.
- `min_version`: Minimum version of NetBox with which the plugin is compatible.
- `max_version`: Maximum version of NetBox with which the plugin is compatible.
- `middleware`: A list of middleware classes to append after NetBox's built-in middleware.
- `queues`: A list of custom background task queues to create.
- `search_extensions`: The dotted path to the list of search index classes (default: `search.indexes`).
- `data_backends`: The dotted path to the list of data source backend classes (default: `data_backends.backends`).
- `template_extensions`: The dotted path to the list of template extension classes (default: `template_content.template_extensions`).
- `menu_items`: The dotted path to the list of menu items provided by the plugin (default: `navigation.menu_items`).
- `graphql_schema`: The dotted path to the plugin's GraphQL schema class, if any (default: `graphql.schema`).
- `user_preferences`: The dotted path to the dictionary mapping of user preferences 
