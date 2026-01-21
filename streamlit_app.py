import streamlit as st
from datetime import datetime, date, time, timedelta

st.set_page_config(page_title="ねこスケジュール", layout="centered")

# =====================
# 初期化
# =====================
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "points" not in st.session_state:
    st.session_state.points = 100

if "happy_streak" not in st.session_state:
    st.session_state.happy_streak = 0
    st.session_state.last_happy_day = None

if "last_added_task" not in st.session_state:
    st.session_state.last_added_task = None

# =====================
# 時刻
# =====================
now = datetime.now()
today = date.today()
current_time = now.time()
current_hour = now.hour

NIGHT_START = 19
NIGHT_END = 22

# =====================
# タイトル
# =====================
st.title("🐱 ねこスケジュール")

# =====================
# タスク追加フォーム
# =====================
st.subheader("➕ タスクを追加")

with st.form("add_task_form"):
    title = st.text_input("タスク名")

    col1, col2 = st.columns(2)
    with col1:
        deadline_date = st.date_input("期限（日付）")
        start_time = st.time_input("開始目安時刻", time(19, 0))

    with col2:
        deadline_time = st.time_input("期限（時間）", time(23, 59))
        planned_minutes = st.number_input(
            "予定作業時間（分）", min_value=5, step=5, value=30
        )

    submitted = st.form_submit_button("追加する")

    if submitted:
        if title == "":
            st.warning("タスク名を入力してね")
        else:
            deadline = datetime.combine(deadline_date, deadline_time)

            st.session_state.tasks.append(
                {
                    "title": title,
                    "start_time": start_time,
                    "planned_minutes": planned_minutes,
                    "deadline": deadline,
                    "done": False,
                    "log": []
                }
            )
            st.session_state.last_added_task = title
            st.success("タスクを追加したにゃ 🐾")
            st.rerun()

# =====================
# タスク分類
# =====================
unfinished = [t for t in st.session_state.tasks if not t["done"]]
overdue = [t for t in unfinished if t["deadline"] < now]
active = [t for t in unfinished if t["deadline"] >= now]

current_task = active[0] if active else None

# =====================
# ねこ表情 & メッセージ
# =====================
cat_face = "😼"
message = "今日は何をやるにゃ？"

if st.session_state.last_added_task:
    message = f"「{st.session_state.last_added_task}」を追加したにゃ！"

if overdue:
    cat_face = "😰"
    message = "期限を過ぎた課題があるにゃ…"

if current_task and current_time > current_task["start_time"]:
    cat_face = "😰"
    message = "そろそろ始めたいにゃ"

if not unfinished and st.session_state.tasks:
    cat_face = "😺"
    message = "全部終わったにゃ！"
    if st.session_state.last_happy_day != today:
        st.session_state.happy_streak += 1
        st.session_state.last_happy_day = today

# =====================
# 夜の通知UI（最優先）
# =====================
if NIGHT_START <= current_hour <= NIGHT_END and current_task:
    with st.container():
        st.markdown(
            """
            <div style="
                background:#f4f4f4;
                padding:20px;
                border-radius:18px;
                box-shadow:0 4px 8px rgba(0,0,0,0.08);
            ">
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"### 🌙 ねこからの通知 {cat_face}")
        st.write(message)

        st.write(
            f"**今やるタスク**：{current_task['title']}  \n"
            f"⏰ 開始目安：{current_task['start_time'].strftime('%H:%M')}  \n"
            f"🧩 予定時間：{current_task['planned_minutes']}分"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("▶ 今からやる"):
                current_task["log"].append({"start": datetime.now()})
                st.success("作業スタート！")

        with col2:
            if st.button("☑ 終わった"):
                end = datetime.now()
                log = current_task["log"][-1]
                log["end"] = end
                spent = int((end - log["start"]).total_seconds() / 60)
                log["minutes"] = spent

                if spent > current_task["planned_minutes"]:
                    st.session_state.points -= 10

                current_task["done"] = True
                st.success("お疲れさま！")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# =====================
# タスク一覧（追加後に分かりやすい）
# =====================
st.divider()
st.subheader("📋 タスク一覧")

for t in st.session_state.tasks:
    if t["done"]:
        status = "✅"
    elif t["deadline"] < now:
        status = "⚠️"
    else:
        status = "⏳"

    highlight = ""
    if t["title"] == st.session_state.last_added_task:
        highlight = "background-color:#fff3cd; padding:12px; border-radius:12px;"

    st.markdown(
        f"""
        <div style="{highlight}">
        {status} <strong>{t['title']}</strong><br>
        ⏰ 開始目安：{t['start_time'].strftime('%H:%M')}<br>
        📅 期限：{t['deadline'].strftime('%m/%d %H:%M')}<br>
        🧩 予定時間：{t['planned_minutes']}分
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================
# ステータス
# =====================
st.divider()
st.subheader("📊 ステータス")
st.write(f"⭐ ポイント：{st.session_state.points}")
st.write(f"😺 ニコニコ連続日数：{st.session_state.happy_streak}")

# =====================
# 実績ログ
# =====================
st.subheader("📝 実績ログ")

for t in st.session_state.tasks:
    st.write(f"### {t['title']}")
    for log in t["log"]:
        if "end" in log:
            st.write(
                f"- {log['start'].strftime('%H:%M')}〜"
                f"{log['end'].strftime('%H:%M')}（{log['minutes']}分）"
            )
