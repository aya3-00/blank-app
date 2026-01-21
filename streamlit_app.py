import streamlit as st
from datetime import datetime, date, time, timedelta
import json
import os
import pandas as pd
import numpy as np

# =====================
# 基本設定
# =====================
st.set_page_config(page_title="ねこスケジュール", layout="centered")

DATA_FILE = "tasks.json"

# =====================
# 保存・読込
# =====================
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, ensure_ascii=False, default=str)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                st.session_state.tasks = json.load(f)
            except:
                st.session_state.tasks = []

# =====================
# AI作業時間予測
# =====================
def predict_minutes(title, planned):
    logs = []

    for t in st.session_state.tasks:
        if t.get("title") == title:
            for log in t.get("log", []):
                if "minutes" in log:
                    logs.append(log["minutes"])

    if len(logs) >= 3:
        return int(np.mean(logs))
    else:
        return int(planned * 1.2)

# =====================
# 初期化
# =====================
if "tasks" not in st.session_state:
    st.session_state.tasks = []
    load_data()

# =====================
# 現在時刻
# =====================
now = datetime.now()
today = date.today()

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
        deadline_date = st.date_input("期限（日付）", today)
        start_time = st.time_input("開始目安", time(19, 0))

    with col2:
        deadline_time = st.time_input("期限（時間）", time(23, 59))
        planned = st.number_input("予定作業時間（分）", 5, 600, 30, 5)

    if st.form_submit_button("追加する") and title:
        predicted = predict_minutes(title, planned)

        st.session_state.tasks.append(
            {
                "id": datetime.now().timestamp(),
                "title": title,
                "start_time": start_time.strftime("%H:%M"),
                "planned": planned,
                "predicted": predicted,
                "deadline": datetime.combine(
                    deadline_date, deadline_time
                ).isoformat(),
                "done": False,
                "log": []
            }
        )
        save_data()
        st.success(f"🧠 AI予測：{predicted}分くらいにゃ！")
        st.rerun()

# =====================
# タスク一覧
# =====================
st.divider()
st.subheader("📋 タスク一覧")

if not st.session_state.tasks:
    st.info("まだタスクがないにゃ 🐾")

for i, t in enumerate(st.session_state.tasks):
    try:
        deadline = datetime.fromisoformat(str(t.get("deadline")))
    except:
        continue

    start_dt = datetime.combine(
        today,
        datetime.strptime(t.get("start_time", "00:00"), "%H:%M").time()
    )

    remaining = int((start_dt - now).total_seconds() // 60)

    if t.get("done"):
        status = "✅"
    elif deadline < now:
        status = "🔥"
    else:
        status = "⏳"

    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(
            f"""
            <div style="background:#f4f4f4;padding:12px;border-radius:12px">
            {status} <b>{t['title']}</b><br>
            ⏰ 開始目安：{t['start_time']}（あと {remaining} 分）<br>
            🧠 AI予測：{t['predicted']}分 / 🧩 予定：{t['planned']}分<br>
            📅 期限：{deadline.strftime('%m/%d %H:%M')}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        if st.button("🗑", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            save_data()
            st.rerun()

# =====================
# カレンダー表示
# =====================
st.divider()
st.subheader("📅 1週間カレンダー")

dates = [today + timedelta(days=i) for i in range(7)]
calendar = {d.strftime("%m/%d"): [] for d in dates}

for t in st.session_state.tasks:
    try:
        d = datetime.fromisoformat(str(t.get("deadline"))).date()
        if d in dates:
            calendar[d.strftime("%m/%d")].append(t["title"])
    except:
        pass

df = pd.DataFrame(
    {day: [" / ".join(tasks)] for day, tasks in calendar.items()}
)

st.dataframe(df, use_container_width=True)
