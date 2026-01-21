import streamlit as st
from datetime import datetime, date, time, timedelta
import json
import os

st.set_page_config(page_title="ねこスケジュール", layout="centered")

DATA_FILE = "tasks.json"

# =====================
# 保存・読込
# =====================
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "tasks": st.session_state.tasks,
                "points": st.session_state.points,
                "happy_streak": st.session_state.happy_streak,
                "last_happy_day": str(st.session_state.last_happy_day)
            },
            f,
            ensure_ascii=False,
            default=str
        )

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.tasks = data["tasks"]
            st.session_state.points = data["points"]
            st.session_state.happy_streak = data["happy_streak"]
            st.session_state.last_happy_day = (
                date.fromisoformat(data["last_happy_day"])
                if data["last_happy_day"] != "None" else None
            )

# =====================
# 初期化
# =====================
if "tasks" not in st.session_state:
    st.session_state.tasks = []
    st.session_state.points = 100
    st.session_state.happy_streak = 0
    st.session_state.last_happy_day = None
    st.session_state.last_added_task = None
    load_data()

# =====================
# 時刻
# =====================
now = datetime.now()
today = date.today()
current_hour = now.hour

NIGHT_START = 19
NIGHT_END = 22

# =====================
# タイトル
# =====================
st.title("🐱 ねこスケジュール")

# =====================
# タスク追加
# =====================
st.subheader("➕ タスクを追加")

with st.form("add_task"):
    title = st.text_input("タスク名")
    col1, col2 = st.columns(2)

    with col1:
        deadline_date = st.date_input("期限（日付）")
        start_time = st.time_input("開始目安", time(19, 0))

    with col2:
        deadline_time = st.time_input("期限（時間）", time(23, 59))
        planned_minutes = st.number_input("予定作業時間（分）", 5, 600, 30, 5)

    if st.form_submit_button("追加する"):
        if title:
            st.session_state.tasks.append(
                {
                    "id": datetime.now().timestamp(),
                    "title": title,
                    "start_time": start_time.strftime("%H:%M"),
                    "planned_minutes": planned_minutes,
                    "deadline": datetime.combine(deadline_date, deadline_time).isoformat(),
                    "done": False,
                    "log": []
                }
            )
            st.session_state.last_added_task = title
            save_data()
            st.rerun()
        else:
            st.warning("タスク名を入力してね")

# =====================
# タスク分類
# =====================
unfinished = [t for t in st.session_state.tasks if not t["done"]]
unfinished.sort(key=lambda x: x["deadline"])
current_task = unfinished[0] if unfinished else None

# =====================
# 夜通知
# =====================
if NIGHT_START <= current_hour <= NIGHT_END and current_task:
    deadline = datetime.fromisoformat(current_task["deadline"])
    start_time = datetime.strptime(current_task["start_time"], "%H:%M").time()
    start_dt = datetime.combine(today, start_time)
    remaining = int((start_dt - now).total_seconds() // 60)

    face = "😼"
    msg = "今がチャンスにゃ"

    if remaining < 0:
        face = "😰"
        msg = "開始目安すぎてるにゃ…"

    st.markdown(
        f"""
        <div style="background:#f4f4f4;padding:20px;border-radius:16px">
        <h3>🌙 ねこからの通知 {face}</h3>
        <b>{current_task['title']}</b><br>
        ⏳ 今やるまであと {remaining} 分<br><br>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================
# タスク一覧
# =====================
st.divider()
st.subheader("📋 タスク一覧")

for t in st.session_state.tasks:
    deadline = datetime.fromisoformat(t["deadline"])
    status = "✅" if t["done"] else "⚠️" if deadline < now else "⏳"

    highlight = (
        "background:#fff3cd;padding:12px;border-radius:12px;"
        if t["title"] == st.session_state.last_added_task else ""
    )

    with st.container():
        st.markdown(
            f"""
            <div style="{highlight}">
            {status} <b>{t['title']}</b><br>
            ⏰ 開始目安 {t['start_time']} / 📅 {deadline.strftime('%m/%d %H:%M')}
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        # 完了
        with c1:
            if not t["done"] and st.button("☑ 完了", key=f"done_{t['id']}"):
                t["done"] = True
                save_data()
                st.rerun()

        # 編集
        with c2:
            if st.button("✏️ 編集", key=f"edit_{t['id']}"):
                st.session_state.editing = t["id"]

        # 削除
        with c3:
            if st.button("🗑 削除", key=f"del_{t['id']}"):
                st.session_state.tasks.remove(t)
                save_data()
                st.rerun()

        # 編集フォーム
        if st.session_state.get("editing") == t["id"]:
            with st.form(f"edit_form_{t['id']}"):
                new_title = st.text_input("タスク名", t["title"])
                new_minutes = st.number_input(
                    "予定時間", 5, 600, t["planned_minutes"], 5
                )
                if st.form_submit_button("保存"):
                    t["title"] = new_title
                    t["planned_minutes"] = new_minutes
                    st.session_state.editing = None
                    save_data()
                    st.rerun()

# =====================
# ステータス
# =====================
st.divider()
st.subheader("📊 ステータス")
st.write(f"⭐ ポイント：{st.session_state.points}")
st.write(f"😺 ニコニコ連続日数：{st.session_state.happy_streak}")
