# Views - NetBox OSS
Writing Views
-------------

If your plugin will provide its own page or pages within the NetBox web UI, you'll need to define views. A view is a piece of business logic which performs an action and/or renders a page when a request is made to a particular URL. HTML content is rendered using a [template](https://netboxlabs.com/docs/netbox/en/stable/plugins/development/templates/). Views are typically defined in `views.py`, and URL patterns in `urls.py`.

As an example, let's write a view which displays a random animal and the sound it makes. We'll use Django's generic `View` class to minimize the amount of boilerplate code needed.

```
from django.shortcuts import render
from django.views.generic import View
from .models import Animal

class RandomAnimalView(View):
    """
    Display a randomly-selected animal.
    """
    def get(self, request):
        animal = Animal.objects.order_by('?').first()
        return render(request, 'netbox_animal_sounds/animal.html', {
            'animal': animal,
        })

```


This view retrieves a random Animal instance from the database and passes it as a context variable when rendering a template named `animal.html`. HTTP `GET` requests are handled by the view's `get()` method, and `POST` requests are handled by its `post()` method.

Our example above is extremely simple, but views can do just about anything. They are generally where the core of your plugin's functionality will reside. Views also are not limited to returning HTML content: A view could return a CSV file or image, for instance. For more information on views, see the [Django documentation](https://docs.djangoproject.com/en/stable/topics/class-based-views/).

### URL Registration

To make the view accessible to users, we need to register a URL for it. We do this in `urls.py` by defining a `urlpatterns` variable containing a list of paths.

```
from django.urls import path
from . import views

urlpatterns = [
    path('random/', views.RandomAnimalView.as_view(), name='random_animal'),
]

```


A URL pattern has three components:

*   `route` - The unique portion of the URL dedicated to this view
*   `view` - The view itself
*   `name` - A short name used to identify the URL path internally

This makes our view accessible at the URL `/plugins/animal-sounds/random/`. (Remember, our `AnimalSoundsConfig` class sets our plugin's base URL to `animal-sounds`.) Viewing this URL should show the base NetBox template with our custom content inside it.

### View Classes

NetBox provides several generic view classes (documented below) to facilitate common operations, such as creating, viewing, modifying, and deleting objects. Plugins can subclass these views for their own use.


|View Class        |Description                                           |
|------------------|------------------------------------------------------|
|ObjectView        |View a single object                                  |
|ObjectEditView    |Create or edit a single object                        |
|ObjectDeleteView  |Delete a single object                                |
|ObjectChildrenView|A list of child objects within the context of a parent|
|ObjectListView    |View a list of objects                                |
|BulkImportView    |Import a set of new objects                           |
|BulkEditView      |Edit multiple objects                                 |
|BulkDeleteView    |Delete multiple objects                               |


Warning

Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `views.generic` module, they are not yet supported for use by plugins.

#### Example Usage

```
# views.py
from netbox.views.generic import ObjectEditView
from .models import Thing

class ThingEditView(ObjectEditView):
    queryset = Thing.objects.all()
    template_name = 'myplugin/thing.html'
    ...

```


Object Views
------------

Below are the class definitions for NetBox's object views. These views handle CRUD actions for individual objects. The view, add/edit, and delete views each inherit from `BaseObjectView`, which is not intended to be used directly.

### `BaseObjectView (ObjectPermissionRequiredMixin, View)`

Base class for generic views which display or manipulate a single object.

**Attributes:**


|Name         |Type|Description                                             |
|-------------|----|--------------------------------------------------------|
|queryset     |    |Django QuerySet from which the object(s) will be fetched|
|template_name|    |The name of the HTML template file to render            |


#### `get_queryset(self, request)`

Return the base queryset for the view. By default, this returns `self.queryset.all()`.

**Parameters:**


|Name   |Type|Description        |Default |
|-------|----|-------------------|--------|
|request|    |The current request|required|


#### `get_object(self, **kwargs)`

Return the object being viewed or modified. The object is identified by an arbitrary set of keyword arguments gleaned from the URL, which are passed to `get_object_or_404()`. (Typically, only a primary key is needed.)

If no matching object is found, return a 404 response.

Return any additional context data to include when rendering the template.

**Parameters:**


|Name    |Type|Description            |Default |
|--------|----|-----------------------|--------|
|request |    |The current request    |required|
|instance|    |The object being viewed|required|


### `ObjectView ([BaseObjectView](#netbox.views.generic.base.BaseObjectView "netbox.views.generic.base.BaseObjectView"))`

Retrieve a single object for display.

Note: If `template_name` is not specified, it will be determined automatically based on the queryset model.

**Attributes:**


|Name|Type|Description                    |
|----|----|-------------------------------|
|tab |    |A ViewTab instance for the view|


#### `get_template_name(self)`

Return self.template\_name if defined. Otherwise, dynamically resolve the template name using the queryset model's `app_label` and `model_name`.

### `ObjectEditView (GetReturnURLMixin, [BaseObjectView](#netbox.views.generic.base.BaseObjectView "netbox.views.generic.base.BaseObjectView"))`

Create or edit a single object.

**Attributes:**


|Name|Type|Description                               |
|----|----|------------------------------------------|
|form|    |The form used to create or edit the object|


#### `alter_object(self, obj, request, url_args, url_kwargs)`

Provides a hook for views to modify an object before it is processed. For example, a parent object can be defined given some parameter from the request URL.

**Parameters:**


|Name      |Type|Description            |Default |
|----------|----|-----------------------|--------|
|obj       |    |The object being edited|required|
|request   |    |The current request    |required|
|url_args  |    |URL path args          |required|
|url_kwargs|    |URL path kwargs        |required|


### `ObjectDeleteView (GetReturnURLMixin, [BaseObjectView](#netbox.views.generic.base.BaseObjectView "netbox.views.generic.base.BaseObjectView"))`

Delete a single object.

### `ObjectChildrenView ([ObjectView](#netbox.views.generic.object_views.ObjectView "netbox.views.generic.object_views.ObjectView"), ActionsMixin, TableMixin)`

Display a table of child objects associated with the parent object. For example, NetBox uses this to display the set of child IP addresses within a parent prefix.

**Attributes:**



* Name: child_model
  * Type: 
  * Description: The model class which represents the child objects
* Name: table
  * Type: 
  * Description: The django-tables2 Table class used to render the child objects list
* Name: filterset
  * Type: 
  * Description: A django-filter FilterSet that is applied to the queryset
* Name: filterset_form
  * Type: 
  * Description: The form class used to render filter options
* Name: actions
  * Type: 
  * Description: A mapping of supported actions to their required permissions. When adding custom actions, bulkaction names must be prefixed with bulk_. (See ActionsMixin.)


#### `get_children(self, request, parent)`

Return a QuerySet of child objects.

**Parameters:**


|Name   |Type|Description        |Default |
|-------|----|-------------------|--------|
|request|    |The current request|required|
|parent |    |The parent object  |required|


#### `prep_table_data(self, request, queryset, parent)`

Provides a hook for subclassed views to modify data before initializing the table.

**Parameters:**


|Name    |Type|Description                           |Default |
|--------|----|--------------------------------------|--------|
|request |    |The current request                   |required|
|queryset|    |The filtered queryset of child objects|required|
|parent  |    |The parent object                     |required|


Multi-Object Views
------------------

Below are the class definitions for NetBox's multi-object views. These views handle simultaneous actions for sets objects. The list, import, edit, and delete views each inherit from `BaseMultiObjectView`, which is not intended to be used directly.

### `BaseMultiObjectView (ObjectPermissionRequiredMixin, View)`

Base class for generic views which display or manipulate multiple objects.

**Attributes:**


|Name         |Type|Description                                                   |
|-------------|----|--------------------------------------------------------------|
|queryset     |    |Django QuerySet from which the object(s) will be fetched      |
|table        |    |The django-tables2 Table class used to render the objects list|
|template_name|    |The name of the HTML template file to render                  |


#### `get_queryset(self, request)`

Return the base queryset for the view. By default, this returns `self.queryset.all()`.

**Parameters:**


|Name   |Type|Description        |Default |
|-------|----|-------------------|--------|
|request|    |The current request|required|


Return any additional context data to include when rendering the template.

**Parameters:**


|Name   |Type|Description        |Default |
|-------|----|-------------------|--------|
|request|    |The current request|required|


### `ObjectListView ([BaseMultiObjectView](#netbox.views.generic.base.BaseMultiObjectView "netbox.views.generic.base.BaseMultiObjectView"), ActionsMixin, TableMixin)`

Display multiple objects, all the same type, as a table.

**Attributes:**



* Name: filterset
  * Type: 
  * Description: A django-filter FilterSet that is applied to the queryset
* Name: filterset_form
  * Type: 
  * Description: The form class used to render filter options
* Name: actions
  * Type: 
  * Description: A mapping of supported actions to their required permissions. When adding custom actions, bulkaction names must be prefixed with bulk_. (See ActionsMixin.)


#### `export_table(self, table, columns=None, filename=None)`

Export all table data in CSV format.

**Parameters:**



* Name: table
  * Type: 
  * Description: The Table instance to export
  * Default: required
* Name: columns
  * Type: 
  * Description: A list of specific columns to include. If None, all columns will be exported.
  * Default: None
* Name: filename
  * Type: 
  * Description: The name of the file attachment sent to the client. If None, will be determined automaticallyfrom the queryset model name.
  * Default: None


#### `export_template(self, template, request)`

Render an ExportTemplate using the current queryset.

**Parameters:**


|Name    |Type|Description            |Default |
|--------|----|-----------------------|--------|
|template|    |ExportTemplate instance|required|
|request |    |The current request    |required|


### `BulkImportView (GetReturnURLMixin, [BaseMultiObjectView](#netbox.views.generic.base.BaseMultiObjectView "netbox.views.generic.base.BaseMultiObjectView"))`

Import objects in bulk (CSV format).

**Attributes:**


|Name      |Type|Description                                 |
|----------|----|--------------------------------------------|
|model_form|    |The form used to create each imported object|


#### `save_object(self, object_form, request)`

Provide a hook to modify the object immediately before saving it (e.g. to encrypt secret data).

**Parameters:**


|Name       |Type|Description            |Default |
|-----------|----|-----------------------|--------|
|object_form|    |The model form instance|required|
|request    |    |The current request    |required|


### `BulkEditView (GetReturnURLMixin, [BaseMultiObjectView](#netbox.views.generic.base.BaseMultiObjectView "netbox.views.generic.base.BaseMultiObjectView"))`

Edit objects in bulk.

**Attributes:**


|Name     |Type|Description                                 |
|---------|----|--------------------------------------------|
|filterset|    |FilterSet to apply when deleting by QuerySet|
|form     |    |The form class used to edit objects in bulk |


### `BulkDeleteView (GetReturnURLMixin, [BaseMultiObjectView](#netbox.views.generic.base.BaseMultiObjectView "netbox.views.generic.base.BaseMultiObjectView"))`

Delete objects in bulk.

**Attributes:**


|Name     |Type|Description                                    |
|---------|----|-----------------------------------------------|
|filterset|    |FilterSet to apply when deleting by QuerySet   |
|table    |    |The table used to display devices being deleted|


#### `get_form(self)`

Provide a standard bulk delete form if none has been specified for the view

Feature Views
-------------

These views are provided to enable or enhance certain NetBox model features, such as change logging or journaling. These typically do not need to be subclassed: They can be used directly e.g. in a URL path.

### `ObjectChangeLogView (ConditionalLoginRequiredMixin, View)`

Present a history of changes made to a particular object. The model class must be passed as a keyword argument when referencing this view in a URL path. For example:

```
path('sites/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='site_changelog', kwargs={'model': Site}),

```


**Attributes:**



* Name: base_template
  * Type: 
  * Description: The name of the template to extend. If not provided, "{app}/{model}.html" will be used.


### `ObjectJournalView (ConditionalLoginRequiredMixin, View)`

Show all journal entries for an object. The model class must be passed as a keyword argument when referencing this view in a URL path. For example:

```
path('sites/<int:pk>/journal/', ObjectJournalView.as_view(), name='site_journal', kwargs={'model': Site}),

```


**Attributes:**



* Name: base_template
  * Type: 
  * Description: The name of the template to extend. If not provided, "{app}/{model}.html" will be used.


Extending Core Views
--------------------

### Additional Tabs

Plugins can "attach" a custom view to a core NetBox model by registering it with `register_model_view()`. To include a tab for this view within the NetBox UI, declare a TabView instance named `tab`, and add it to the template context dict:

```
from dcim.models import Site
from myplugin.models import Stuff
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

@register_model_view(Site, name='myview', path='some-other-stuff')
class MyView(generic.ObjectView):
    ...
    tab = ViewTab(
        label='Other Stuff',
        badge=lambda obj: Stuff.objects.filter(site=obj).count(),
        permission='myplugin.view_stuff'
    )

    def get(self, request, pk):
        ...
        return render(
            request,
            "myplugin/mytabview.html",
            context={
                "tab": self.tab,
            },
        )

```


### `register_model_view(model, name='', path=None, kwargs=None)`

This decorator can be used to "attach" a view to any model in NetBox. This is typically used to inject additional tabs within a model's detail view. For example, to add a custom tab to NetBox's dcim.Site model:

```
@register_model_view(Site, 'myview', path='my-custom-view')
class MyView(ObjectView):
    ...

```


This will automatically create a URL path for MyView at `/dcim/sites/<id>/my-custom-view/` which can be resolved using the view name \`dcim:site\_myview'.

**Parameters:**



* Name: model
  * Type: 
  * Description: The Django model class with which this view will be associated.
  * Default: required
* Name: name
  * Type: 
  * Description: The string used to form the view's name for URL resolution (e.g. via reverse()). This will be appendedto the name of the base view for the model using an underscore. If blank, the model name will be used.
  * Default: ''
* Name: path
  * Type: 
  * Description: The URL path by which the view can be reached (optional). If not provided, name will be used.
  * Default: None
* Name: kwargs
  * Type: 
  * Description: A dictionary of keyword arguments for the view to include when registering its URL path (optional).
  * Default: None


### `ViewTab`

ViewTabs are used for navigation among multiple object-specific views, such as the changelog or journal for a particular object.

**Parameters:**



* Name: label
  * Type: 
  * Description: Human-friendly text
  * Default: required
* Name: badge
  * Type: 
  * Description: A static value or callable to display alongside the label (optional). If a callable is used, it mustaccept a single argument representing the object being viewed.
  * Default: None
* Name: weight
  * Type: 
  * Description: Numeric weight to influence ordering among other tabs (default: 1000)
  * Default: 1000
* Name: permission
  * Type: 
  * Description: The permission required to display the tab (optional).
  * Default: None
* Name: hide_if_empty
  * Type: 
  * Description: If true, the tab will be displayed only if its badge has a meaningful value. (Tabs without abadge are always displayed.)
  * Default: False


#### `render(self, instance)`

Return the attributes needed to render a tab in HTML.

### Extra Template Content

Plugins can inject custom content into certain areas of core NetBox views. This is accomplished by subclassing `PluginTemplateExtension`, optionally designating one or more particular NetBox models, and defining the desired method(s) to render custom content. Five methods are available:


|Method           |View       |Description                                        |
|-----------------|-----------|---------------------------------------------------|
|navbar()         |All        |Inject content inside the top navigation bar       |
|list_buttons()   |List view  |Add buttons to the top of the page                 |
|buttons()        |Object view|Add buttons to the top of the page                 |
|alerts()         |Object view|Inject content at the top of the page              |
|left_page()      |Object view|Inject content on the left side of the page        |
|right_page()     |Object view|Inject content on the right side of the page       |
|full_width_page()|Object view|Inject content across the entire bottom of the page|


The `navbar()` and `alerts()` methods were introduced in NetBox v4.1.

Additionally, a `render()` method is available for convenience. This method accepts the name of a template to render, and any additional context data you want to pass. Its use is optional, however.

To control where the custom content is injected, plugin authors can specify an iterable of models by overriding the `models` attribute on the subclass. Extensions which do not specify a set of models will be invoked on every view, where supported.

When a PluginTemplateExtension is instantiated, context data is assigned to `self.context`. Available data includes:

*   `object` - The object being viewed (object views only)
*   `model` - The model of the list view (list views only)
*   `request` - The current request
*   `settings` - Global NetBox settings
*   `config` - Plugin-specific configuration parameters

For example, accessing `{{ request.user }}` within a template will return the current user.

Declared subclasses should be gathered into a list or tuple for integration with NetBox. By default, NetBox looks for an iterable named `template_extensions` within a `template_content.py` file. (This can be overridden by setting `template_extensions` to a custom value on the plugin's PluginConfig.) An example is below.

```
from netbox.plugins import PluginTemplateExtension
from .models import Animal

class SiteAnimalCount(PluginTemplateExtension):
    models = ['dcim.site']

    def right_page(self):
        return self.render('netbox_animal_sounds/inc/animal_count.html', extra_context={
            'animal_count': Animal.objects.count(),
        })

template_extensions = [SiteAnimalCount]

```
