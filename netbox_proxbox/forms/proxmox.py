# Django Imports
from django import forms

# NetBox Imports
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from ipam.models import IPAddress
from django.utils.translation import gettext as _

# Proxbox Imports
from ..models import ProxmoxEndpoint
from ..choices import ProxmoxModeChoices


class ProxmoxEndpointForm(NetBoxModelForm):
    """
    Form for ProxmoxEndpoint model.
    It is used to CREATE and UPDATE ProxmoxEndpoint objects.
    """
    ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        help_text=_('Select a NetBox IP Address'),
        label=_('IP Address'),
        required=False
    )
    domain = forms.CharField(
        required=False,
        help_text=_('Domain name of the Proxmox Endpoint (Cluster). It will try using the DNS name provided in IP Address if it is not empty.'),
        label=_('Domain')
    )
    verify_ssl = forms.BooleanField(
        required=False,
        help_text=_('Choose or not to verify SSL certificate of the Proxmox Endpoint. Only use this if you are sure about the SSL certificate of the Proxmox Endpoint.'),
        label=_('Verify SSL')
    )
    comments = CommentField()

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            # NetBox 4.5 form stack may return None from parent clean().
            # In that case, validated field values are already in self.cleaned_data.
            cleaned_data = getattr(self, 'cleaned_data', {}) or {}

        password = (cleaned_data.get('password') or '').strip()
        token_name = (cleaned_data.get('token_name') or '').strip()
        token_value = (cleaned_data.get('token_value') or '').strip()

        if not password:
            if token_name and not token_value:
                self.add_error('token_value', _('Token Value is required when Token Name is set.'))

            if token_value and not token_name:
                self.add_error('token_name', _('Token Name is required when Token Value is set.'))

            if not (token_name and token_value):
                raise forms.ValidationError(
                    _('Provide either username/password or username with both Token Name and Token Value.')
                )

        return cleaned_data
    
    class Meta:
        model = ProxmoxEndpoint
        fields = (
            'name', 'ip_address', 'domain', 'port', 'username',
            'password', 'token_name', 'token_value', 'verify_ssl',
            'tags'
        )


class ProxmoxEndpointFilterForm(NetBoxModelFilterSetForm):
    """
    Filter form for ProxmoxEndpoint model.
    It is used in the ProxmoxEndpointListView.
    """
    
    model = ProxmoxEndpoint
    name = forms.CharField(
        required=False
    )
    ip_address = forms.ModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        help_text='Select IP Address'
    )
    mode = forms.MultipleChoiceField(
        choices=ProxmoxModeChoices,
        required=False
    )
