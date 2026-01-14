# Backlog Tickets - plat-portal-api

Tài liệu này tổng hợp tất cả các backlog tickets được tìm thấy trong project.

## 📋 Nguồn thông tin
- **Jira/Atlassian**: https://mayoretailinternetservices.atlassian.net/browse/
- **Project Prefix**: PS- (Platform Services)

---

## 🚀 Version v1.2.4 - Pending (CHANGELOG.md)

### 1. [PS-892](https://mayoretailinternetservices.atlassian.net/browse/PS-892/)
**Title**: 2D Transit PROD broken UI  
**Status**: Pending  
**Type**: Bug Fix  
**Location**: CHANGELOG.md

### 2. [PS-894](https://mayoretailinternetservices.atlassian.net/browse/PS-894/)
**Title**: [API]Check and fix security issue  
**Status**: Pending  
**Type**: Security  
**Location**: CHANGELOG.md  
**Related**: Xem thêm chi tiết trong `SECURITY_VULNERABILITIES_AND_ISSUES.md`

### 3. [PS-895](https://mayoretailinternetservices.atlassian.net/browse/PS-894/)
**Title**: Add information Last Login in the list Users  
**Status**: Pending  
**Type**: Feature  
**Location**: CHANGELOG.md  
**Note**: Link Jira có vẻ sai (trỏ đến PS-894 thay vì PS-895)

### 4. [PS-896](https://mayoretailinternetservices.atlassian.net/browse/PS-896/)
**Title**: As a user, I want to tracking Add, Update, Delete members in the Organizations Activity  
**Status**: Pending  
**Type**: Feature  
**Location**: CHANGELOG.md  
**Implementation**: 
- File: `app/tenancies/sub_views/organization.py`
- Sử dụng `log_activity_task` để track activities

### 5. [PS-923](https://mayoretailinternetservices.atlassian.net/browse/PS-923/)
**Title**: [Migration] Ensure LWA url is valid, improve LWA admin interface  
**Status**: Pending  
**Type**: Migration/Improvement  
**Location**: CHANGELOG.md

---

## 🔧 Tickets trong Code (TODO/In Progress)

### 6. PS-906
**Title**: REST Auth Serializers Configuration  
**Status**: TODO  
**Type**: Technical Debt/Refactoring  
**Locations**:
- `config/settings/common.py` (lines 236, 257)
  - TODO comment về REST_AUTH_SERIALIZERS configuration
  - TODO comment về OLD_PASSWORD_FIELD_ENABLED
- `app/tenancies/tests/client/test_user_login.py` (line 48)
  - TODO: feature/PS-906 - Token handling in login test
- `app/tenancies/serializers.py` (line 856)
  - Comment: PS-906 - Token expiration check logic

**Details**:
- Có vẻ như đang refactor cách xử lý authentication tokens
- Cần migrate từ token-based sang JWT-based authentication
- Test case đang sử dụng 'key' thay vì 'token' (temporary workaround)

### 7. PS-914
**Title**: Track Active Users  
**Status**: Implemented  
**Type**: Feature  
**Location**: `app/tenancies/sub_urls/client.py` (line 82)  
**Endpoint**: `clients/<uuid:client_id>/track-active/`  
**View**: `UserClientTrackLogin`

### 8. PS-867
**Title**: Optimize Organization Member Role Permissions  
**Status**: Completed  
**Type**: Optimization  
**Location**: `app/tenancies/serializers.py` (line 1068)  
**Details**: 
- Optimized logic for granting all access clients in Organization
- Related to MWM-1425: grant all access clients in ORG

### 9. PS-587
**Title**: Validate unique name of Client  
**Status**: Completed  
**Type**: Validation  
**Location**: `app/tenancies/serializers.py` (line 1229)  
**Implementation**: 
- Uses `ClientService.unique_name_client()` to validate unique client names within organization

---

## 🔒 Security Issues (Không có Ticket ID cụ thể)

Xem file `SECURITY_VULNERABILITIES_AND_ISSUES.md` để biết chi tiết về:
- 12 Critical security issues
- 3 Medium priority best practices
- Tổng cộng 15+ security issues cần address

**Note**: PS-894 có thể liên quan đến các security issues này.

---

## 📊 Tổng kết

### Tickets theo Status:
- **Pending (v1.2.4)**: 5 tickets (PS-892, PS-894, PS-895, PS-896, PS-923)
- **TODO/In Progress**: 1 ticket (PS-906)
- **Completed**: 2 tickets (PS-867, PS-587)
- **Implemented**: 1 ticket (PS-914)

### Tickets theo Type:
- **Bug Fix**: 1 (PS-892)
- **Security**: 1 (PS-894)
- **Feature**: 3 (PS-895, PS-896, PS-914)
- **Migration**: 1 (PS-923)
- **Technical Debt**: 1 (PS-906)
- **Optimization**: 1 (PS-867)
- **Validation**: 1 (PS-587)

### Priority Recommendations:
1. **High Priority**: 
   - PS-894 (Security issues - Critical)
   - PS-892 (PROD broken UI - Urgent)
   
2. **Medium Priority**:
   - PS-896 (User tracking feature)
   - PS-895 (Last Login feature)
   - PS-906 (Technical debt - Auth refactoring)
   
3. **Low Priority**:
   - PS-923 (Migration/Admin improvement)

---

## 🔍 Cách tìm thêm tickets

1. **GitLab Merge Requests**: Check merge request titles (theo convention, title phải bắt đầu bằng task ID)
2. **Git Commits**: Search commit messages cho PS-xxx patterns
3. **Jira Dashboard**: https://mayoretailinternetservices.atlassian.net/browse/PS-xxx
4. **Code Comments**: Search cho patterns như `# PS-`, `TODO.*PS-`, `FIXME.*PS-`

---

## 📝 Notes

- Một số ticket links trong CHANGELOG có vẻ không chính xác (PS-895 link đến PS-894)
- PS-906 có nhiều TODO comments trong code, cần được prioritize
- Security issues document có nhiều items nhưng không có ticket IDs cụ thể, có thể cần tạo tickets mới

---

## 🔗 Related Documents

- **[BACKLOG_SUGGESTIONS.md](./BACKLOG_SUGGESTIONS.md)**: Đề xuất các backlog tickets mới về Performance, Bug Fixes và New Features (20+ suggestions)
- **[SECURITY_VULNERABILITIES_AND_ISSUES.md](./SECURITY_VULNERABILITIES_AND_ISSUES.md)**: Chi tiết về security issues cần fix

