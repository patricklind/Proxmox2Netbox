from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.core.exceptions import ValidationError

from netbox.models import NetBoxModel

from proxmox2netbox.fields import DomainField
from proxmox2netbox.choices import ProxmoxModeChoices, SyncTypeChoices, SyncStatusChoices
from proxmox2netbox.models.vm_backup import VMBackup as VMBackup

class CommonProperties:
    @property
    def ip(self) -> str:
        """Get the IP address of the Proxmox endpoint."""
        return str(self.ip_address.address).split('/')[0] if self.ip_address else None
    
    @property
    def url(self) -> str:
        """Construct the full URL for the Proxmox endpoint."""
        try:
            protocol = 'https' if self.verify_ssl else 'http'
            host = self.domain if self.domain else self.ip
            return f"{protocol}://{host}:{self.port}"
        except Exception as e:
            return f"Error: {e}"

class ProxmoxEndpoint(NetBoxModel, CommonProperties):
    name = models.CharField(
        default='Proxmox Endpoint',
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Name of the Proxmox Endpoint/Cluster. It will be filled automatically by API.'),
    )
    ip_address = models.ForeignKey(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('IP Address'),
        null=True,
        blank=True,
        help_text=_('IP Address of the Proxmox Endpoint (Cluster). Fallback if domain name is not provided.'),
    )
    domain = DomainField(
        verbose_name=_('Domain'),
        help_text=_('Domain name of the Proxmox Endpoint (Cluster).'),
        blank=True,
        null=True,
    )
    port = models.PositiveIntegerField(
        default=8006,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name=_('HTTP Port'),
    )
    mode = models.CharField(
        max_length=255,
        choices=ProxmoxModeChoices,
        default=ProxmoxModeChoices.PROXMOX_MODE_UNDEFINED,

    )
    version = models.CharField(max_length=20, blank=True, null=True)
    repoid = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name=_('Repository ID'),
    )
    username = models.CharField(
        default='root@pam',
        max_length=255,
        verbose_name=_('Username'),
        help_text=_("Username must be in the format of 'user@realm'. Default is 'root@pam'.")
    )
    password = models.CharField(
        max_length=255,
        verbose_name=_('Password'),
        help_text=_('Password for Proxmox login auth. Optional if you use API token auth.'),
        blank=True,
        null=True,
    )
    token_name = models.CharField(
        max_length=255,
        verbose_name=_('Token Name'),
        help_text=_('API token name for Proxmox token auth. Optional if password auth is used.'),
        blank=True,
        default='',
    )
    token_value = models.CharField(
        max_length=255,
        verbose_name=_('Token Value'),
        help_text=_('API token value/secret for Proxmox token auth. Optional if password auth is used.'),
        blank=True,
        default='',
    )
    verify_ssl = models.BooleanField(
        default=True,
        verbose_name=_('Verify SSL'),
        help_text=_('Choose or not to verify SSL certificate of the Proxmox Endpoint'),
    )
    netbox_site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('NetBox Site'),
        null=True,
        blank=True,
        help_text=_('NetBox site to assign synced objects to. If not set, a default site is used.'),
    )
    netbox_vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('NetBox VRF'),
        null=True,
        blank=True,
        help_text=_('VRF to assign synced IP addresses to. If not set, the global routing table is used.'),
    )
    netbox_device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Node Device Type'),
        null=True,
        blank=True,
        help_text=_('Device type to assign to synced Proxmox nodes. If not set, one is auto-detected from the node\'s CPU model or a generic "Proxmox Node" type is used.'),
    )

    class Meta:
        verbose_name_plural: str = "Proxmox Endpoints"
        unique_together = ['name', 'ip_address', 'domain']
        ordering = ('name',)

    def clean(self):
        super().clean()

        password = (self.password or '').strip()
        token_name = (self.token_name or '').strip()
        token_value = (self.token_value or '').strip()

        has_password = bool(password)
        has_token_name = bool(token_name)
        has_token_value = bool(token_value)
        has_token_auth = has_token_name and has_token_value

        # Password auth is enough on its own.
        # Only enforce token pair validation when password auth is not used.
        if not has_password:
            if has_token_name and not has_token_value:
                raise ValidationError({'token_value': _('Token Value is required when Token Name is set.')})

            if has_token_value and not has_token_name:
                raise ValidationError({'token_name': _('Token Name is required when Token Value is set.')})

            if not has_token_auth:
                raise ValidationError(
                    _('Provide either username/password or username with both Token Name and Token Value.')
                )

    def __str__(self):
        address = self.domain or (str(self.ip_address.address).split('/')[0] if self.ip_address else None) or 'no address'
        return f"{self.name} ({address})"

    def get_absolute_url(self):
        return reverse('plugins:proxmox2netbox:proxmoxendpoint', args=[self.pk])


class ProxmoxNodeTypeMapping(NetBoxModel):
    """
    Maps a specific Proxmox node name (per endpoint) to a NetBox DeviceType.
    When present, sync uses this type instead of the endpoint default.
    Existing nodes without a mapping are never updated.
    """
    endpoint = models.ForeignKey(
        to='proxmox2netbox.ProxmoxEndpoint',
        on_delete=models.CASCADE,
        related_name='node_type_mappings',
        verbose_name=_('Proxmox Endpoint'),
    )
    node_name = models.CharField(
        max_length=255,
        verbose_name=_('Node Name'),
        help_text=_('Exact node name as reported by Proxmox (e.g. pve01).'),
    )
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('Device Type'),
        help_text=_('Device type to assign to this node when syncing.'),
    )

    class Meta:
        verbose_name = 'Node Device Type Mapping'
        verbose_name_plural = 'Node Device Type Mappings'
        unique_together = ['endpoint', 'node_name']
        ordering = ('endpoint', 'node_name')

    def __str__(self):
        return f'{self.endpoint.name} / {self.node_name} → {self.device_type}'

    def get_absolute_url(self):
        return reverse('plugins:proxmox2netbox:proxmoxnodetypemapping', args=[self.pk])


class NetBoxEndpoint(NetBoxModel, CommonProperties):
    name = models.CharField(
        default='NetBox Endpoint',
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Name of the NetBox Endpoint.'),
    )
    ip_address = models.ForeignKey(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('IP Address'),
        null=True,
        blank=True,
        help_text=_('IP Address of the NetBox API. Fallback if domain name is not provided.'),
    )
    domain = DomainField(
        default='localhost',
        verbose_name=_('Domain'),
        help_text=_('Domain name of the NetBox API. Default is "localhost".'),
    )
    port = models.PositiveIntegerField(
        default=443,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name=_('HTTP Port'),
    )
    token = models.ForeignKey(
        to='users.Token',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('API Token'),
        null=True,
        blank=True,
        help_text=_('API Token for the NetBox API. Needed for Proxmox2NetBox Backend Service to communicate with NetBox.'),
    )
    verify_ssl = models.BooleanField(
        default=True,
        verbose_name=_('Verify SSL'),
        help_text=_('Choose or not to verify SSL certificate of the Netbox Endpoint'),
    )

    class Meta:
        verbose_name_plural: str = 'Netbox Endpoints'
        unique_together = ['name', 'ip_address']
        
    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    def get_absolute_url(self):
        # Legacy model kept for migration compatibility.
        return reverse("plugins:proxmox2netbox:home")


class FastAPIEndpoint(NetBoxModel, CommonProperties):
    name = models.CharField(
        default='Proxmox2NetBox Endpoint',
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Name of the Proxmox2NetBox Endpoint.'),
    )
    ip_address = models.ForeignKey(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('IP Address'),
        null=True,
        blank=True,
        help_text=_('IP Address of the Proxmox2NetBox API (Backend Service). Fallback if domain name is not provided.'),
    )
    domain = DomainField(
        default='localhost',
        verbose_name=_('Domain'),
        help_text=_('Domain name of the Proxmox2NetBox API (Backend Service). Default is "localhost".'),
    )
    port = models.PositiveIntegerField(
        default=8800,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name=_('HTTP Port'),
    )
    verify_ssl = models.BooleanField(
        default=True,
        verbose_name=_('Verify SSL'),
        help_text=_('Choose or not to verify SSL certificate of the Proxmox2NetBox Endpoint'),
    )
    token = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Token'),
        help_text=_('Token for the Proxmox2NetBox Endpoint. If not provided, the Proxmox2NetBox Endpoint will not be able to send messages to the client (user) browser.'),
    )
    use_websocket = models.BooleanField(
        default=False,
        verbose_name=_('Use WebSocket'),
        help_text=_('Choose or not to use WebSocket for the Proxmox2NetBox Endpoint. If enabled, the Proxmox2NetBox Endpoint will use WebSocket connection to send messages to the client (user) browser.'),
    )
    websocket_domain = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('WebSocket Domain'),
        help_text=_('Domain name of the WebSocket for the Proxmox2NetBox Endpoint'),
    )
    websocket_port = models.PositiveIntegerField(
        default=8800,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name=_('WebSocket Port'),
        help_text=_('Port of the WebSocket for the Proxmox2NetBox Endpoint (the same as HTTP port)'),
    )
    server_side_websocket = models.BooleanField(
        default=False,
        verbose_name=_('[BETA] Server Side WebSocket'),
        help_text=_('Choose or not to use server side WebSocket connection for the Proxmox2NetBox Endpoint. This is experimental feature and may not work as expected. This way, client (user) browser will not be able to send messages to the Proxmox2NetBox Endpoint.'),
    )

    class Meta:
        verbose_name_plural: str = 'FastAPI Endpoints'
        unique_together = ['name', 'ip_address']
    
    @property
    def websocket_url(self) -> str:
        """Construct the full URL for the Proxmox2NetBox endpoint."""
        try:
            protocol = 'wss' if self.verify_ssl else 'ws'
            host = self.domain if self.domain else self.ip
            return f"{protocol}://{host}:{self.websocket_port}"
        except Exception as e:
            return f"Error: {e}"
        
    def __str__(self):
        return f"{self.name} ({self.domain})"

    def get_absolute_url(self):
        # Legacy model kept for migration compatibility.
        return reverse("plugins:proxmox2netbox:home")


class SyncProcess(NetBoxModel):
    name = models.CharField(max_length=255, unique=True)
    sync_type = models.CharField(
        max_length=20,
        choices=SyncTypeChoices,
        default=SyncTypeChoices.ALL,
    )
    status = models.CharField(
        max_length=20,
        choices=SyncStatusChoices,
        default=SyncStatusChoices.NOT_STARTED,
    )  
    started_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text=_('When the sync process started. Format: YYYY-MM-DD HH:MM:SS')
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text=_('When the sync process completed. Format: YYYY-MM-DD HH:MM:SS')
    )
    runtime = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Time elapsed for the sync process. Format: seconds')
    )

    def __str__(self):
        return f'{self.name} ({self.sync_type})'
    
    def get_absolute_url(self):
        return reverse("plugins:proxmox2netbox:syncprocess", args=[self.pk])
