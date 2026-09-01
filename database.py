# -*- coding: utf-8 -*-
"""
database.py - 專責 Supabase (PostgreSQL) CRUD 與衝突檢測
"""

import os
import re
import pandas as pd
from typing import List, Dict, Tuple
from supabase import create_client, Client
from postgrest.exceptions import APIError

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL 及 Key 未設定，請配置環境變數。")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_worker_names(input_val) -> List[str]:
    """解析以中英文逗號或頓號分隔的同工姓名，並去除空白與空值"""
    if isinstance(input_val, list):
        return [str(x).strip() for x in input_val if str(x).strip()]
    if not input_val:
        return []
    names = re.split(r'[,，、]', str(input_val))
    return [name.strip() for name in names if name.strip()]

def get_active_worker_names() -> List[str]:
    """取得目前系統中狀態為啟用 (Active) 的同工姓名列表"""
    try:
        supabase = get_client()
        res = supabase.table("workers").select("name").eq("status", "Active").execute()
        if res.data:
            return [w["name"] for w in res.data if w.get("name")]
        return []
    except Exception:
        return []

# ── 模組 A：恩典紀錄 ──
def save_grace_record(date_str: str, time_slot: str, worker_name: str, gift: str, reflection: str, prayer: str) -> bool:
    try:
        supabase = get_client()
        data = {
            "event_date": date_str,
            "time_slot": time_slot,
            "worker_name": worker_name,
            "gift_item": gift,
            "reflection": reflection,
            "prayer_item": prayer
        }
        res = supabase.table("grace_records").insert(data).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"[Error save_grace_record]: {e}")
        return False

# ── 模組 B：場地防撞檢查與儲存 ──
def check_venue_conflict(date_str: str, time_slot: str, venue: str) -> Tuple[bool, List[Dict]]:
    """檢查場地在相同日期與時段是否已被預約"""
    try:
        supabase = get_client()
        res = supabase.table("venue_bookings") \
            .select("*") \
            .eq("event_date", date_str) \
            .eq("time_slot", time_slot) \
            .eq("venue_name", venue) \
            .execute()
        has_conflict = len(res.data) > 0
        return has_conflict, res.data
    except Exception as e:
        print(f"[Error check_venue_conflict]: {e}")
        return False, []

def save_venue_booking(date_str: str, time_slot: str, venue: str, applicant: str, purpose: str) -> bool:
    try:
        supabase = get_client()
        data = {
            "event_date": date_str,
            "time_slot": time_slot,
            "venue_name": venue,
            "applicant": applicant,
            "purpose": purpose
        }
        res = supabase.table("venue_bookings").insert(data).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"[Error save_venue_booking]: {e}")
        return False

# ── 模組 C：排班重複檢查與儲存 ──
def check_roster_conflict(date_str: str, time_slot: str, current_roles: Dict[str, any]) -> Tuple[bool, List[str]]:
    """
    檢查：
    1. 表單內部是否有同一同工兼任多職
    2. 雲端資料庫同日同場次是否已有該同工的事奉排班
    """
    warnings = []
    role_mapping = {}
    all_workers = []

    for role, value in current_roles.items():
        parsed = parse_worker_names(value)
        for name in parsed:
            if name in role_mapping:
                warnings.append(f"同工【{name}】在本次排班中同時擔任「{role_mapping[name]}」與「{role}」")
            else:
                role_mapping[name] = role
            all_workers.append(name)

    if all_workers:
        try:
            supabase = get_client()
            res = supabase.table("roster_records") \
                .select("roles_data") \
                .eq("event_date", date_str) \
                .eq("time_slot", time_slot) \
                .execute()
            
            for record in res.data:
                existing_roles = record.get("roles_data", {})
                for role, names_val in existing_roles.items():
                    existing_names = parse_worker_names(names_val)
                    for w in set(all_workers):
                        if w in existing_names:
                            warnings.append(f"同工【{w}】在資料庫同日同場次已有排班記錄（崗位：{role}）")
        except Exception as e:
            print(f"[Error check_roster_conflict]: {e}")

    return len(warnings) > 0, warnings

def save_roster_record(date_str: str, time_slot: str, roles_data: Dict[str, any]) -> bool:
    try:
        supabase = get_client()
        data = {
            "event_date": date_str,
            "time_slot": time_slot,
            "roles_data": roles_data
        }
        res = supabase.table("roster_records").insert(data).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"[Error save_roster_record]: {e}")
        return False

# ── 模組 D：全欄位關鍵字查詢 ──
def query_records(table_name: str, keyword: str = "", start_date: str = None, end_date: str = None) -> pd.DataFrame:
    try:
        supabase = get_client()
        query = supabase.table(table_name).select("*")
        
        if start_date:
            query = query.gte("event_date", start_date)
        if end_date:
            query = query.lte("event_date", end_date)
            
        res = query.execute()
        df = pd.DataFrame(res.data)
        
        if df.empty:
            return pd.DataFrame()
        
        if keyword and keyword.strip():
            kw = keyword.strip().lower()
            mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(kw, regex=False).any(), axis=1)
            df = df[mask]
            
        return df
    except APIError as e:
        print(f"[Supabase APIError]: {e}")
        return pd.DataFrame({"error": [f"資料庫查詢失敗 (APIError)：請檢查 Supabase 是否已建立【{table_name}】資料表或開放 RLS 存取權限。"]})
    except Exception as e:
        print(f"[Unexpected Error]: {e}")
        return pd.DataFrame({"error": [f"系統發生未預期錯誤：{str(e)}"]})
