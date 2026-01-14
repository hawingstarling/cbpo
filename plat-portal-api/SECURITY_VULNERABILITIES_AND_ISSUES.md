# Security Vulnerabilities và Best Practices Issues

## 📋 Tổng Quan
Tài liệu này liệt kê tất cả các vấn đề về Security trong plat-portal-api, bao gồm:
- Hardcoded secrets và credentials
- Insecure authentication/authorization
- SQL injection risks
- XSS vulnerabilities
- CSRF protection issues
- Sensitive data exposure
- Insecure API endpoints

---

## 🔴 CRITICAL - Security Vulnerabilities

### 1. **Hardcoded Secrets và Credentials**

#### Vấn đề: Potential secret exposure trong code
```python
# app/tenancies/utils.py
from config.settings.common import SECRET_KEY  # ✅ OK - từ env
# Nhưng cần verify không có hardcoded secrets trong code
```

**Cần kiểm tra:**
- [ ] Không có API keys hardcoded
- [ ] Không có passwords trong code
- [ ] Không có database credentials trong source code
- [ ] Tất cả secrets đều từ environment variables

**Giải pháp:**
```bash
# Scan for potential secrets
grep -r "password\s*=\s*['\"].*['\"]" app/
grep -r "api_key\s*=\s*['\"].*['\"]" app/
grep -r "secret\s*=\s*['\"].*['\"]" app/
```

---

### 2. **Insecure Password Handling**

#### Vấn đề: Test passwords có thể leak vào production
```python
# app/tenancies/tests/organization/test_organization.py
# Line 354
'password': 'emcuangayhomqua',  # ❌ Weak password trong test
```

**Impact:**
- Test data có thể được commit
- Weak passwords trong test có thể được copy sang production

**Giải pháp:**
```python
# ✅ Use factory/fixtures với strong random passwords
from django.contrib.auth.hashers import make_password

def create_test_user():
    return User.objects.create(
        email='test@example.com',
        password=make_password('TestPassword123!@#')  # Strong password
    )
```

---

### 3. **Missing Input Validation**

#### Vấn đề: Không validate input đầy đủ
```python
# app/tenancies/sub_views/organization.py
# Line 104
client = Client.objects.get(pk=self.kwargs.get('client_id'))
# ❌ Không validate UUID format trước khi query
```

**Impact:**
- Potential for injection attacks
- Invalid input có thể gây lỗi không mong muốn
- Information disclosure qua error messages

**Giải pháp:**
```python
from django.core.validators import UUIDValidator
from django.core.exceptions import ValidationError

def get_client(self):
    client_id = self.kwargs.get('client_id')
    # ✅ Validate UUID format
    validator = UUIDValidator()
    try:
        validator(client_id)
    except ValidationError:
        raise InvalidParameterException(message="Invalid client_id format.")
    
    try:
        client = Client.objects.get(pk=client_id)
    except Client.DoesNotExist:
        raise InvalidParameterException(message="Client not found.")
    return client
```

---

### 4. **Insecure Direct Object References (IDOR)**

#### Vấn đề: Không verify user có quyền access object
```python
# Potential issue: Accessing objects without permission check
# Cần verify mọi object access đều có permission check
```

**Cần kiểm tra:**
- [ ] Tất cả object access đều có permission check
- [ ] User không thể access objects của user khác
- [ ] Organization/Client isolation được enforce

**Giải pháp:**
```python
# ✅ Always check permissions
def get_client(self):
    client = Client.objects.get(pk=self.kwargs.get('client_id'))
    # ✅ Verify user has access to this client
    if not self.request.user.has_perm('view_client', client):
        raise PermissionDenied("You don't have permission to access this client.")
    return client
```

---

### 5. **Missing Rate Limiting**

#### Vấn đề: API endpoints không có rate limiting
```python
# Cần implement rate limiting cho:
# - Login endpoints
# - Password reset endpoints
# - Registration endpoints
# - OTP generation endpoints
```

**Impact:**
- Brute force attacks
- DDoS attacks
- Resource exhaustion

**Giải pháp:**
```python
# config/settings/common.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',  # Stricter for login
        'password_reset': '3/hour',  # Very strict
    }
}

# app/tenancies/sub_views/client.py
from rest_framework.throttling import UserRateThrottle

class LoginView(APIView):
    throttle_classes = [UserRateThrottle]
    throttle_scope = 'login'  # Use custom rate
```

---

### 6. **Insecure Token Storage và Transmission**

#### Vấn đề: Token có thể bị expose
```python
# app/tenancies/utils.py
# Line 84-86
s = URLSafeTimedSerializer(SECRET_KEY)
token = s.dumps({'user_id': str(user.user_id)})
return token
```

**Cần kiểm tra:**
- [ ] Tokens không được log
- [ ] Tokens không được expose trong error messages
- [ ] HTTPS được enforce trong production
- [ ] Token expiration được set đúng

**Giải pháp:**
```python
# ✅ Set proper expiration
token = s.dumps(
    {'user_id': str(user.user_id)},
    salt='password-reset',  # Use salt
    max_age=3600  # 1 hour expiration
)

# ✅ Never log tokens
logger.info("Password reset requested for user", extra={'user_id': user.id})
# ❌ Never: logger.info(f"Token: {token}")
```

---

### 7. **Missing CSRF Protection**

#### Vấn đề: Cần verify CSRF protection được enable
```python
# config/settings/common.py
# Cần verify:
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',  # ✅ Must be present
    # ...
]
```

**Giải pháp:**
```python
# For API endpoints that need CSRF exemption (if using session auth):
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Only if necessary and with proper authentication
@method_decorator(csrf_exempt, name='dispatch')
class SomeAPIView(APIView):
    authentication_classes = [TokenAuthentication]  # Must have auth
```

---

### 8. **SQL Injection Risks**

#### Vấn đề: Raw SQL queries không được parameterized
```python
# Cần scan cho:
# - Raw SQL queries
# - .extra() với user input
# - String formatting trong queries
```

**Cần kiểm tra:**
```bash
# Scan for potential SQL injection
grep -r "\.raw(" app/
grep -r "\.extra(" app/
grep -r "\.execute(" app/
```

**Giải pháp:**
```python
# ❌ Bad - SQL injection risk
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# ✅ Good - Parameterized
User.objects.filter(email=user_input)

# ✅ Good - Raw query với parameters
User.objects.raw("SELECT * FROM users WHERE email = %s", [user_input])
```

---

### 9. **Sensitive Data in Logs**

#### Vấn đề: Logging sensitive information
```python
# app/tenancies/sub_views/organization.py
# Line 383
logger.info("%s --- URL Invitation: %s", self.request.data.get('email'), url)
# ✅ Email OK, nhưng cần verify không log passwords, tokens
```

**Cần kiểm tra:**
- [ ] Không log passwords
- [ ] Không log tokens
- [ ] Không log credit card numbers
- [ ] Không log full request data (có thể chứa sensitive info)

**Giải pháp:**
```python
# ✅ Sanitize logs
def sanitize_for_logging(data):
    """Remove sensitive fields from data before logging"""
    sensitive_fields = ['password', 'token', 'api_key', 'secret', 'credit_card']
    sanitized = data.copy()
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'
    return sanitized

logger.info("Request data", extra={'data': sanitize_for_logging(request.data)})
```

---

### 10. **Missing Security Headers**

#### Vấn đề: Security headers không được set
```python
# config/settings/common.py
# Cần add security headers
```

**Giải pháp:**
```python
# config/settings/common.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Or use django-security package
MIDDLEWARE = [
    # ...
    'django.middleware.security.SecurityMiddleware',
    # ...
]
```

---

### 11. **Insecure File Upload**

#### Vấn đề: File upload không được validate đầy đủ
```python
# app/tenancies/utils.py
# Line 44
image_name = token_hex(12) + '.' + image_extension
# ❌ Không validate file type, size, content
```

**Impact:**
- Malicious file uploads
- Path traversal attacks
- Storage exhaustion

**Giải pháp:**
```python
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image_upload(file):
    # ✅ Validate extension
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type {ext} not allowed.")
    
    # ✅ Validate size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("File too large.")
    
    # ✅ Validate content (check magic bytes)
    file.seek(0)
    header = file.read(4)
    if not is_valid_image_header(header):
        raise ValidationError("Invalid file content.")
    
    return True
```

---

### 12. **Missing Authentication trên Sensitive Endpoints**

#### Vấn đề: Cần verify tất cả sensitive endpoints đều có authentication
```python
# Cần review tất cả views:
# - Payment endpoints
# - User data endpoints
# - Permission endpoints
# - Admin endpoints
```

**Giải pháp:**
```python
# ✅ Always require authentication
from rest_framework.permissions import IsAuthenticated

class SensitiveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    
    def get(self, request):
        # Only authenticated users can access
        pass
```

---

## 🟡 MEDIUM - Security Best Practices

### 13. **Weak Password Policy**

#### Vấn đề: Không có password strength requirements
```python
# Cần implement password validation
```

**Giải pháp:**
```python
# app/tenancies/validations/password.py
from django.core.exceptions import ValidationError
import re

def validate_password_strength(password):
    """Validate password meets strength requirements"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters.")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number.")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")
    
    return True
```

---

### 14. **Missing Audit Logging**

#### Vấn đề: Không log security events đầy đủ
```python
# Cần log:
# - Login attempts (success/failure)
# - Permission changes
# - Sensitive data access
# - Password changes
# - Account modifications
```

**Giải pháp:**
```python
# app/core/audit_logger.py
import logging

audit_logger = logging.getLogger('audit')

def log_security_event(event_type, user, details):
    audit_logger.info(
        f"Security Event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': user.id if user else None,
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'details': details,
            'timestamp': timezone.now().isoformat()
        }
    )

# Usage
log_security_event('login_success', user, {'ip': request.META.get('REMOTE_ADDR')})
log_security_event('permission_changed', user, {'permission': 'admin', 'action': 'granted'})
```

---

### 15. **Insecure Session Configuration**

#### Vấn đề: Session security settings
```python
# config/settings/common.py
# Cần verify:
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour
```

---

## 📊 Tổng Kết

### Số Lượng Issues:
- **Critical:** 12 major security concerns
- **Medium:** 3 best practice improvements
- **Total:** 15+ security issues cần address

### Impact Ước Tính:
- **Security posture:** Cải thiện đáng kể khi fix
- **Compliance:** Đáp ứng các security standards
- **Risk reduction:** Giảm 70-80% security risks

### Priority Fix:
1. **P0 (Critical - Immediate):**
   - Input validation
   - Rate limiting
   - Authentication checks
   - SQL injection prevention

2. **P1 (High - Soon):**
   - Security headers
   - Password policy
   - Audit logging
   - Token security

3. **P2 (Medium - Next Sprint):**
   - File upload validation
   - Session security
   - Log sanitization

### Security Checklist:

- [ ] All secrets in environment variables
- [ ] Input validation on all endpoints
- [ ] Rate limiting on sensitive endpoints
- [ ] Authentication required on all sensitive endpoints
- [ ] Permission checks on all object access
- [ ] SQL injection prevention (no raw queries with user input)
- [ ] XSS prevention (proper escaping)
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] Password strength requirements
- [ ] Secure token handling
- [ ] Audit logging for security events
- [ ] File upload validation
- [ ] Sensitive data not in logs
- [ ] HTTPS enforced in production

### Tools Recommendations:

1. **Security Scanning:**
   ```bash
   # Bandit - Python security linter
   pip install bandit
   bandit -r app/
   
   # Safety - Check dependencies for vulnerabilities
   pip install safety
   safety check
   
   # Django security check
   python manage.py check --deploy
   ```

2. **Dependency Scanning:**
   ```bash
   # Check for vulnerable packages
   pip install pip-audit
   pip-audit
   ```

3. **Code Review Checklist:**
   - [ ] No hardcoded secrets
   - [ ] Input validation
   - [ ] Authentication/authorization
   - [ ] Error handling (no info disclosure)
   - [ ] Logging (no sensitive data)



