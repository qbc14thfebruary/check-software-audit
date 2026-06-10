import csv
import os
import winreg
from datetime import datetime

# Định nghĩa tập luật để phân loại nhanh các phần mềm phổ biến
FREE_PUBLISHERS = [
    "google",
    "mozilla",
    "apache",
    "node.js",
    "git",
    "wireshark",
    "videolan",
]
FREE_SOFTWARE_KEYWORDS = [
    "7-zip",
    "sharex",
    "crystaldisk",
    "notepad++",
    "vlc",
    "python",
    "vscode",
    "visual studio code",
    "brave",
    "chrome",
    "firefox",
    "winscp",
    "putty",
]
COMMERCIAL_KEYWORDS = ["adobe", "autocad", "autodesk", "winrar", "office", "idm"]


def analyze_license(name, publisher):
    name_lower = name.lower()
    pub_lower = publisher.lower()

    # 1. Kiểm tra phần mềm mở/miễn phí quen thuộc
    if any(k in name_lower for k in FREE_SOFTWARE_KEYWORDS) or any(
        p in pub_lower for p in FREE_PUBLISHERS
    ):
        return "Miễn phí (Free/OpenSource)", "An toàn"

    # 2. Kiểm tra các phần mềm thường bị dùng lậu trong doanh nghiệp
    if any(k in name_lower for k in COMMERCIAL_KEYWORDS):
        if "winrar" in name_lower:
            return (
                "Cần xem xét (Check file rarreg.key)",
                "Rủi ro cao nếu không có hóa đơn",
            )
        if "office" in name_lower or "microsoft 365" in name_lower:
            return (
                "Cần xem xét (Check bản quyền/KMS)",
                "Rủi ro cao nếu dùng Crack",
            )
        return "Thương mại (Nghi vấn Lậu nếu thiếu Key)", "Cần kiểm tra hóa đơn"

    # 3. Kiểm tra trường hợp đặc biệt: Visual Studio Community
    if "visual studio" in name_lower and "community" in name_lower:
        return "Miễn phí có điều kiện (Community)", "Rủi ro nếu công ty lớn"

    # 4. Các thành phần hệ thống hoặc thư viện đi kèm mặc định
    if (
        "microsoft" in pub_lower
        or "update" in name_lower
        or "redistributable" in name_lower
        or "driver" in name_lower
    ):
        return "Hệ thống / Mặc định", "An toàn"

    return "Cần xem xét (Chưa rõ nguồn gốc)", "Kiểm tra thủ công"


def format_registry_date(date_str):
    """Chuyển đổi định dạng ngày YYYYMMDD trong Registry sang YYYY-MM-DD"""
    if not date_str or len(date_str) != 8:
        return "Không rõ"
    try:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    except Exception:
        return "Không rõ"


def get_installed_software(hive, subkey, architecture):
    software_list = []
    try:
        registry_key = winreg.OpenKey(
            hive,
            subkey,
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            if architecture == 64
            else winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
        )
        count = winreg.QueryInfoKey(registry_key)[0]

        for i in range(count):
            try:
                software_name_key = winreg.EnumKey(registry_key, i)
                sub_key_path = f"{subkey}\\{software_name_key}"
                current_key = winreg.OpenKey(hive, sub_key_path)

                try:
                    display_name = winreg.QueryValueEx(
                        current_key, "DisplayName"
                    )[0]
                except FileNotFoundError:
                    continue

                try:
                    display_version = winreg.QueryValueEx(
                        current_key, "DisplayVersion"
                    )[0]
                except FileNotFoundError:
                    display_version = "Unknown"

                try:
                    publisher = winreg.QueryValueEx(current_key, "Publisher")[0]
                except FileNotFoundError:
                    publisher = "Unknown"

                try:
                    install_location = winreg.QueryValueEx(
                        current_key, "InstallLocation"
                    )[0]
                except FileNotFoundError:
                    install_location = "Unknown"

                # Lấy ngày cài đặt phần mềm từ Registry
                try:
                    install_date_raw = winreg.QueryValueEx(
                        current_key, "InstallDate"
                    )[0]
                    install_date = format_registry_date(str(install_date_raw))
                except FileNotFoundError:
                    install_date = "Không rõ"

                # Tự động phân tích trạng thái bản quyền và mức độ rủi ro
                license_status, risk_level = analyze_license(
                    display_name, publisher
                )

                software_list.append(
                    {
                        "Software Name": display_name,
                        "Version": display_version,
                        "Publisher": publisher,
                        "Install Date": install_date,
                        "License Status": license_status,
                        "Risk Level": risk_level,
                        "Install Location": install_location,
                        "Architecture": f"{architecture}-bit",
                    }
                )
                winreg.CloseKey(current_key)
            except Exception:
                continue
        winreg.CloseKey(registry_key)
    except Exception as e:
        print(f"Lỗi truy cập Registry: {e}")

    return software_list


def run_audit():
    print("=== ĐANG BẮT ĐẦU QUÉT VÀ PHÂN TÍCH BẢN QUYỀN HỆ THỐNG... ===")

    uninstall_subkey = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
    all_software = []

    all_software.extend(
        get_installed_software(
            winreg.HKEY_LOCAL_MACHINE, uninstall_subkey, architecture=64
        )
    )
    all_software.extend(
        get_installed_software(
            winreg.HKEY_LOCAL_MACHINE, uninstall_subkey, architecture=32
        )
    )
    all_software.extend(
        get_installed_software(
            winreg.HKEY_CURRENT_USER, uninstall_subkey, architecture=64
        )
    )

    # Lọc trùng lặp
    unique_software = {i["Software Name"]: i for i in all_software}.values()

    # Xuất file CSV nâng cấp
    output_file = "SoftwareAuditReport.csv"
    fields = [
        "Software Name",
        "Version",
        "Publisher",
        "Install Date",
        "License Status",
        "Risk Level",
        "Install Location",
        "Architecture",
    ]

    with open(
        output_file, mode="w", encoding="utf-8-sig", newline=""
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(unique_software)

    print(f"\n[THÀNH CÔNG] Đã quét và phân loại xong {len(unique_software)} mục.")
    print(f"Báo cáo chi tiết đã lưu tại: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    run_audit()
