# Hướng dẫn Quản lý và Rà soát Bản quyền Phần mềm với Python

Tài liệu này cung cấp mã nguồn script Python giúp tự động quét, thống kê và hỗ trợ rà soát trạng thái bản quyền phần mềm trên hệ điều hành Windows.

---

## 1. Mã nguồn Python (`CheckSoftwareAudit.py`)

Script này sử dụng thư viện `winreg` (thư viện có sẵn trên hệ điều hành Windows, không cần cài đặt thêm bên thứ ba) để quét sâu vào cả hai phân vùng Registry `32-bit` và `64-bit`. 
Kết quả thu được sẽ được xuất ra dưới dạng file báo cáo định dạng CSV (`SoftwareAuditReport.csv`), giúp bạn dễ dàng mở bằng Microsoft Excel để theo dõi, bộ lọc và đối chiếu.

## 2. Cách chạy script này hiệu quả nhất

Vì kịch bản kiểm tra (Script) này cần thực hiện quyền truy cập và đọc thông tin cấu hình hệ thống sâu bên trong các nhánh bảo mật Registry (điển hình là nhánh hệ thống HKEY_LOCAL_MACHINE), 
bạn nên vận hành đoạn mã dưới quyền Quản trị viên (Administrator) tối cao để đảm bảo công cụ không bị hệ điều hành chặn và tránh bỏ sót bất kỳ phần mềm vi phạm hoặc ẩn giấu nào.

## 3. Các bước thực hiện tuần tự như sau:

- **Khởi chạy bảng điều khiển quyền cao:** Mở công cụ dòng lệnh Command Prompt (CMD) hoặc PowerShell trên Windows bằng cách kích chuột phải vào icon ứng dụng và chọn Run as Administrator (Chạy dưới quyền quản trị viên).

- **Thực thi lệnh quét:** Di chuyển thư mục làm việc đến vị trí lưu tệp script và chạy câu lệnh sau:

```bash
python CheckSoftwareAudit.py
```
- Kiểm tra kết quả báo cáo: Sau khi tiến trình chạy kết thúc, một file báo cáo mang tên software_audit_report.csv sẽ tự động xuất hiện ngay tại cùng thư mục chứa tệp script.
Lúc này, bạn chỉ cần mở tệp này bằng phần mềm Microsoft Excel là đã có ngay một bảng số liệu danh mục trực quan, rõ ràng và cực kỳ scannable phục vụ cho công tác hậu kiểm bản quyền nội bộ doanh nghiệp.
