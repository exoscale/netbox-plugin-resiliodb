# Event Types - NetBox OSS
This feature was introduced in NetBox v4.1.

Plugins can register their own custom event types for use with NetBox [event rules](https://netboxlabs.com/docs/netbox/en/stable/models/extras/eventrule/). This is accomplished by calling the `register()` method on an instance of the `EventType` class. This can be done anywhere within the plugin. An example is provided below.

```
from django.utils.translation import gettext_lazy as _
from netbox.events import EventType, EVENT_TYPE_KIND_SUCCESS

EventType(
    name='ticket_opened',
    text=_('Ticket opened'),
    kind=EVENT_TYPE_KIND_SUCCESS
).register()

```


### `EventType` `dataclass`

A type of event which can occur in NetBox. Event rules can be defined to automatically perform some action in response to an event.

**Parameters:**



* Name: name
  * Type: str
  * Description: The unique name under which the event is registered.
  * Default: required
* Name: text
  * Type: str
  * Description: The human-friendly event name. This should support translation.
  * Default: required
* Name: kind
  * Type: str
  * Description: The event's classification (info, success, warning, or danger). The default type is info.
  * Default: 'info'
* Name: destructive
  * Type: bool
  * Description: Indicates that the associated object was destroyed as a result of the event (default: False).
  * Default: False

