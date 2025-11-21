from app.core.context import AppContext
from app.core.services.app_confg import AppService
from app.tenancies.config_static_variable import MEMBER_STATUS
from app.tenancies.models import User, Role, Organization
from app.tenancies.services import ClientService
from app.tenancies.services import UserService, RoleService, UserOTPService, OrganizationService
from config.settings.common import ROOT_DIR

DATA = {
    'email': 'test@gmail.com',
    'password': 'test123'
}

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "permission/tests/fixtures/data.json",
    APPS_DIR + "tenancies/tests/fixtures/role.json",
    APPS_DIR + "tenancies/tests/fixtures/setting.json",
]


def init_client(data: dict = {'name': 'WS TEST', 'logo': ''}, user: User = None,
                organization: Organization = None, role_organization: Role = None):
    if not user:
        user = init_user()
    if not role_organization:
        role_organization = RoleService.role_client()
    if not organization:
        organization = OrganizationService.create_organization(name="TEST", owner=user)
    organization_role = OrganizationService.create_user_organization(organization=organization, user=user,
                                                                     role=role_organization)
    organization_role.status = MEMBER_STATUS[0][0]
    organization_role.save()
    return ClientService.create_client(name=data.get('name', 'WS-TEST'),
                                       logo=data.get('logo', ''),
                                       owner=user, organization=organization)


def init_user(email: str = None, password: str = None):
    if not email or not password:
        email = DATA['email']
        password = DATA['password']
    user = UserService.create_user(email=email,
                                   password=password)
    token = UserService.create_token(user=user)
    UserOTPService.get_or_create_code(user)
    return user, token


def init_app_context(app_name: str = "mwrw"):
    context = AppContext.instance()
    context.app_name_profile = app_name
    context.all_module_enum = AppService.get_all_module_enum()
    context.modules_app = AppService.get_modules_app(app_name=app_name)
    context.module_permissions_app = AppService.get_module_permissions_app(
        app_name=app_name)
    context.permissions_app = AppService.get_permissions_app(app_name=app_name)
