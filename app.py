# -*- coding: utf-8 -*-
"""
app.py - 主應用程式 (維持純英文變數，解耦 UI 標籤與資料庫邏輯)
"""

import datetime
import streamlit as st
import constants as c
import database as db

st.set_page_config(page_title=c.APP_TITLE, page_icon="⛪", layout="wide")

st.title(c.APP_TITLE)
st.caption(c.APP_SUBTITLE)

# ── 1. 動態載入後台自訂選單選項 ──
time_slot_options = db.get_setting_options("TIME_SLOT_OPTIONS")
grace_gifts_options = db.get_setting_options("GRACE_GIFTS_OPTIONS")
venue_options = db.get_setting_options("VENUE_OPTIONS")
roster_roles_options = db.get_setting_options("ROSTER_ROLES_OPTIONS")

# ── 2. 共用時段與日期選擇區塊 ──
st.subheader(c.LABELS["date_section"])
col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input(c.LABELS["select_date"], value=datetime.date.today(), key="main_date_input")
    date_str = selected_date.strftime("%Y-%m-%d")

with col_time:
    selected_time_option = st.selectbox(c.LABELS["select_time"], time_slot_options, key="main_time_select")
    if selected_time_option == "其他 / 請自行於下方輸入" or (time_slot_options and selected_time_option == time_slot_options[-1]):
        selected_time = st.text_input(c.LABELS["custom_time"], value="", key="main_custom_time")
    else:
        selected_time = selected_time_option

# ── 3. 主選單 5 個 Tabs 宣告 ──
tab_grace, tab_venue, tab_roster, tab_search, tab_admin = st.tabs([
    c.LABELS["tab_grace"],
    c.LABELS["tab_venue"],
    c.LABELS["tab_roster"],
    c.LABELS["tab_search"],
    "⚙️ 後台設定"
])

# ── 模組 A (📖 恩典與體會紀錄) ──
with tab_grace:
    st.header(c.LABELS["grace_header"])
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        worker_name = st.text_input(c.LABELS["worker_name"], key="grace_worker_name")
        gift_option = st.selectbox(c.LABELS["gifts_select"], grace_gifts_options, key="grace_gift_select")
        gift_val = st.text_input(c.LABELS["custom_gift"], key="grace_custom_gift") if (grace_gifts_options and gift_option == grace_gifts_options[-1]) else gift_option
    
    with col_a2:
        reflection = st.text_area(c.LABELS["reflection"], height=100, key="grace_reflection")
        prayer = st.text_area(c.LABELS["prayer"], height=80, key="grace_prayer")
        
    if st.button(c.LABELS["btn_save_grace"], type="primary", key="btn_save_grace"):
        if not worker_name.strip():
            st.warning("請填寫同工姓名！")
        else:
            success = db.save_grace_record(date_str, selected_time, worker_name, gift_val, reflection, prayer)
            if success:
                st.success("恩典紀錄儲存成功！")
            else:
                st.error("儲存失敗，請檢查資料庫連線。")

# ── 模組 B (🏠 場地借用與防撞檢查) ──
with tab_venue:
    st.header(c.LABELS["venue_header"])
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        venue_option = st.selectbox(c.LABELS["venue_select"], venue_options, key="venue_select")
        venue_val = st.text_input(c.LABELS["custom_venue"], key="venue_custom_text") if (venue_options and venue_option == venue_options[-1]) else venue_option
        applicant = st.text_input(c.LABELS["applicant"], key="venue_applicant")
    
    with col_b2:
        purpose = st.text_area(c.LABELS["purpose"], height=100, key="venue_purpose")
        force_save_venue = st.checkbox(c.LABELS["force_save_venue"], key="venue_force_save")
        
    if st.button(c.LABELS["btn_save_venue"], type="primary", key="btn_save_venue"):
        if not venue_val.strip() or not applicant.strip():
            st.warning("請填寫完整的場地與申請人資訊！")
        else:
            has_conflict, conflicts = db.check_venue_conflict(date_str, selected_time, venue_val)
            if has_conflict and not force_save_venue:
                st.error(f"⚠️ 場地衝突！【{venue_val}】於 {date_str} {selected_time} 已被【{conflicts[0].get('applicant')}】預約。")
                st.info("如確定要聯合使用場地，請勾選「強制儲存 (Force Save)」後再點擊提交。")
            else:
                success = db.save_venue_booking(date_str, selected_time, venue_val, applicant, purpose)
                if success:
                    st.success("場地預約申請提交成功！")
                else:
                    st.error("預約提交失敗，請檢查資料庫連線。")

# ── 模組 C (📅 事奉排班時間表 - 動態渲染版) ──
with tab_roster:
    st.header(c.LABELS["roster_header"])
    st.caption(c.LABELS["roster_select_hint"])
    
    roles_data = {}
    col_c1, col_c2 = st.columns(2)
    
    mid_index = (len(roster_roles_options) + 1) // 2
    left_roles = roster_roles_options[:mid_index]
    right_roles = roster_roles_options[mid_index:]

    with col_c1:
        for idx, r_name in enumerate(left_roles):
            # 加入 idx 避免相同名稱導致 key 碰撞
            roles_data[r_name] = st.text_input(f"{r_name} 同工", key=f"roster_left_{idx}_{r_name}")

    with col_c2:
        for idx, r_name in enumerate(right_roles):
            roles_data[r_name] = st.text_input(f"{r_name} 同工", key=f"roster_right_{idx}_{r_name}")

    force_save_roster = st.checkbox(c.LABELS["force_save_roster"], key="roster_force_save")

    if st.button(c.LABELS["btn_save_roster"], type="primary", key="btn_save_roster"):
        has_conflict, warnings = db.check_roster_conflict(date_str, selected_time, roles_data)
        
        if has_conflict and not force_save_roster:
            st.warning("⚠️ 偵測到重複排班預警：")
            for w in warnings:
                st.write(f"- {w}")
            st.info("如為一人兼任多職或聯合聚會，請勾選「強制儲存 (Force Save)」後再點擊發布。")
        else:
            save_payload = {k: v for k, v in roles_data.items() if v.strip()}
            success = db.save_roster_record(date_str, selected_time, save_payload)
            if success:
                st.success("🎉 事奉時間表已成功發布！")
            else:
                st.error("發布失敗，請檢查資料庫連線。")

# ── 模組 D (🔍 全欄位查詢版面 - 精簡版) ──
with tab_search:
    st.header(c.LABELS["search_header"])
    
    col_q1, col_q2, col_q3 = st.columns([2, 3, 3])
    with col_q1:
        module_choice = st.selectbox(
            c.LABELS["select_module"], 
            ["恩典紀錄", "場地借用", "事奉排班"], 
            key="search_module_choice"
        )
    with col_q2:
        search_kw = st.text_input(c.LABELS["search_keyword"], key="search_keyword_input")
    with col_q3:
        date_range = st.date_input(
            c.LABELS["date_range"], 
            value=(datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()),
            key="search_date_range"
        )
        
    if st.button(c.LABELS["btn_search"], key="btn_execute_search", type="primary"):
        table_map = {
            "恩典紀錄": "grace_records",
            "場地借用": "venue_bookings",
            "事奉排班": "roster_records"
        }
        start_d = date_range[0].strftime("%Y-%m-%d") if len(date_range) > 0 else None
        end_d = date_range[1].strftime("%Y-%m-%d") if len(date_range) > 1 else None
        
        target_table = table_map.get(module_choice, "grace_records")
        df_result = db.query_records(target_table, keyword=search_kw, start_date=start_d, end_date=end_d)
        
        if "error" in df_result.columns:
            st.error(df_result["error"].iloc[0])
        elif df_result.empty:
            st.info(c.LABELS["no_data_found"])
        else:
            st.dataframe(df_result, use_container_width=True)
            csv = df_result.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                c.LABELS["export_csv"], 
                data=csv, 
                file_name=f"{module_choice}_export.csv", 
                mime="text/csv", 
                key="btn_download_csv"
            )


# ── 模組 E (⚙️ 後台管理與系統設定板面 - 整合同工名單管理) ──
with tab_admin:
    st.header("⚙️ 系統設定與維護板面")
    st.info("您可以在此維護全系統的選單選項，以及管理教會同工基本名單。")

    admin_target = st.selectbox(
        "請選擇欲管理的項目",
        ["選擇時段", "事奉恩賜 / 服侍項目", "選擇借用場地 / 房間", "事奉排班崗位 / 項目", "👥 教會同工名單維護"],
        key="admin_target_select"
    )

    mapping_keys = {
        "選擇時段": "TIME_SLOT_OPTIONS",
        "事奉恩賜 / 服侍項目": "GRACE_GIFTS_OPTIONS",
        "選擇借用場地 / 房間": "VENUE_OPTIONS",
        "事奉排班崗位 / 項目": "ROSTER_ROLES_OPTIONS"
    }

    # ──── 分支 A：處理 4 大選單選項文字編輯 ────
    if admin_target in mapping_keys:
        current_key = mapping_keys[admin_target]
        current_list = db.get_setting_options(current_key)

        st.markdown("---")
        st.subheader(f"🛠️ 正在編輯：【{admin_target}】")

        raw_text = st.text_area(
            "選項清單（每行代表一個選項）：",
            value="\n".join(current_list),
            height=220,
            help="請逐行輸入您要顯示於選單中的名稱。",
            key=f"admin_raw_text_{current_key}"
        )

        col_btn1, col_btn2 = st.columns([2, 4])
        with col_btn1:
            if st.button("💾 儲存修改內容", type="primary", key=f"btn_save_admin_{current_key}"):
                new_options = [line.strip() for line in raw_text.split("\n") if line.strip()]
                if db.update_setting_options(current_key, new_options):
                    st.success(f"✅ 【{admin_target}】選項已成功更新！")
                    st.rerun()
                else:
                    st.error("儲存失敗，請檢查資料庫權限或連線。")

        with col_btn2:
            if st.button("🔄 重置所有選項為系統預設值", key=f"btn_reset_admin_{current_key}"):
                if db.reset_all_settings_to_default():
                    st.success("已恢復預設設定！")
                    st.rerun()

    # ──── 分支 B：處理 同工名單 CRUD 管理 ────
    elif admin_target == "👥 教會同工名單維護":
        st.markdown("---")
        st.subheader("👥 教會同工名單維護區塊")

        # 子頁籤：檢視/刪除 與 新增同工
        subtab_list, subtab_add = st.tabs(["📋 目前同工名單", "➕ 新增同工資料"])

        with subtab_list:
            workers_data = db.get_all_workers()
            if not workers_data:
                st.info("目前尚無同工資料，請至「新增同工資料」頁籤進行建立。")
            else:
                import pandas as pd
                df_workers = pd.DataFrame(workers_data)
                
                # 重新整理欄位顯示順序與欄位名稱
                column_rename = {
                    "id": "ID",
                    "name": "同工姓名",
                    "department": "所屬部門/小組",
                    "role": "主要事奉崗位",
                    "phone": "聯絡電話",
                    "email": "電子郵件"
                }
                df_display = df_workers.rename(columns=column_rename)
                st.dataframe(df_display, use_container_width=True)

                # 刪除同工功能
                st.markdown("##### 🗑️ 刪除同工資料")
                col_del1, col_del2 = st.columns([3, 1])
                with col_del1:
                    worker_to_delete = st.selectbox(
                        "選擇要刪除的同工：",
                        options=workers_data,
                        format_func=lambda w: f"ID: {w['id']} | {w['name']} ({w.get('department', '無部門')})",
                        key="sb_delete_worker"
                    )
                with col_del2:
                    st.write("") # 垂直對齊置中
                    st.write("")
                    if st.button("確認刪除", key="btn_delete_worker", type="secondary"):
                        if worker_to_delete:
                            if db.delete_worker(worker_to_delete["id"]):
                                st.success(f"已成功刪除同工：{worker_to_delete['name']}")
                                st.rerun()
                            else:
                                st.error("刪除失敗，請檢查資料庫連線。")

        with subtab_add:
            st.markdown("##### ➕ 新增同工基本資料")
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                new_w_name = st.text_input("同工姓名 *", key="add_w_name")
                new_w_dept = st.text_input("所屬部門 / 小組 (選填)", key="add_w_dept")
                new_w_role = st.text_input("主要事奉崗位 (選填)", key="add_w_role")
            with col_w2:
                new_w_phone = st.text_input("聯絡電話 (選填)", key="add_w_phone")
                new_w_email = st.text_input("電子郵件 (選填)", key="add_w_email")

            if st.button("💾 儲存同工資料", type="primary", key="btn_save_new_worker"):
                if not new_w_name.strip():
                    st.warning("⚠️ 請務必填寫「同工姓名」！")
                else:
                    if db.add_worker(new_w_name, new_w_dept, new_w_role, new_w_phone, new_w_email):
                        st.success(f"🎉 同工【{new_w_name}】資料已成功新增！")
                        st.rerun()
                    else:
                        st.error("新增失敗，請檢查資料庫連線或 Supabase `workers` 表結構。")
