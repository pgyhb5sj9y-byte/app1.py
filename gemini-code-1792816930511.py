import streamlit as st
import pandas as pd

st.set_page_config(page_title="TCHP Smart Reefer System", page_icon="🚢", layout="wide")

st.title("🚢 HỆ THỐNG KIỂM SOÁT VÀ ĐỐI CHIẾU CONTAINER LẠNH TỰ ĐỘNG (TCHP)")
st.markdown("---")

# 1. KHỞI TẠO CƠ SỞ DỮ LIỆU ĐỘNG (SESSION STATE)
if 'master_data' not in st.session_state:
    # Dữ liệu mặc định ban đầu
    st.session_state.master_data = pd.DataFrame(
        [
            {"So_Container": "TCNU1234567", "Hang_Tau": "ONE", "Booking": "BK-2026-01", "Nhiet_Do_Chuan": -18.0, "Thong_Gio_Chuan": 0, "Loai_Hang": "Thủy sản"},
            {"So_Container": "MSKU9876543", "Hang_Tau": "Maersk", "Booking": "BK-2026-02", "Nhiet_Do_Chuan": 5.0, "Thong_Gio_Chuan": 15, "Loai_Hang": "Trái cây"}
        ]
    )

# 2. MENU ĐIỀU HƯỚNG
menu = st.sidebar.radio(
    "CHỌN CHỨC NĂNG (GIẢI PHÁP CHƯƠNG 3):", 
    [
        "1. Quản lý Master Data (Hãng Tàu)", 
        "2. Giải pháp 1: Smart Gate (Cổng)", 
        "3. Giải pháp 2: Smart Yard (Bãi)"
    ]
)

# ==========================================
# TAB 1: QUẢN LÝ DỮ LIỆU GỐC TỪ HÃNG TÀU
# ==========================================
if menu == "1. Quản lý Master Data (Hãng Tàu)":
    st.subheader("⚙️ Nhập dữ liệu Booking gốc từ Hãng tàu (Master Data)")
    st.write("Tại đây, bộ phận Thương vụ sẽ upload/nhập dữ liệu chuẩn của hãng tàu cấp. Dữ liệu này dùng để đối chiếu ở Cổng.")
    
    with st.form("add_data_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_cont = st.text_input("Số Container (VD: CMAU1112223)")
            new_line = st.selectbox("Hãng Tàu", ["ONE", "Maersk", "CMA CGM", "MSC", "Evergreen", "ZIM"])
        with col2:
            new_bk = st.text_input("Số Booking")
            new_cargo = st.text_input("Loại hàng hóa")
        with col3:
            new_temp = st.number_input("Nhiệt độ cài đặt chuẩn (°C)", value=0.0, step=0.5)
            new_vent = st.number_input("Thông gió chuẩn (CBM/h)", value=0, step=5)
            
        submit_btn = st.form_submit_button("➕ Thêm vào Cơ sở dữ liệu")
        
        if submit_btn and new_cont:
            # Thêm dòng mới vào dataframe
            new_row = pd.DataFrame([{
                "So_Container": new_cont.upper(), "Hang_Tau": new_line, "Booking": new_bk, 
                "Nhiet_Do_Chuan": new_temp, "Thong_Gio_Chuan": new_vent, "Loai_Hang": new_cargo
            }])
            st.session_state.master_data = pd.concat([st.session_state.master_data, new_row], ignore_index=True)
            st.success(f"Đã thêm Container {new_cont.upper()} thành công!")

    st.markdown("**DỮ LIỆU MASTER DATA HIỆN TẠI TRÊN HỆ THỐNG:**")
    st.dataframe(st.session_state.master_data, use_container_width=True)

# ==========================================
# TAB 2: GIẢI PHÁP 1 - ĐỐI CHIẾU TẠI CỔNG
# ==========================================
elif menu == "2. Giải pháp 1: Smart Gate (Cổng)":
    st.subheader("🚧 Giải pháp 1: Đối chiếu tự động thông tin khai báo tại Cổng (Gate-in)")
    st.info("Mô phỏng: Tài xế đến cổng đọc số Container. Nhân viên nhập lời khai của tài xế vào. Hệ thống sẽ tự tra cứu Master Data để so khớp.")
    
    list_conts = st.session_state.master_data["So_Container"].tolist()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Nhân viên Cổng nhập thông tin Tài xế khai:**")
        check_cont = st.selectbox("Chọn Số Container xe đang chở đến:", list_conts)
        driver_temp = st.number_input("Nhiệt độ Tài xế báo (°C):", value=0.0, step=0.5)
        driver_vent = st.number_input("Thông gió Tài xế báo (CBM/h):", value=0, step=5)
        check_btn = st.button("🔍 ĐỐI CHIẾU & PHÁT HÀNH GATE-PASS", type="primary", use_container_width=True)

    with col2:
        if check_btn:
            # Rút trích dữ liệu chuẩn từ Master Data
            target_data = st.session_state.master_data[st.session_state.master_data["So_Container"] == check_cont].iloc[0]
            
            st.markdown("**Kết quả tra cứu hệ thống:**")
            st.write(f"- Hãng tàu yêu cầu Nhiệt độ: **{target_data['Nhiet_Do_Chuan']}°C**")
            st.write(f"- Hãng tàu yêu cầu Thông gió: **{target_data['Thong_Gio_Chuan']} CBM/h**")
            
            # Logic Đối chiếu
            if driver_temp == target_data['Nhiet_Do_Chuan'] and driver_vent == target_data['Thong_Gio_Chuan']:
                st.success("✅ THÔNG TIN TRÙNG KHỚP. Đã in Gate-Pass. Cho phép xe vào bãi.")
            else:
                st.error("🚨 CẢNH BÁO! THÔNG TIN KHAI BÁO SAI LỆCH VỚI HÃNG TÀU.")
                st.warning("❌ HỆ THỐNG TỪ CHỐI GATE-PASS. Yêu cầu tài xế đỗ xe vào bãi chờ và liên hệ Thương vụ để làm rõ.")

# ==========================================
# TAB 3: GIẢI PHÁP 2 - CẬP NHẬT TẠI BÃI BẰNG TABLET
# ==========================================
elif menu == "3. Giải pháp 2: Smart Yard (Bãi)":
    st.subheader("📱 Giải pháp 2: App Mobile cho Kỹ thuật viên bãi lạnh")
    st.write("Thay vì ghi sổ tay, kỹ thuật viên dùng Tablet tra cứu thẳng vào hệ thống.")
    
    list_conts = st.session_state.master_data["So_Container"].tolist()
    selected_cont_yard = st.selectbox("Chọn Container vừa hạ bãi cần cắm điện:", list_conts)
    
    target_data = st.session_state.master_data[st.session_state.master_data["So_Container"] == selected_cont_yard].iloc[0]
    
    st.info(f"👉 Container {selected_cont_yard} (Hãng {target_data['Hang_Tau']}) - Cần cắm duy trì mức **{target_data['Nhiet_Do_Chuan']}°C**.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        actual_temp = st.number_input("Nhập Nhiệt độ màn hình Cont hiện tại (°C):", value=target_data['Nhiet_Do_Chuan'], step=0.1)
    with col_b:
        status = st.selectbox("Tình trạng Máy lạnh:", ["Máy chạy tốt", "Máy báo lỗi đèn đỏ", "Hư hỏng vỏ/phích cắm"])
        
    if st.button("💾 ĐỒNG BỘ LÊN HỆ THỐNG TOPO"):
        if status == "Máy chạy tốt":
            st.success(f"Đã cập nhật Real-time: Cont {selected_cont_yard} đang chạy với nhiệt độ {actual_temp}°C. Chuyển dữ liệu lên Văn phòng ĐĐHT thành công (Không cần ghi sổ)!")
        else:
            st.error(f"Đã cập nhật sự cố: {status}. Gửi thông báo khẩn đến Trưởng ca trực!")
