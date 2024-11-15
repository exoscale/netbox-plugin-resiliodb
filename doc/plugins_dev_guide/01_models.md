# Models - NetBox OSS
Database Models
---------------

Creating Models
---------------

If your plugin introduces a new type of object in NetBox, you'll probably want to create a [Django model](https://docs.djangoproject.com/en/stable/topics/db/models/) for it. A model is essentially a Python representation of a database table, with attributes that represent individual columns. Instances of a model (objects) can be created, manipulated, and deleted using [queries](https://docs.djangoproject.com/en/stable/topics/db/queries/). Models must be defined within a file named `models.py`.

Below is an example `models.py` file containing a model with two character (text) fields:

```
from django.db import models

class MyModel(models.Model):
    foo = models.CharField(max_length=50)
    bar = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.foo} {self.bar}'

```


Every model includes by default a numeric primary key. This value is generated automatically by the database, and can be referenced as `pk` or `id`.

Note

Model names should adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/#class-names) standards and be CapWords (no underscores). Using underscores in model names will result in problems with permissions.

Enabling NetBox Features
------------------------

Plugin models can leverage certain NetBox features by inheriting from NetBox's `NetBoxModel` class. This class extends the plugin model to enable features unique to NetBox, including:

*   Bookmarks
*   Change logging
*   Cloning
*   Custom fields
*   Custom links
*   Custom validation
*   Export templates
*   Journaling
*   Tags
*   Webhooks

This class performs two crucial functions:

1.  Apply any fields, methods, and/or attributes necessary to the operation of these features
2.  Register the model with NetBox as utilizing these features

Simply subclass NetBoxModel when defining a model in your plugin:

```
# models.py
from django.db import models
from netbox.models import NetBoxModel

class MyModel(NetBoxModel):
    foo = models.CharField()
    ...

```


### NetBoxModel Properties

#### `docs_url`

This attribute specifies the URL at which the documentation for this model can be reached. By default, it will return `/static/docs/models/<app_label>/<model_name>/`. Plugin models can override this to return a custom URL. For example, you might direct the user to your plugin's documentation hosted on [ReadTheDocs](https://readthedocs.org/).

#### `_netbox_private`

By default, any model introduced by a plugin will appear in the list of available object types e.g. when creating a custom field or certain dashboard widgets. If your model is intended only for "behind the scenes use" and should not be exposed to end users, set `_netbox_private` to True. This will omit it from the list of general-purpose object types.

### Enabling Features Individually

If you prefer instead to enable only a subset of these features for a plugin model, NetBox provides a discrete "mix-in" class for each feature. You can subclass each of these individually when defining your model. (Your model will also need to inherit from Django's built-in `Model` class.)

For example, if we wanted to support only tags and export templates, we would inherit from NetBox's `ExportTemplatesMixin` and `TagsMixin` classes, and from Django's `Model` class. (Inheriting _all_ the available mixins is essentially the same as subclassing `NetBoxModel`.)

```
# models.py
from django.db import models
from netbox.models.features import ExportTemplatesMixin, TagsMixin

class MyModel(ExportTemplatesMixin, TagsMixin, models.Model):
    foo = models.CharField()
    ...

```


Database Migrations
-------------------

Once you have completed defining the model(s) for your plugin, you'll need to create the database schema migrations. A migration file is essentially a set of instructions for manipulating the PostgreSQL database to support your new model, or to alter existing models. Creating migrations can usually be done automatically using Django's `makemigrations` management command. (Ensure that your plugin has been installed and enabled first, otherwise it won't be found.)

Note

NetBox enforces a safeguard around the `makemigrations` command to protect regular users from inadvertently creating erroneous schema migrations. To enable this command for plugin development, set `DEVELOPER=True` in `configuration.py`.

```
$ ./manage.py makemigrations my_plugin 
Migrations for 'my_plugin':
  /home/jstretch/animal_sounds/my_plugin/migrations/0001_initial.py
    - Create model MyModel

```


Next, we can apply the migration to the database with the `migrate` command:

```
$ ./manage.py migrate my_plugin
Operations to perform:
  Apply all migrations: my_plugin
Running migrations:
  Applying my_plugin.0001_initial... OK

```


For more information about database migrations, see the [Django documentation](https://docs.djangoproject.com/en/stable/topics/migrations/).

Feature Mixins Reference
------------------------

Warning

Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `features` module, they are not yet supported for use by plugins.

### `BookmarksMixin (Model)` `django-model`

Enables support for user bookmarks.

#### `bookmarks: GenericRelation` `blank` `django-field` `nullable`

bookmarks

### `ChangeLoggingMixin (Model)` `django-model`

Provides change logging support for a model. Adds the `created` and `last_updated` fields.

#### `created: DateTimeField` `blank` `django-field` `nullable`

created

#### `last_updated: DateTimeField` `blank` `django-field` `nullable`

last updated

#### `serialize_object(self, exclude=None)`

Return a JSON representation of the instance. Models can override this method to replace or extend the default serialization logic provided by the `serialize_object()` utility function.

**Parameters:**


|Name   |Type|Description                                                      |Default|
|-------|----|-----------------------------------------------------------------|-------|
|exclude|    |An iterable of attribute names to omit from the serialized output|None   |


#### `snapshot(self)`

Save a snapshot of the object's current state in preparation for modification. The snapshot is saved as `_prechange_snapshot` on the instance.

#### `to_objectchange(self, action)`

Return a new ObjectChange representing a change made to this object. This will typically be called automatically by ChangeLoggingMiddleware.

### `CloningMixin (Model)` `django-model`

Provides the clone() method used to prepare a copy of existing objects.

#### `clone(self)`

Returns a dictionary of attributes suitable for creating a copy of the current instance. This is used for pre- populating an object creation form in the UI. By default, this method will replicate any fields listed in the model's `clone_fields` list (if defined), but it can be overridden to apply custom logic.

```
class MyModel(NetBoxModel):
    def clone(self):
        attrs = super().clone()
        attrs['extra-value'] = 123
        return attrs

```


### `CustomLinksMixin (Model)` `django-model`

Enables support for custom links.

### `CustomFieldsMixin (Model)` `django-model`

Enables support for custom fields.

#### `custom_field_data: JSONField` `blank` `django-field`

custom field data

#### `cf` `cached` `property` `writable`

Return a dictionary mapping each custom field for this instance to its deserialized value.

```
>>> tenant = Tenant.objects.first()
>>> tenant.cf
{'primary_site': <Site: DM-NYC>, 'cust_id': 'DMI01', 'is_active': True}

```


#### `custom_fields` `cached` `property` `writable`

Return the QuerySet of CustomFields assigned to this model.

```
>>> tenant = Tenant.objects.first()
>>> tenant.custom_fields
<RestrictedQuerySet [<CustomField: Primary site>, <CustomField: Customer ID>, <CustomField: Is active>]>

```


#### `get_custom_fields(self, omit_hidden=False)`

Return a dictionary of custom fields for a single object in the form `{field: value}`.

```
>>> tenant = Tenant.objects.first()
>>> tenant.get_custom_fields()
{<CustomField: Customer ID>: 'CYB01'}

```


**Parameters:**


|Name       |Type|Description                                                  |Default|
|-----------|----|-------------------------------------------------------------|-------|
|omit_hidden|    |If True, custom fields with no UI visibility will be omitted.|False  |


#### `get_custom_fields_by_group(self)`

Return a dictionary of custom field/value mappings organized by group. Hidden fields are omitted.

```
>>> tenant = Tenant.objects.first()
>>> tenant.get_custom_fields_by_group()
{
    '': {<CustomField: Primary site>: <Site: DM-NYC>},
    'Billing': {<CustomField: Customer ID>: 'DMI01', <CustomField: Is active>: True}
}

```


#### `populate_custom_field_defaults(self)`

Apply the default value for each custom field

#### `clean(self)`

Hook for doing any extra model-wide validation after clean() has been called on every field by self.clean\_fields. Any ValidationError raised by this method will not be associated with a particular field; it will have a special-case association with the field defined by NON\_FIELD\_ERRORS.

### `CustomValidationMixin (Model)` `django-model`

Enables user-configured validation rules for models.

#### `clean(self)`

Hook for doing any extra model-wide validation after clean() has been called on every field by self.clean\_fields. Any ValidationError raised by this method will not be associated with a particular field; it will have a special-case association with the field defined by NON\_FIELD\_ERRORS.

### `EventRulesMixin (Model)` `django-model`

Enables support for event rules, which can be used to transmit webhooks or execute scripts automatically.

Note

`EventRulesMixin` was renamed from `WebhooksMixin` in NetBox v3.7.

### `ExportTemplatesMixin (Model)` `django-model`

Enables support for export templates.

### `JobsMixin (Model)` `django-model`

Enables support for job results.

#### `jobs: GenericRelation` `blank` `django-field` `nullable`

jobs

#### `get_latest_jobs(self)`

Return a list of the most recent jobs for this instance.

### `JournalingMixin (Model)` `django-model`

Enables support for object journaling. Adds a generic relation (`journal_entries`) to NetBox's JournalEntry model.

#### `journal_entries: GenericRelation` `blank` `django-field` `nullable`

journal entries

### `TagsMixin (Model)` `django-model`

Enables support for tag assignment. Assigned tags can be managed via the `tags` attribute, which is a `TaggableManager` instance.

#### `tags: TaggableManager` `django-field` `nullable`

Tags: A comma-separated list of tags.

Choice Sets
-----------

For model fields which support the selection of one or more values from a predefined list of choices, NetBox provides the `ChoiceSet` utility class. This can be used in place of a regular choices tuple to provide enhanced functionality, namely dynamic configuration and colorization. (See [Django's documentation](https://docs.djangoproject.com/en/stable/ref/models/fields/#choices) on the `choices` parameter for supported model fields.)

To define choices for a model field, subclass `ChoiceSet` and define a tuple named `CHOICES`, of which each member is a two- or three-element tuple. These elements are:

*   The database value
*   The corresponding human-friendly label
*   The assigned color (optional)

A complete example is provided below.

Note

Authors may find it useful to declare each of the database values as constants on the class, and reference them within `CHOICES` members. This convention allows the values to be referenced from outside the class, however it is not strictly required.

### Dynamic Configuration

Some model field choices in NetBox can be configured by an administrator. For example, the default values for the Site model's `status` field can be replaced or supplemented with custom choices. To enable dynamic configuration for a ChoiceSet subclass, define its `key` as a string specifying the model and field name to which it applies. For example:

```
from utilities.choices import ChoiceSet

class StatusChoices(ChoiceSet):
    key = 'MyModel.status'

```


To extend or replace the default values for this choice set, a NetBox administrator can then reference it under the [`FIELD_CHOICES`](https://netboxlabs.com/docs/netbox/en/stable/configuration/data-validation/#field_choices) configuration parameter. For example, the `status` field on `MyModel` in `my_plugin` would be referenced as:

```
FIELD_CHOICES = {
    'my_plugin.MyModel.status': (
        # Custom choices
    )
}

```


### Example

```
# choices.py
from utilities.choices import ChoiceSet

class StatusChoices(ChoiceSet):
    key = 'MyModel.status'

    STATUS_FOO = 'foo'
    STATUS_BAR = 'bar'
    STATUS_BAZ = 'baz'

    CHOICES = [
        (STATUS_FOO, 'Foo', 'red'),
        (STATUS_BAR, 'Bar', 'green'),
        (STATUS_BAZ, 'Baz', 'blue'),
    ]

```


Warning

For dynamic configuration to work properly, `CHOICES` must be a mutable list, rather than a tuple.

```
# models.py
from django.db import models
from .choices import StatusChoices

class MyModel(models.Model):
    status = models.CharField(
        max_length=50,
        choices=StatusChoices,
        default=StatusChoices.STATUS_FOO
    )

```


