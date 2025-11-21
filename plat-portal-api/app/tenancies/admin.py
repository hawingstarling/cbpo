from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from app.payments.config import (
    APP_MWRW,
    PLAN_BUSINESS,
    PLAN_CUSTOM,
    PLAN_PROFESSIONAL,
    PLAN_STANDARD,
    APP_TRANSIT,
)
from app.payments.models import (
    ApprovalOrganizationalPayment,
    ApprovalOrganizationalServiceConfig,
    Plan,
    Subscription,
)
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import (
    AppClientConfig,
    Client,
    ClientModule,
    Organization,
    OrganizationUser,
    Role,
    User,
    UserClient,
    UserOTP,
    WhiteListEmail,
    Setting,
)
from ..payments.serializers import (
    MwPlanConfigSerializer,
    TransitPlanConfigSerializer,
    PlanConfigSerializer,
)


class UserAdmin(AuthUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "can_create_client",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_removed",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return True


@admin.register(UserClient)
class UserClientAdmin(admin.ModelAdmin):
    list_display = (
        "client_id",
        "client_name",
        "organization_name",
        "user_id",
        "user_email",
        "role_key_name",
        "created",
    )
    search_fields = (
        "user__email__icontains",
        "client__name__icontains",
        "client__organization__name__icontains",
    )
    list_filter = ("status",)
    ordering = ("-created",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return True

    def client_name(self, obj):
        return obj.client.name

    def user_email(self, obj):
        return obj.user.email

    def role_key_name(self, obj):
        return obj.role.name

    def organization_name(self, obj):
        return obj.client.organization.name if obj.client.organization else None

    client_name.short_description = "Client Id"
    organization_name.short_description = "Organization Name"
    user_email.short_description = "User Email"
    role_key_name.short_description = "Role"


@admin.register(OrganizationUser)
class OrganizationUserAdmin(admin.ModelAdmin):
    list_display = (
        "organization_id",
        "organization_name",
        "user_id",
        "user_email",
        "role_key_name",
        "created",
        "is_removed",
    )
    search_fields = (
        "user__email__icontains",
        "user__username__icontains",
        "organization__name__icontains",
    )
    list_filter = ("status", "is_removed")
    ordering = ("-created",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return True

    def user_email(self, obj):
        return obj.user.email

    def role_key_name(self, obj):
        return obj.role.key

    def organization_name(self, obj):
        return obj.organization.name

    organization_name.short_description = "Organization Name"
    user_email.short_description = "User Email"
    role_key_name.short_description = "Role"


@admin.register(ClientModule)
class ClientModuleAdmin(admin.ModelAdmin):
    list_display = (
        "client_id",
        "client_name",
        "organization_name",
        "module",
        "enabled",
        "created",
    )
    search_fields = (
        "client__name__icontains",
        "client__organization__name__icontains",
        "module",
    )
    list_filter = ("enabled",)
    ordering = ("-created",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return True

    def client_name(self, obj):
        return obj.client.name

    def organization_name(self, obj):
        return obj.client.organization.name if obj.client.organization else None

    client_name.short_description = "Client Id"
    organization_name.short_description = "Organization Name"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_removed",
        "organization_name",
        "logo",
        "active",
        "create_by",
        "created",
    )
    search_fields = ("name", "organization__name__icontains", "owner__email__icontains")
    list_filter = ("active", "is_removed")
    ordering = ("-created",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return True

    def create_by(self, obj):
        return obj.owner.email

    def organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    create_by.short_description = "Create By"
    organization_name.short_description = "Organization Name"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "logo", "create_by", "created")
    search_fields = ("name__icontains", "owner__email__icontains")
    ordering = ("-created",)

    actions = [
        "add_manually_standard",
        "add_manually_professional",
        "add_manually_business",
        "add_manually_custom",
        "init_blank_subscription",
    ]

    def add_manually_standard(self, request, queryset):
        plan = Plan.objects.get(type__exact=PLAN_STANDARD)
        for obj in queryset:
            self.__add_manually(obj, plan, request)

    def add_manually_professional(self, request, queryset):
        plan = Plan.objects.get(type__exact=PLAN_PROFESSIONAL)
        for obj in queryset:
            self.__add_manually(obj, plan, request)

    def add_manually_business(self, request, queryset):
        plan = Plan.objects.get(type__exact=PLAN_BUSINESS)
        for obj in queryset:
            self.__add_manually(obj, plan, request)

    def add_manually_custom(self, request, queryset):
        plan = Plan.objects.get(type__exact=PLAN_CUSTOM)
        for obj in queryset:
            self.__add_manually(obj, plan, request)

    def __add_manually(self, organization: Organization, plan: Plan, request):
        try:
            Subscription.objects.get(organization_id=organization.id)
            return self.message_user(
                request,
                "Subscription does exist for this organization.",
                messages.WARNING,
            )
        except Subscription.DoesNotExist:
            sub, _ = Subscription.all_objects.update_or_create(
                organization_id=organization.id,
                defaults={
                    "is_removed": False,
                    "external_subscription_id": None,
                    "expired_in": None,
                    "plan_id": plan.id,
                    "user_id": organization.owner.id,
                    "status": "active",
                    "is_active": True,
                },
            )
            ApprovalOrganizationalPayment.all_objects.update_or_create(
                organization_id=organization.id,
                defaults={
                    "is_removed": False,
                    "subscription_id": sub.id,
                    "max_internal_users": plan.max_internal_users,
                    "max_external_users": plan.max_external_users,
                    "max_workspaces": plan.max_workspaces,
                },
            )
            if plan.application == APP_MWRW:
                serializer = MwPlanConfigSerializer(plan)
            elif plan.application == APP_TRANSIT:
                serializer = TransitPlanConfigSerializer(plan)
            else:
                serializer = PlanConfigSerializer(plan)

            ApprovalOrganizationalServiceConfig.all_objects.update_or_create(
                organization=organization,
                defaults={"config": serializer.data, "is_removed": False},
            )

        except Exception as err:
            raise err

    def init_blank_subscription(self, request, queryset):
        if len(queryset) > 1:
            return self.message_user(request, "limit one selection", messages.ERROR)
        _organization = queryset[0]
        try:
            Subscription.objects.get(organization=_organization)
            return self.message_user(
                request,
                "Subscription does exist for this organization.",
                messages.WARNING,
            )
        except Subscription.DoesNotExist:
            Subscription.all_objects.update_or_create(
                organization=_organization,
                defaults={
                    "is_removed": False,
                    "user": _organization.owner,
                    "status": None,
                    "expired_in": None,
                    "is_active": False,
                },
            )
            return self.message_user(request, "Init successfully!", messages.SUCCESS)

    add_manually_standard.short_description = "Add manual subscription Standard"
    add_manually_professional.short_description = "Add manual subscription Professional"
    add_manually_business.short_description = "Add manual subscription Business"
    init_blank_subscription.short_description = (
        "Init blank subscription for the Organization Owner"
    )

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return True

    def create_by(self, obj):
        return obj.owner.email

    create_by.short_description = "Create By"


@admin.register(AppClientConfig)
class AppClientConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "app", "client", "created")
    search_fields = ("app__icontains", "client__name__icontains")
    ordering = ("-created",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return True


@admin.register(WhiteListEmail)
class WhiteListEmailAdmin(admin.ModelAdmin):
    list_display = ("email",)
    search_fields = ("email",)


@admin.register(Setting)
class SettingAdmin(DynamicArrayMixin, admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(UserOTP)
admin.site.register(Role)
