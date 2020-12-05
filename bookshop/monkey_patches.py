from django.db import models
from django.db.models import ForeignKey
from django.db import models
from django.db.models import ForeignKey, OneToOneRel
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor, ForwardOneToOneDescriptor
from django.utils.translation import gettext_lazy as _


class ForeignKeyMonkeyPatch(ForeignKey):
    def __init__(self, to, on_delete=None, *args, **kwargs):
        super().__init__(to, on_delete, *args, **kwargs)


class OneToOneFieldMonkeyPatch(ForeignKeyMonkeyPatch):
    many_to_many = False
    many_to_one = False
    one_to_many = False
    one_to_one = True

    related_accessor_class = ReverseOneToOneDescriptor
    forward_related_accessor_class = ForwardOneToOneDescriptor
    rel_class = OneToOneRel

    description = _("One-to-one relationship")

    def __init__(self, to, on_delete=None, *args, **kwargs):
        kwargs['unique'] = True
        super().__init__(to, on_delete, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if "unique" in kwargs:
            del kwargs['unique']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        if self.remote_field.parent_link:
            return None
        return super().formfield(**kwargs)

    def save_form_data(self, instance, data):
        if isinstance(data, self.remote_field.model):
            setattr(instance, self.name, data)
        else:
            setattr(instance, self.attname, data)

    def _check_unique(self, **kwargs):
        # Override ForeignKey since check isn't applicable here.
        return []




setattr(models, 'ForeignKey', ForeignKeyMonkeyPatch)
setattr(models, 'OneToOneField', OneToOneFieldMonkeyPatch)