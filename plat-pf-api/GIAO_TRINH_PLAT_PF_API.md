# GIÁO TRÌNH DỰ ÁN PLAT-PF-API
## Precise Financial API - Hệ thống Quản lý Tài chính Chính xác

---

## MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Mô hình dữ liệu và Quan hệ](#3-mô-hình-dữ-liệu-và-quan-hệ)
4. [Logic nghiệp vụ](#4-logic-nghiệp-vụ)
5. [Các chức năng chính](#5-các-chức-năng-chính)
6. [Cơ sở dữ liệu](#6-cơ-sở-dữ-liệu)
7. [Cấu hình hệ thống](#7-cấu-hình-hệ-thống)
8. [API bên thứ ba](#8-api-bên-thứ-ba)
9. [Mô hình API bên thứ ba](#9-mô-hình-api-bên-thứ-ba)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1. Mục đích dự án

**Plat-PF-API (Precise Financial API)** là một hệ thống quản lý tài chính và phân tích dữ liệu bán hàng cho các doanh nghiệp thương mại điện tử. Hệ thống được thiết kế để:

- **Quản lý dữ liệu bán hàng**: Thu thập, xử lý và phân tích dữ liệu bán hàng từ nhiều kênh (Amazon, Shopify, eBay, v.v.)
- **Tính toán lợi nhuận**: Tự động tính toán lợi nhuận, chi phí, và các chỉ số tài chính
- **Tích hợp đa kênh**: Kết nối với nhiều nền tảng thương mại điện tử và hệ thống quản lý kho
- **Báo cáo và phân tích**: Cung cấp các báo cáo chi tiết và dashboard phân tích
- **Quản lý đa tenant**: Hỗ trợ nhiều khách hàng (clients) trên cùng một hệ thống

### 1.2. Công nghệ sử dụng

- **Backend Framework**: Django 3.1.14
- **API Framework**: Django REST Framework 3.14.0
- **Database**: PostgreSQL 9.6+
- **Task Queue**: Celery 5.3.4 với Redis
- **Search Engine**: Elasticsearch 7.15.0
- **Authentication**: OAuth2, JWT (RS256)
- **Cloud Storage**: Google Cloud Storage
- **Language**: Python 3.10.13

### 1.3. Cấu trúc ứng dụng

Dự án được tổ chức thành các Django apps:

```
app/
├── core/           # Core functionality (authentication, permissions, utilities)
├── financial/      # Financial management (sales, items, transactions)
├── database/       # Multi-tenant database management
├── edi/           # EDI (Electronic Data Interchange) processing
├── es/            # Elasticsearch integration
├── job/           # Background job management
├── selling_partner/ # Amazon Selling Partner API integration
├── shopify_partner/ # Shopify API integration
├── stat_report/   # Statistical reporting
├── third_party_logistic/ # 3PL integration
├── extensiv/      # Extensiv (3PL) integration
└── csp/           # Content Security Policy
```

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1. Kiến trúc Multi-Tenant

Hệ thống sử dụng kiến trúc **Multi-Tenant Database** với các đặc điểm:

#### 2.1.1. Database per Tenant
- Mỗi client có thể có database riêng hoặc dùng chung database với bảng riêng
- Dynamic table naming: `{table_name}_{client_id_tbl}`
- Ví dụ: `sale_abc123`, `item_abc123`

#### 2.1.2. MultiDbTableManagerBase

Manager cơ sở quản lý multi-tenant:

```python
class MultiDbTableManagerBase:
    - db_table_default: Tên bảng mặc định
    - db_table_template: Template tên bảng với {client_id_tbl}
    - tenant_db_for(client_id): Chuyển context sang client cụ thể
```

**Cách hoạt động:**
1. Khi gọi `Model.objects.tenant_db_for(client_id)`, manager sẽ:
   - Xác định database connection cho client
   - Tạo tên bảng động từ template
   - Cấu hình các quan hệ ForeignKey

### 2.2. Kiến trúc phân tầng

```
┌─────────────────────────────────────┐
│   API Layer (Django REST Framework) │
├─────────────────────────────────────┤
│   Service Layer (Business Logic)    │
├─────────────────────────────────────┤
│   Model Layer (Django ORM)           │
├─────────────────────────────────────┤
│   Database Layer (PostgreSQL)        │
└─────────────────────────────────────┘
```

### 2.3. Authentication & Authorization

#### 2.3.1. Authentication Methods
- **JWT (RS256)**: Sử dụng RSA key pair cho signing/verification
- **OAuth2**: Hỗ trợ OAuth2 Provider
- **Token Authentication**: Django REST Framework token

#### 2.3.2. Permission System
- Module-based permissions: `MODULE_PF_KEY`
- Role-based access control (RBAC)
- Client-scoped permissions

### 2.4. Background Processing

#### 2.4.1. Celery Configuration
- **Broker**: Redis
- **Result Backend**: Django Database
- **Task Routing**: Phân loại tasks vào các queues khác nhau
- **Scheduler**: Django Celery Beat

#### 2.4.2. Task Types
- **Live Feed Sync**: Đồng bộ dữ liệu từ các kênh bán hàng
- **Transaction Processing**: Xử lý giao dịch tài chính
- **Data Import/Export**: Import/export dữ liệu
- **Report Generation**: Tạo báo cáo

---

## 3. MÔ HÌNH DỮ LIỆU VÀ QUAN HỆ

### 3.1. Core Models

#### 3.1.1. Organization
```python
class Organization:
    - id: UUID (Primary Key)
    - name: Text
    - logo: CharField
```
**Mục đích**: Đại diện cho tổ chức/công ty mẹ

#### 3.1.2. ClientPortal
```python
class ClientPortal:
    - id: UUID (Primary Key)
    - organization: ForeignKey(Organization)
    - name: Text
    - logo: CharField
    - active: Boolean
    - dashboard_button_color: CharField
    - account_manager: CharField
    - user_sync_info: JSONField
    - is_oe: Boolean
```
**Mục đích**: Đại diện cho khách hàng (tenant) trong hệ thống

**Quan hệ**:
- `Organization` → `ClientPortal` (1:N)
- `ClientPortal` → `ClientSettings` (1:1)
- `ClientPortal` → `Brand` (1:N)
- `ClientPortal` → `Sale` (1:N)

#### 3.1.3. ClientSettings
```python
class ClientSettings:
    - client: OneToOneField(ClientPortal)
    - allow_sale_data_update_from: Date
    - ac_client_register: Boolean
    # Amazon MWS
    - ac_mws_access_key: CharField
    - ac_mws_secret_key: CharField
    - ac_mws_merchant_id: CharField
    # Amazon SPAPI
    - ac_spapi_app_id: CharField
    - ac_spapi_access_token: Text
    - ac_spapi_refresh_token: Text
    - ac_spapi_enabled: Boolean
    # CartRover
    - ac_cart_rover: JSONField
    - ac_cart_rover_enabled: Boolean
    # 3PL Central
    - ac_3pl_central_enabled: Boolean
    # COGs Configuration
    - cog_use_extensiv: Boolean
    - cog_use_dc: Boolean
    - cog_use_pf: Boolean
    - cog_priority_source: JSONField
```
**Mục đích**: Lưu trữ cấu hình và thông tin tích hợp cho từng client

### 3.2. Product & Inventory Models

#### 3.2.1. Brand
```python
class Brand:
    - id: UUID
    - name: CharField
    - client: ForeignKey(ClientPortal)
    - is_obsolete: Boolean
    - supplier_name: CharField
    - edi: CharField
```
**Mục đích**: Quản lý thương hiệu sản phẩm

#### 3.2.2. Channel
```python
class Channel:
    - id: UUID
    - name: CharField (unique)
    - label: CharField
    - use_in_global_filter: Boolean
    - is_pull_data: Boolean
    - time_control_priority: Integer
```
**Mục đích**: Đại diện cho các kênh bán hàng (Amazon, Shopify, eBay, v.v.)

#### 3.2.3. Item
```python
class Item:
    - id: UUID
    - channel: ForeignKey(Channel)
    - client: ForeignKey(ClientPortal)
    - sku: CharField
    - upc: CharField
    - asin: CharField
    - title: CharField
    - brand: ForeignKey(Brand)
    - est_shipping_cost: DecimalField
    - est_drop_ship_cost: DecimalField
    - fulfillment_type: ForeignKey(FulfillmentChannel)
    - product_number: CharField
    - product_type: CharField
```
**Mục đích**: Quản lý thông tin sản phẩm

**Quan hệ**:
- `Item` → `Channel` (N:1)
- `Item` → `Brand` (N:1)
- `Item` → `ItemCOG` (1:N)
- `Item` → `SaleItem` (1:N)

#### 3.2.4. ItemCOG
```python
class ItemCOG:
    - item: ForeignKey(Item)
    - cog: DecimalField
    - date: DateField
    - source: CharField
```
**Mục đích**: Lưu trữ Cost of Goods (COG) theo thời gian

### 3.3. Sales Models

#### 3.3.1. Sale
```python
class Sale:
    - id: BigAutoField
    - channel_sale_id: CharField
    - channel: ForeignKey(Channel)
    - client: ForeignKey(ClientPortal)
    - sale_status: ForeignKey(SaleStatus)
    - profit_status: ForeignKey(ProfitStatus)
    - date: DateTimeField
    - city, state, country, postal_code: CharField
    - customer_name: CharField
    - is_prime: Boolean
    - total_amount: DecimalField
```
**Mục đích**: Đại diện cho một đơn hàng

**Quan hệ**:
- `Sale` → `Channel` (N:1)
- `Sale` → `ClientPortal` (N:1)
- `Sale` → `SaleStatus` (N:1)
- `Sale` → `SaleItem` (1:N)
- `Sale` → `SaleChargeAndCost` (1:N)

#### 3.3.2. SaleItem
```python
class SaleItem:
    - sale: ForeignKey(Sale)
    - item: ForeignKey(Item)
    - quantity: IntegerField
    - unit_price: DecimalField
    - total_price: DecimalField
    - cog: DecimalField
    - shipping_cost: DecimalField
    - profit: DecimalField
```
**Mục đích**: Chi tiết các sản phẩm trong đơn hàng

**Quan hệ**:
- `SaleItem` → `Sale` (N:1)
- `SaleItem` → `Item` (N:1)
- `SaleItem` → `SaleItemFinancial` (1:1)

#### 3.3.3. SaleChargeAndCost
```python
class SaleChargeAndCost:
    - sale: ForeignKey(Sale)
    - type: CharField
    - amount: DecimalField
    - description: TextField
```
**Mục đích**: Lưu trữ các khoản phí và chi phí liên quan đến đơn hàng

### 3.4. Transaction Models

#### 3.4.1. GenericTransaction
```python
class GenericTransaction:
    - id: UUID
    - client: ForeignKey(ClientPortal)
    - channel: ForeignKey(Channel)
    - transaction_type: CharField
    - amount: DecimalField
    - currency: CharField
    - date: DateTimeField
    - description: TextField
```
**Mục đích**: Lưu trữ các giao dịch tài chính từ các nguồn khác nhau

### 3.5. Status Models

#### 3.5.1. SaleStatus
```python
class SaleStatus:
    - name: CharField
    - value: CharField (choices)
    - order: IntegerField
    - description: TextField
```
**Giá trị có thể**: `PENDING`, `SHIPPED`, `DELIVERED`, `RETURNED`, `REFUNDED`, v.v.

#### 3.5.2. ProfitStatus
```python
class ProfitStatus:
    - name: CharField
    - value: CharField (choices)
    - order: IntegerField
```
**Giá trị có thể**: `PROFITABLE`, `BREAK_EVEN`, `LOSS`, v.v.

### 3.6. Configuration Models

#### 3.6.1. BrandSetting
```python
class BrandSetting:
    - brand: ForeignKey(Brand)
    - client: ForeignKey(ClientPortal)
    - shipping_cost_method: CharField
    - drop_ship_cost_method: CharField
    - po_dropship_method: CharField
    - freight_cost_config: JSONField
```
**Mục đích**: Cấu hình tính toán chi phí cho từng brand

#### 3.6.2. FinancialSettings
```python
class FinancialSettings:
    - system_contacts: ArrayField(EmailField)
    - bulk_data_process_limit: IntegerField
    - division_max_limit: IntegerField
```
**Mục đích**: Cấu hình toàn hệ thống

### 3.7. User & Permission Models

#### 3.7.1. User
```python
class User:
    - user_id: UUID (Primary Key)
    - username: CharField
    - email: EmailField
    - first_name, last_name: CharField
    - avatar: CharField
    - hash: TextField
```
**Mục đích**: Quản lý người dùng (sync từ Portal Service)

#### 3.7.2. UserPermission
```python
class UserPermission:
    - user: ForeignKey(User)
    - client: ForeignKey(ClientPortal)
    - role: CharField
    - module: CharField
```
**Mục đích**: Phân quyền người dùng theo client và module

### 3.8. Sơ đồ quan hệ chính

```
Organization
    └── ClientPortal (1:N)
        ├── ClientSettings (1:1)
        ├── Brand (1:N)
        │   └── BrandSetting (1:1)
        ├── Channel (N:M qua Sale)
        ├── Sale (1:N)
        │   ├── SaleItem (1:N)
        │   │   └── Item (N:1)
        │   │       └── ItemCOG (1:N)
        │   └── SaleChargeAndCost (1:N)
        ├── GenericTransaction (1:N)
        └── UserPermission (1:N)
            └── User (N:1)
```

---

## 4. LOGIC NGHIỆP VỤ

### 4.1. Live Feed Integration

#### 4.1.1. Mục đích
Đồng bộ dữ liệu bán hàng từ các kênh (Amazon, Shopify, v.v.) vào hệ thống.

#### 4.1.2. Quy trình

**Bước 1: Khởi tạo Live Feed Manager**
```python
SaleItemsLiveFeedManager(
    client_id=client_id,
    flatten=DataFlattenTrack,
    marketplace="amazon",
    from_date="2024-01-01",
    to_date="2024-01-31"
)
```

**Bước 2: Lấy dữ liệu từ API**
- Gọi API của kênh (AC Service, DC Service)
- Phân trang dữ liệu
- Xử lý lỗi và retry

**Bước 3: Validate và Transform**
- Validate dữ liệu theo schema
- Transform sang format nội bộ
- Map các trường dữ liệu

**Bước 4: Import vào Database**
- Bulk insert/update vào Sale, SaleItem
- Tính toán các trường phái sinh
- Cập nhật status

#### 4.1.3. Filter Modes

- **POSTED_FILTER_MODE**: Lọc theo `purchase_date`
- **MODIFIED_FILTER_MODE**: Lọc theo `last_modified_date`

### 4.2. Transaction Event Processing

#### 4.2.1. Mục đích
Xử lý các sự kiện giao dịch từ Amazon Financial Events.

#### 4.2.2. Event Types

**Shipment Events**:
- Order shipment
- Shipment adjustments
- Shipment refunds

**Adjustment Events**:
- Reimbursements
- Chargebacks
- Adjustments

**Refund Events**:
- Order refunds
- Partial refunds

**Service Fee Events**:
- Subscription fees
- FBA fees
- Other service fees

#### 4.2.3. Quy trình xử lý

1. **Nhận dữ liệu từ SPAPI**
2. **Parse và validate**
3. **Map sang GenericTransaction**
4. **Tính toán ảnh hưởng đến Sale/SaleItem**
5. **Cập nhật profit, charges**

### 4.3. COG (Cost of Goods) Calculation

#### 4.3.1. Nguồn COG

1. **Extensiv**: Từ hệ thống 3PL Extensiv
2. **Data Central (DC)**: Từ Data Central service
3. **PF (Precise Financial)**: Từ dữ liệu nội bộ

#### 4.3.2. Priority System

```python
cog_priority_source = [
    {"source": "extensiv", "priority": 1},
    {"source": "dc", "priority": 2},
    {"source": "pf", "priority": 3}
]
```

Hệ thống sẽ chọn COG từ nguồn có priority cao nhất (số nhỏ nhất).

#### 4.3.3. COG Conflict Resolution

Khi có nhiều nguồn COG khác nhau:
- Tạo `COGSConflict` record
- Cho phép user chọn nguồn sử dụng
- Log conflict để audit

### 4.4. Shipping Cost Calculation

#### 4.4.1. Nguồn Shipping Cost

1. **FedEx Shipment**: Từ dữ liệu FedEx
2. **Brand Settings**: Tính theo cấu hình brand
3. **Estimated**: Ước tính từ Item.est_shipping_cost

#### 4.4.2. Calculation Methods

**From Brand Settings**:
- Fixed cost per unit
- Percentage of sale price
- Tiered pricing

**From FedEx**:
- Actual shipping cost từ FedEx API
- Match theo tracking number

### 4.5. Profit Calculation

#### 4.5.1. Công thức

```
Profit = Total Price - COG - Shipping Cost - Charges - Fees
```

#### 4.5.2. Profit Status

- **PROFITABLE**: Profit > 0
- **BREAK_EVEN**: Profit = 0
- **LOSS**: Profit < 0

### 4.6. Data Flattening

#### 4.6.1. Mục đích
Chuyển đổi dữ liệu quan hệ thành dạng phẳng (flat) để:
- Export ra file
- Index vào Elasticsearch
- Tạo báo cáo

#### 4.6.2. Quy trình

1. **Aggregate dữ liệu** từ Sale, SaleItem, Transaction
2. **Flatten** thành một record
3. **Export** hoặc **Index** vào Elasticsearch

### 4.7. Bulk Operations

#### 4.7.1. Bulk Sync
Đồng bộ hàng loạt dữ liệu từ nguồn bên ngoài:
- Validate dữ liệu
- Batch processing
- Error handling và retry

#### 4.7.2. Bulk Edit
Cho phép chỉnh sửa hàng loạt SaleItem:
- Update COG
- Update shipping cost
- Update status

---

## 5. CÁC CHỨC NĂNG CHÍNH

### 5.1. Quản lý Sales

#### 5.1.1. Xem danh sách Sales
- Filter theo client, channel, date range
- Search theo sale ID, customer name
- Sort và pagination

#### 5.1.2. Chi tiết Sale
- Thông tin đơn hàng
- Danh sách items
- Charges và costs
- Transaction history

#### 5.1.3. Cập nhật Sale
- Update status
- Update profit status
- Manual adjustments

### 5.2. Quản lý Items

#### 5.2.1. CRUD Operations
- Create, Read, Update, Delete items
- Import từ file
- Bulk update

#### 5.2.2. COG Management
- Xem lịch sử COG
- Set COG manually
- Resolve COG conflicts

### 5.3. Dashboard & Reports

#### 5.3.1. Dashboard
- Tổng quan sales
- Top products
- Profit analysis
- Geographic distribution

#### 5.3.2. Custom Reports
- Sales report
- Profit report
- Item performance
- Shipping cost analysis

### 5.4. Data Import/Export

#### 5.4.1. Import
- Import từ file Excel/CSV
- Import từ API
- Validation và error reporting

#### 5.4.2. Export
- Export to Excel
- Export to CSV
- Export to JSON

### 5.5. Integration Management

#### 5.5.1. Amazon SPAPI
- OAuth connection
- Report management
- Financial events sync

#### 5.5.2. Shopify
- OAuth connection
- Order sync
- Product sync

#### 5.5.3. Extensiv (3PL)
- Product COG sync
- Inventory sync

### 5.6. Alert System

#### 5.6.1. Alert Types
- No brand settings
- Data sync errors
- COG conflicts
- Low profit items

#### 5.6.2. Delivery Methods
- Email
- In-app notification

### 5.7. User Management

#### 5.7.1. User Permissions
- Assign roles
- Set module permissions
- Client-scoped access

#### 5.7.2. User Favorites
- Save favorite filters
- Save favorite reports

---

## 6. CƠ SỞ DỮ LIỆU

### 6.1. Database Architecture

#### 6.1.1. Multi-Database Support

Hệ thống hỗ trợ nhiều database:
- **Default database**: Lưu trữ shared data (Organization, Channel, User, v.v.)
- **Client databases**: Mỗi client có thể có database riêng

#### 6.1.2. Dynamic Table Naming

Với multi-tenant trong cùng database:
- Template: `{table_name}_{client_id_tbl}`
- Ví dụ: `sale_abc123def456`, `item_abc123def456`

#### 6.1.3. Database Configuration

```python
# config/settings/common.py
DATABASES = {
    'default': env.db('DATABASE_URL'),
    # Dynamic databases từ DatabaseConfig
}
```

### 6.2. Table Structure

#### 6.2.1. Shared Tables (Default DB)

- `organization`
- `client_portal`
- `client_settings`
- `channel`
- `user`
- `user_permission`
- `sale_status`
- `profit_status`
- `financial_settings`

#### 6.2.2. Client-Specific Tables

- `sale_{client_id}`
- `sale_item_{client_id}`
- `item_{client_id}`
- `item_cog_{client_id}`
- `generic_transaction_{client_id}`
- `sale_charge_and_cost_{client_id}`

### 6.3. Indexes

#### 6.3.1. Common Indexes

- `client_id` + `channel_id`
- `date` ranges
- `channel_sale_id` (unique)
- `sku` + `client_id`

#### 6.3.2. Performance Optimization

- GIN indexes cho ArrayField
- Composite indexes cho queries thường dùng
- Partial indexes cho soft-delete

### 6.4. Migrations

#### 6.4.1. Standard Migrations
```bash
python manage.py migrate
```

#### 6.4.2. Template Table Migration
```bash
python manage.py migrate_db_table_template
```

Tạo template tables cho dynamic table naming.

### 6.5. Database Connections

#### 6.5.1. Connection Pooling
- Sử dụng psycopg2
- Connection pooling qua Django

#### 6.5.2. Transaction Management
- `ATOMIC_REQUESTS = True`: Mỗi request là một transaction
- Manual transaction control cho bulk operations

---

## 7. CẤU HÌNH HỆ THỐNG

### 7.1. Environment Variables

#### 7.1.1. Database
```env
DATABASE_URL=postgres://user:password@host:5432/dbname
DATABASE_{CLIENT_NAME}_URL=postgres://...
```

#### 7.1.2. Authentication
```env
PRIVATE_KEY_PATH=/path/to/private.pem
PUBLIC_KEY_PATH=/path/to/public.pem
JWT_EXPIRATION_DELTA=5  # minutes
```

#### 7.1.3. External Services
```env
# Portal Service
URL_PORTAL_SERVICE=http://portal-api.qa.channelprecision.com
PS_INTERNAL_TOKEN=123456

# Data Source Service
URL_DS_SERVICE=http://ds-api.qa.channelprecision.com
DS_TOKEN=xxx

# Account Central Service
URL_AC_SERVICE=http://ac-api.qa.channelprecision.com
AC_API_KEY=xxx

# Data Central Service
URL_DC_SERVICE=http://dc-api.qa.channelprecision.com
```

#### 7.1.4. Celery
```env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_TASK_DEFAULT_QUEUE=celery
CELERY_TASK_QUEUE_IMPORT_LIB=celery
```

#### 7.1.5. Redis
```env
USER_CLIENT_REDIS_CHANNEL=redis://redis:6379/0
REDIS_TTL=5  # minutes
PREFIX_REDIS_KEY=PF
```

#### 7.1.6. Firebase
```env
FIRE_BASE_REAL_TIME_DB_URL=https://xxx.firebaseio.com
FIRE_BASE_ACCESS_KEY=xxx
FIRE_BASE_REF=/
```

#### 7.1.7. Google Cloud Storage
```env
GOOGLE_CLOUD_STORAGE_BUCKET_NAME=xxx
GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY=xxx
```

#### 7.1.8. Elasticsearch
```env
ELASTICSEARCH_URL_DEFAULT=http://localhost:9200
```

#### 7.1.9. Shopify
```env
SHOPIFY_API_VERSION=2025-10
FERNET_KEY=xxx  # For encrypting Shopify tokens
```

#### 7.1.10. FedEx FTP
```env
FTP_FEDEX_HOST=xxx
FTP_FEDEX_USER=xxx
FTP_FEDEX_PASSWD=xxx
FTP_FEDEX_PORT=21
```

#### 7.1.11. Twilio (SMS)
```env
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=xxx
```

### 7.2. Django Settings

#### 7.2.1. Installed Apps
```python
LOCAL_APPS = (
    'app.core',
    'app.financial',
    'app.edi',
    'app.database',
    'app.job',
    'app.es',
    'app.selling_partner',
    'app.shopify_partner',
    'app.stat_report',
    'app.third_party_logistic',
    'app.extensiv',
)
```

#### 7.2.2. Middleware
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
    'app.csp.middleware.CSPMiddleware'
]
```

#### 7.2.3. REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'app.core.simple_authentication.JWTTokenHandlerAuthentication'
    ],
    'DEFAULT_PAGINATION_CLASS': 'app.core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'app.core.exception_handler.api_exception_handler',
}
```

### 7.3. Celery Configuration

#### 7.3.1. Task Routes
```python
CELERY_TASK_ROUTES = {
    'plat_import_lib_api.tasks.*': {'queue': 'import_lib'}
}
```

#### 7.3.2. Task Settings
```python
CELERYD_MAX_TASKS_PER_CHILD = 100
CELERYD_TASK_SOFT_TIME_LIMIT = 2400  # 40 minutes
CELERY_RESULT_BACKEND = 'django-db'
```

### 7.4. Logging

#### 7.4.1. Log Handlers
- **File**: Rotating file handler
- **Console**: Stream handler
- **Bugsnag**: Error tracking

#### 7.4.2. Log Levels
- DEBUG: Development
- INFO: General information
- ERROR: Errors (sent to Bugsnag)

---

## 8. API BÊN THỨ BA

### 8.1. Portal Service (PS)

#### 8.1.1. Mục đích
Quản lý users, organizations, clients.

#### 8.1.2. Endpoints sử dụng
- User information
- Client information
- Organization information

#### 8.1.3. Authentication
- Internal token: `PS_INTERNAL_TOKEN`

### 8.2. Data Source Service (DS)

#### 8.2.1. Mục đích
Cung cấp dữ liệu bán hàng từ các kênh.

#### 8.2.2. Endpoints
- `GET /sale_items`: Lấy danh sách sale items
- Parameters: `marketplace`, `page`, `limit`, `from`, `to`

#### 8.2.3. Authentication
- Token: `DS_TOKEN`

### 8.3. Account Central Service (AC)

#### 8.3.1. Mục đích
Quản lý tài khoản Amazon (MWS, SPAPI).

#### 8.3.2. Endpoints
- Amazon account registration
- MWS credentials
- SPAPI OAuth

#### 8.3.3. Authentication
- API Key: `AC_API_KEY`

### 8.4. Data Central Service (DC)

#### 8.4.1. Mục đích
Cung cấp dữ liệu COG và inventory.

#### 8.4.2. Endpoints
- COG data
- Inventory data

### 8.5. Amazon Selling Partner API (SPAPI)

#### 8.5.1. Mục đích
Lấy dữ liệu từ Amazon:
- Financial events
- Reports
- Orders

#### 8.5.2. OAuth Flow

1. **Generate OAuth URL**
   - User click "Connect Amazon"
   - Redirect to Amazon OAuth consent page

2. **Callback**
   - Amazon redirect với `code` và `state`
   - Exchange `code` lấy `access_token` và `refresh_token`

3. **Store Tokens**
   - Encrypt và lưu vào `ClientSettings`

#### 8.5.3. Report Management

**Request Report**:
```python
POST /reports/2021-06-30/reports
{
    "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
    "dataStartTime": "2024-01-01T00:00:00Z",
    "dataEndTime": "2024-01-31T23:59:59Z"
}
```

**Get Report**:
```python
GET /reports/2021-06-30/reports/{reportId}
```

**Download Report**:
```python
GET /reports/2021-06-30/documents/{documentId}
```

#### 8.5.4. Financial Events

**List Financial Events**:
```python
GET /finances/v0/financialEvents
{
    "PostedAfter": "2024-01-01T00:00:00Z",
    "PostedBefore": "2024-01-31T23:59:59Z"
}
```

### 8.6. Shopify API

#### 8.6.1. Mục đích
Lấy dữ liệu từ Shopify:
- Orders
- Products
- Inventory

#### 8.6.2. OAuth Flow

1. **Generate OAuth URL**
   ```python
   GET /admin/oauth/authorize
   ?client_id={api_key}
   &scope={scope}
   &redirect_uri={redirect_url}
   &state={state}
   ```

2. **Callback**
   - Shopify redirect với `code`
   - Exchange `code` lấy `access_token`

3. **Store Token**
   - Encrypt bằng Fernet
   - Lưu vào `OauthTokenRequest`

#### 8.6.3. API Endpoints

**Orders**:
```python
GET /admin/api/2025-10/orders.json
?status=any
&created_at_min=2024-01-01T00:00:00Z
&created_at_max=2024-01-31T23:59:59Z
```

**Products**:
```python
GET /admin/api/2025-10/products.json
```

### 8.7. Extensiv API (3PL)

#### 8.7.1. Mục đích
Lấy COG và inventory từ hệ thống 3PL Extensiv.

#### 8.7.2. Authentication
- Token-based: `cog_extensiv_token`

#### 8.7.3. Endpoints
- Product COG
- Inventory levels

### 8.8. FedEx API

#### 8.8.1. Mục đích
Lấy dữ liệu shipping cost từ FedEx.

#### 8.8.2. Integration Methods
- **FTP**: Download shipment files
- **API**: Real-time queries

### 8.9. Elasticsearch

#### 8.9.1. Mục đích
Index và search dữ liệu.

#### 8.9.2. Indexes
- `sale_item_flatten_{client_id}`
- `item_{client_id}`

#### 8.9.3. Operations
- Index documents
- Search queries
- Aggregations

---

## 9. MÔ HÌNH API BÊN THỨ BA

### 9.1. Amazon SPAPI Models

#### 9.1.1. SPReportClient
```python
class SPReportClient:
    - client: ForeignKey(ClientPortal)
    - channel: ForeignKey(Channel)
    - report_type: ForeignKey(SPReportType)
    - ac_report_id: CharField
    - status: CharField (IN_PROGRESS, READY, ERROR)
    - date_range_covered_start: DateField
    - date_range_covered_end: DateField
    - file_names: ArrayField
    - download_urls: ArrayField
```

**Mục đích**: Quản lý lifecycle của SPAPI reports.

**Quy trình**:
1. Create `SPReportClient` với status `IN_PROGRESS`
2. Request report từ SPAPI
3. Poll cho đến khi report `READY`
4. Download và parse report
5. Update status và file info

#### 9.1.2. SPReportType
```python
class SPReportType:
    - category: ForeignKey(SPReportCategory)
    - name: CharField
    - value: CharField  # SPAPI report type value
    - is_date_range: Boolean
    - source: CharField  # SPAPI_SOURCE_TYPE
```

**Ví dụ report types**:
- `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`
- `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA`
- `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2`

#### 9.1.3. SPOauthClientRegister
```python
class SPOauthClientRegister:
    - client: ForeignKey(ClientPortal)
    - app_setting: ForeignKey(AppSetting)
    - oauth_token_request: ForeignKey(OauthTokenRequest)
    - latest: Boolean
```

**Mục đích**: Quản lý OAuth connection cho client.

### 9.2. Shopify API Models

#### 9.2.1. OauthTokenRequest
```python
class OauthTokenRequest:
    - client: ForeignKey(ClientPortal)
    - shop_url: CharField
    - state: CharField
    - access_token: TextField (encrypted)
```

**Mục đích**: Lưu trữ OAuth tokens (encrypted).

**Encryption**:
- Sử dụng Fernet (symmetric encryption)
- Key từ `FERNET_KEY` env variable

#### 9.2.2. ShopifyPartnerOauthClientRegister
```python
class ShopifyPartnerOauthClientRegister:
    - client: ForeignKey(ClientPortal)
    - oauth_token_request: ForeignKey(OauthTokenRequest)
    - enabled: Boolean
```

**Mục đích**: Enable/disable Shopify integration cho client.

### 9.3. Extensiv Models

#### 9.3.1. COGSConflict
```python
class COGSConflict:
    - client: ForeignKey(ClientPortal)
    - channel: ForeignKey(Channel)
    - sku: CharField
    - sale_ids: ArrayField
    - extensiv_cog: DecimalField
    - dc_cog: DecimalField
    - pf_cog: DecimalField
    - used_cog: CharField  # Source được chọn
    - status: CharField  # CONFLICT, RESOLVED
```

**Mục đích**: Quản lý conflicts khi có nhiều nguồn COG khác nhau.

**Quy trình**:
1. Detect conflict khi sync COG
2. Tạo `COGSConflict` record
3. User chọn nguồn COG
4. Update `used_cog` và `status = RESOLVED`

### 9.4. Data Source Models

#### 9.4.1. DataFlattenTrack
```python
class DataFlattenTrack:
    - client: ForeignKey(ClientPortal)
    - channel: ForeignKey(Channel)
    - type: CharField  # LIVE_FEED, TRANS_EVENT, etc.
    - last_run: DateTimeField
    - last_run_event: DateTimeField
    - status: CharField
```

**Mục đích**: Track lần sync cuối cùng cho mỗi channel.

### 9.5. Integration Service Models

#### 9.5.1. GenericTransaction
```python
class GenericTransaction:
    - client: ForeignKey(ClientPortal)
    - channel: ForeignKey(Channel)
    - transaction_type: CharField
    - amount: DecimalField
    - currency: CharField
    - date: DateTimeField
    - description: TextField
    - source: CharField  # SPAPI, SHOPIFY, etc.
```

**Mục đích**: Unified model cho tất cả transactions từ các nguồn.

### 9.6. API Request/Response Patterns

#### 9.6.1. Standard Request
```python
{
    "client_id": "uuid",
    "marketplace": "amazon",
    "from_date": "2024-01-01T00:00:00Z",
    "to_date": "2024-01-31T23:59:59Z",
    "page": 1,
    "limit": 100
}
```

#### 9.6.2. Standard Response
```python
{
    "data": [...],
    "pagination": {
        "page": 1,
        "limit": 100,
        "total": 1000,
        "total_pages": 10
    },
    "errors": []
}
```

### 9.7. Error Handling

#### 9.7.1. API Errors
- **400 Bad Request**: Invalid parameters
- **401 Unauthorized**: Authentication failed
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

#### 9.7.2. Retry Logic
- Exponential backoff
- Max retries: 5
- Retry on: 500, 502, 503, 504

### 9.8. Rate Limiting

#### 9.8.1. SPAPI
- 0.5 requests/second (default)
- Burst: 15 requests

#### 9.8.2. Shopify
- 2 requests/second
- Bucket: 40 requests

#### 9.8.3. Internal Services
- DS Service: Configurable
- AC Service: 50 items/request

---

## KẾT LUẬN

Dự án **Plat-PF-API** là một hệ thống phức tạp với nhiều tính năng:

1. **Multi-tenant architecture** cho phép phục vụ nhiều clients
2. **Tích hợp đa kênh** với Amazon, Shopify, và các nền tảng khác
3. **Xử lý dữ liệu tài chính** tự động và chính xác
4. **Báo cáo và phân tích** mạnh mẽ
5. **Scalable architecture** với Celery và Redis

Hệ thống được thiết kế để mở rộng và dễ bảo trì, với code structure rõ ràng và documentation đầy đủ.

---

**Tài liệu này được tạo tự động từ codebase. Để cập nhật, vui lòng chỉnh sửa file này hoặc tạo issue trên repository.**















