# Tables - NetBox OSS

NetBox employs the [`django-tables2`](https://django-tables2.readthedocs.io/) library for rendering dynamic object tables. These tables display lists of objects, and can be sorted and filtered by various parameters.

NetBoxTable
-----------

To provide additional functionality beyond what is supported by the stock `Table` class in `django-tables2`, NetBox provides the `NetBoxTable` class. This custom table class includes support for:

*   User-configurable column display and ordering
*   Custom field & custom link columns
*   Automatic prefetching of related objects

It also includes several default columns:

*   `pk` - A checkbox for selecting the object associated with each table row (where applicable)
*   `id` - The object's numeric database ID, as a hyperlink to the object's view (hidden by default)
*   `actions` - A dropdown menu presenting object-specific actions available to the user

### Example

```
# tables.py
import django_tables2 as tables
from netbox.tables import NetBoxTable
from .models import MyModel

class MyModelTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    ...

    class Meta(NetBoxTable.Meta):
        model = MyModel
        fields = ('pk', 'id', 'name', ...)
        default_columns = ('pk', 'name', ...)

```


### Table Configuration

The NetBoxTable class features dynamic configuration to allow users to change their column display and ordering preferences. To configure a table for a specific request, simply call its `configure()` method and pass the current HTTPRequest object. For example:

```
table = MyModelTable(data=MyModel.objects.all())
table.configure(request)

```


This will automatically apply any user-specific preferences for the table. (If using a generic view provided by NetBox, table configuration is handled automatically.)

Columns
-------

The table column classes listed below are supported for use in plugins. These classes can be imported from `netbox.tables.columns`.

### `BooleanColumn (Column)`

Custom implementation of BooleanColumn to render a nicely-formatted checkmark or X icon instead of a Unicode character.

### `ChoiceFieldColumn (Column)`

Render a model's static ChoiceField with its value from `get_FOO_display()` as a colored badge. Background color is set by the instance's get\_FOO\_color() method, if defined, or can be overridden by a "color" callable.

### `ColorColumn (Column)`

Display an arbitrary color value, specified in RRGGBB format.

### `ColoredLabelColumn (TemplateColumn)`

Render a related object as a colored label. The related object must have a `color` attribute (specifying an RRGGBB value) and a `get_absolute_url()` method.

### `ContentTypeColumn (Column)`

Display a ContentType instance.

### `ContentTypesColumn (ManyToManyColumn)`

Display a list of ContentType instances.

### `MarkdownColumn (TemplateColumn)`

Render a Markdown string.

### `TagColumn (TemplateColumn)`

Display a list of Tags assigned to the object.

### `TemplateColumn (TemplateColumn)`

Overrides django-tables2's stock TemplateColumn class to render a placeholder symbol if the returned value is an empty string.

#### `__init__(self, export_raw=False, **kwargs)` `special`

**Parameters:**



* Name: export_raw
  * Type: 
  * Description: If true, data export returns the raw field value rather than the rendered template. (Default:        False)
  * Default: False


Extending Core Tables
---------------------

Plugins can register their own custom columns on core tables using the `register_table_column()` utility function. This allows a plugin to attach additional information, such as relationships to its own models, to built-in object lists.

```
import django_tables2
from django.utils.translation import gettext_lazy as _

from dcim.tables import SiteTable
from utilities.tables import register_table_column

mycol = django_tables2.Column(
    verbose_name=_('My Column'),
    accessor=django_tables2.A('description')
)

register_table_column(mycol, 'foo', SiteTable)

```


You'll typically want to define an accessor identifying the desired model field or relationship when defining a custom column. See the [django-tables2 documentation](https://django-tables2.readthedocs.io/) for more information on creating custom columns.

### `register_table_column(column, name, *tables)`

Register a custom column for use on one or more tables.

**Parameters:**


|Name  |Type|Description                    |Default |
|------|----|-------------------------------|--------|
|column|    |The column instance to register|required|
|name  |    |The name of the table column   |required|
|tables|    |One or more table classes      |()      |


