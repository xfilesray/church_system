# -*- coding: utf-8 -*-
"""
constants.py - 集中管理繁體中文 UI 標籤、對照表與預設選項
"""

APP_TITLE = "⛪ 教會事奉管理與恩典紀錄系統"
APP_SUBTITLE = "專為教會同工與團隊設計的一站式事奉排班、場地借用與恩典紀錄平台"

TIME_SLOT_OPTIONS = [
    "早堂 (08:00 - 10:00)",
    "主日堂 (10:00 - 12:00)",
    "午堂 (14:00 - 16:00)",
    "晚堂 (19:00 - 21:00)",
    "其他 / 請自行於下方輸入"
]

GRACE_GIFTS_OPTIONS = [
    "講道 / 分享",
    "敬拜讚美 / 樂手",
    "關懷代禱",
    "影音 / 音控 / 直播",
    "行政協調 / 總務",
    "兒童主日學 / 青少年",
    "招待 / 迎賓",
    "其他 / 請自行於下方輸入"
]

VENUE_OPTIONS = [
    "大堂 (Main Sanctuary)",
    "副堂 (Side Chapel)",
    "101 教室",
    "102 教室",
    "舞蹈 / 小組室",
    "其他 / 請自行於下方輸入"
]

LABELS = {
    # ── 共用日期與時段區塊標籤 ──
    "date_section": "📅 請選擇活動 / 事奉時間 (Shared Date & Time)",
    "select_date": "選擇日期",
    "select_time": "選擇時段",
    "custom_time": "請輸入自訂時段",

    # ── 主選單 Tab 標籤 ──
    "tab_grace": "📖 恩典與體會紀錄",
    "tab_venue": "🏠 場地借用",
    "tab_roster": "📅 事奉排班時間表",
    "tab_search": "🔍 查詢紀錄與管理",
    
    # ── Tab 1: 恩賜與體會 ──
    "grace_header": "📖 紀錄事奉恩賜與心得日記",
    "worker_name": "同工姓名",
    "gifts_select": "事奉恩賜 / 服侍項目",
    "custom_gift": "請輸入自訂恩賜/項目",
    "reflection": "恩典體會與心得紀錄",
    "prayer": "代禱事項",
    "btn_save_grace": "儲存恩賜紀錄",
    
    # ── Tab 2: 場地借用 ──
    "venue_header": "🏠 教會房間 / 場地借用申請",
    "venue_select": "選擇借用場地 / 房間",
    "custom_venue": "請輸入自訂場地名稱",
    "applicant": "申請人 / 單位聯絡人",
    "purpose": "事工 / 聚會用途",
    "force_save_venue": "⚠️ 若有場地撞期，仍強制儲存 (Force Save)",
    "btn_save_venue": "提交場地借用申請",
    
    # ── Tab 3: 排班時間表 ──
    "roster_header": "📅 未來事奉時間表 (團隊排班)",
    "worship_lead": "敬拜主領",
    "speaker": "講員 / 證道",
    "av_team": "音控 / 直播同工",
    "usher_team": "招待 / 迎賓同工",
    "sunday_school": "主日學老師",
    "other_roles": "其他事奉同工",
    "roster_select_hint": "💡 請從下拉選單選擇同工（可多選），若不在名單中可於下方手動補充",
    "unselected_placeholder": "請選擇同工...",
    "force_save_roster": "⚠️ 若有重複排班警示，仍強制儲存 (Force Save)",
    "btn_save_roster": "發布事奉時間表",

    # ── Tab 4: 查詢與同工管理 ──
    "search_header": "🔍 紀錄查詢與系統管理",
    "subtab_query": "🔍 紀錄查詢",
    "subtab_worker_mgmt": "👥 同工名單管理",
    "select_module": "選擇查詢模組",
    "search_keyword": "關鍵字搜尋 (支援姓名、內容、用途等)",
    "date_range": "日期區間篩選",
    "btn_search": "執行查詢",
    "no_data_found": "查無符合條件的紀錄。",
    "export_csv": "📥 下載查詢結果 (CSV)",
    "add_worker_header": "➕ 新增同工",
    "worker_name_input": "同工姓名",
    "worker_role_select": "主要事奉領域",
    "btn_add_worker": "新增同工",
    "worker_mgmt_header": "👥 同工名單與狀態維護",
    "btn_update_status": "更新狀態",
    "btn_delete_worker": "刪除同工",
    "msg_worker_updated": "已更新同工狀態！",
    "msg_worker_deleted": "已成功刪除同工！",
    "confirm_delete_worker": "確定要永久刪除此同工嗎？"
}
