# Forms - NetBox OSS
Form Classes
------------

NetBox provides several base form classes for use by plugins.


|Form Class              |Purpose                             |
|------------------------|------------------------------------|
|NetBoxModelForm         |Create/edit individual objects      |
|NetBoxModelImportForm   |Bulk import objects from CSV data   |
|NetBoxModelBulkEditForm |Edit multiple objects simultaneously|
|NetBoxModelFilterSetForm|Filter objects within a list view   |


### `NetBoxModelForm`

This is the base form for creating and editing NetBox models. It extends Django's ModelForm to add support for tags and custom fields.


|Attribute|Description                                                                        |
|---------|-----------------------------------------------------------------------------------|
|fieldsets|A tuple of FieldSet instances which control how form fields are rendered (optional)|


**Example**

```
from django.utils.translation import gettext_lazy as _
from dcim.models import Site
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from utilities.forms.rendering import FieldSet
from .models import MyModel

class MyModelForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all()
    )
    comments = CommentField()
    fieldsets = (
        FieldSet('name', 'status', 'site', 'tags', name=_('Model Stuff')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = MyModel
        fields = ('name', 'status', 'site', 'comments', 'tags')

```


Comment fields

If your form has a `comments` field, there's no need to list it; this will always appear last on the page.

### `NetBoxModelImportForm`

This form facilitates the bulk import of new objects from CSV, JSON, or YAML data. As with model forms, you'll need to declare a `Meta` subclass specifying the associated `model` and `fields`. NetBox also provides several form fields suitable for import various types of CSV data, listed below.

**Example**

```
from django.utils.translation import gettext_lazy as _
from dcim.models import Site
from netbox.forms import NetBoxModelImportForm
from utilities.forms import CSVModelChoiceField
from .models import MyModel


class MyModelImportForm(NetBoxModelImportForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text=_('Assigned site')
    )

    class Meta:
        model = MyModel
        fields = ('name', 'status', 'site', 'comments')

```


### `NetBoxModelBulkEditForm`

This form facilitates editing multiple objects in bulk. Unlike a model form, this form does not have a child `Meta` class, and must explicitly define each field. All fields in a bulk edit form are generally declared with `required=False`.



* Attribute: model
  * Description: The model of object being edited
* Attribute: fieldsets
  * Description: A tuple of FieldSet instances which control how form fields are rendered (optional)
* Attribute: nullable_fields
  * Description: A tuple of fields which can be nullified (set to empty) using the bulk edit form (optional)


**Example**

```
from django import forms
from django.utils.translation import gettext_lazy as _
from dcim.models import Site
from netbox.forms import NetBoxModelBulkEditForm
from utilities.forms import CommentField, DynamicModelChoiceField
from utilities.forms.rendering import FieldSet
from .models import MyModel, MyModelStatusChoices


class MyModelBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        required=False
    )
    status = forms.ChoiceField(
        choices=MyModelStatusChoices,
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    comments = CommentField()

    model = MyModel
    fieldsets = (
        FieldSet('name', 'status', 'site', name=_('Model Stuff')),
    )
    nullable_fields = ('site', 'comments')

```


### `NetBoxModelFilterSetForm`

This form class is used to render a form expressly for filtering a list of objects. Its fields should correspond to filters defined on the model's filter set.


|Attribute|Description                                                                        |
|---------|-----------------------------------------------------------------------------------|
|model    |The model of object being edited                                                   |
|fieldsets|A tuple of FieldSet instances which control how form fields are rendered (optional)|


**Example**

```
from dcim.models import Site
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import DynamicModelMultipleChoiceField, MultipleChoiceField
from .models import MyModel, MyModelStatusChoices

class MyModelFilterForm(NetBoxModelFilterSetForm):
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    status = MultipleChoiceField(
        choices=MyModelStatusChoices,
        required=False
    )

    model = MyModel

```


General Purpose Fields
----------------------

In addition to the [form fields provided by Django](https://docs.djangoproject.com/en/stable/ref/forms/fields/), NetBox provides several field classes for use within forms to handle specific types of data. These can be imported from `utilities.forms.fields` and are documented below.

### `ColorField (CharField)`

A field which represents a color value in hexadecimal `RRGGBB` format. Utilizes NetBox's `ColorSelect` widget to render choices.

A textarea with support for Markdown rendering. Exists mostly just to add a standard `help_text`.

### `JSONField (JSONField)`

Custom wrapper around Django's built-in JSONField to avoid presenting "null" as the default text.

### `MACAddressField (Field)`

Validates a 48-bit MAC address.

### `SlugField (SlugField)`

Extend Django's built-in SlugField to automatically populate from a field called `name` unless otherwise specified.

**Parameters:**


|Name       |Type|Description                                                     |Default|
|-----------|----|----------------------------------------------------------------|-------|
|slug_source|    |Name of the form field from which the slug value will be derived|'name' |


Dynamic Object Fields
---------------------

### `DynamicModelChoiceField (DynamicModelChoiceMixin, ModelChoiceField)`

Dynamic selection field for a single object, backed by NetBox's REST API.

### `DynamicModelMultipleChoiceField (DynamicModelChoiceMixin, ModelMultipleChoiceField)`

A multiple-choice version of `DynamicModelChoiceField`.

Content Type Fields
-------------------

### `ContentTypeChoiceField (ContentTypeChoiceMixin, ModelChoiceField)`

Selection field for a single content type.

### `ContentTypeMultipleChoiceField (ContentTypeChoiceMixin, ModelMultipleChoiceField)`

Selection field for one or more content types.

CSV Import Fields
-----------------

### `CSVChoiceField (CSVChoicesMixin, ChoiceField)`

A CSV field which accepts a single selection value.

### `CSVMultipleChoiceField (CSVChoicesMixin, MultipleChoiceField)`

A CSV field which accepts multiple selection values.

### `CSVModelChoiceField (ModelChoiceField)`

Extends Django's `ModelChoiceField` to provide additional validation for CSV values.

### `CSVContentTypeField ([CSVModelChoiceField](#utilities.forms.fields.csv.CSVModelChoiceField "utilities.forms.fields.csv.CSVModelChoiceField"))`

CSV field for referencing a single content type, in the form `<app>.<model>`.

### `CSVMultipleContentTypeField (ModelMultipleChoiceField)`

CSV field for referencing one or more content types, in the form `<app>.<model>`.

Form Rendering
--------------

### `FieldSet`

A generic grouping of fields, with an optional name. Each item will be rendered on its own row under the provided heading (name), if any. The following types may be passed as items:

*   Field name (string)
*   InlineFields instance
*   TabbedGroups instance
*   ObjectAttribute instance

**Parameters:**


|Name |Type|Description                                           |Default|
|-----|----|------------------------------------------------------|-------|
|items|    |An iterable of items to be rendered (one per row)     |()     |
|name |    |The fieldset's name, displayed as a heading (optional)|None   |


### `InlineFields`

A set of fields rendered inline (side-by-side) with a shared label.

**Parameters:**


|Name  |Type|Description                                    |Default|
|------|----|-----------------------------------------------|-------|
|fields|    |An iterable of form field names                |()     |
|label |    |The label text to render for the row (optional)|None   |


### `TabbedGroups`

Two or more groups of fields (FieldSets) arranged under tabs among which the user can toggle.

**Parameters:**



* Name: fieldsets
  * Type: 
  * Description: An iterable of FieldSet instances, one per tab. Each FieldSet must have aname assigned, which will be employed as the tab's label.
  * Default: ()


### `ObjectAttribute`

Renders the value for a specific attribute on the form's instance. This may be used to display a read-only value and convey additional context to the user. If the attribute has a `get_absolute_url()` method, it will be rendered as a hyperlink.

**Parameters:**


|Name|Type|Description                              |Default |
|----|----|-----------------------------------------|--------|
|name|    |The name of the attribute to be displayed|required|


