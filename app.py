import datetime
import pandas as pd
import streamlit as st

# 設定頁面與手機 RWD 版面
st.set_page_config(
    page_title="IPQC 智慧巡檢手機 App", page_icon="📱", layout="centered"
)

# 初始化 Session State
if "page" not in st.session_state:
    st.session_state.page = "login"
if "inspection_data" not in st.session_state:
    st.session_state.inspection_data = {}
if "meta" not in st.session_state:
    st.session_state.meta = {}
if "submitted_records" not in st.session_state:
    st.session_state.submitted_records = []
if "daily_history" not in st.session_state:
    # 紀錄格式: { "LOT_日期_項次": data }
    st.session_state.daily_history = {}

# --- 1. 登入與巡檢基本設定頁面 ---
if st.session_state.page == "login":
    st.title("🏭 IPQC 行動巡檢系統")
    st.markdown("### 請設定本次巡檢基本資訊與日期")

    with st.form("login_form"):
        inspector = st.text_input("檢驗人員", value="IPQC-黃紫婷")
        shift = st.selectbox("班別", ["早班", "中班", "夜班"])
        session_time = st.selectbox(
            "巡檢時段", ["上午場 (First Half)", "下午場 (Second Half)"]
        )
        # 登入時即可選擇檢驗日期（支援當日或歷史補登）
        target_date = st.date_input(
            "檢驗日期 (支援補登)", value=datetime.date.today()
        )
        line = st.selectbox("產線", ["AKC"])
        model = st.selectbox("機種", ["BLM243"])
        lot_no = st.text_input("生產批號 / 批量", value="LOT-20261016-01")

        submitted = st.form_submit_button("🚀 進入巡檢主選單")
        if submitted:
            st.session_state.meta = {
                "inspector": inspector,
                "shift": shift,
                "session_time": session_time,
                "inspection_date": target_date,
                "line": line,
                "model": model,
                "lot_no": lot_no,
            }
            st.session_state.inspection_data = {}

            # 載入該批號在該選擇日期的歷史紀錄（支援補登帶入）
            key_prefix = f"{lot_no}_{target_date}"
            for k, v in st.session_state.daily_history.items():
                if k.startswith(key_prefix):
                    item_no = int(k.split("_")[-1])
                    st.session_state.inspection_data[item_no] = v

            st.session_state.page = "dashboard"
            st.rerun()

# --- 2. 主選單儀表板 (支援日期切換與補登) ---
elif st.session_state.page == "dashboard":
    meta = st.session_state.meta
    st.title(f"📋 {meta['line']}產線 - {meta['model']} 巡檢選單")

    # 讓檢驗人員在主畫面也能隨時切換或確認檢驗日期
    selected_date = st.date_input(
        "📅 當前檢驗/補登日期",
        value=meta.get("inspection_date", datetime.date.today()),
        key="dashboard_date_picker",
    )
    # 如果在主畫面切換了日期，同步更新 meta 並重新載入該日期的資料
    if selected_date != meta.get("inspection_date"):
        meta["inspection_date"] = selected_date
        st.session_state.inspection_data = {}
        key_prefix = f"{meta['lot_no']}_{selected_date}"
        for k, v in st.session_state.daily_history.items():
            if k.startswith(key_prefix):
                item_no = int(k.split("_")[-1])
                st.session_state.inspection_data[item_no] = v
        st.rerun()

    st.caption(
        f"人員：{meta['inspector']} | 班別：{meta['shift']} ({meta['session_time']}) | 批號：{meta['lot_no']}"
    )

    # 16項檢驗項目定義 (包含頻率屬性)
    items_def = [
        (1, "厚度", "高度規", "6x 2.18~2.58mm", "numeric", 6, 2.18, 2.58, "every_session"),
        (2, "三相端子點焊脫拔力", "拉力計", "3x 10 Kgf Min", "numeric", 3, 10.0, 999.0, "every_session"),
        (3, "定部扭轉脫拔力", "扭力板手", "20 Nm Min", "numeric", 1, 20.0, 999.0, "once_day"),
        (4, "磁鐵脫拔力", "萬材機", "5 Kgf Min", "numeric", 1, 5.0, 999.0, "once_day"),
        (5, "軸與轉子堆疊角度(第一層)", "投影機", "0°±0.25°", "numeric", 1, -0.25, 0.25, "every_session"),
        (6, "軸與轉子堆疊角度(第二層)", "投影機", "5.5°±0.25°", "numeric", 1, 5.25, 5.75, "every_session"),
        (7, "軸與轉子堆疊角度(第三層)", "投影機", "11°±0.25°", "numeric", 1, 10.75, 11.25, "every_session"),
        (8, "皮帶輪扭轉脫拔力", "扭力板手", "20Nm Min", "numeric", 1, 20.0, 999.0, "once_day"),
        (9, "三相端子高度", "高度規", "3x 24.2~25.2mm", "numeric", 3, 24.2, 25.2, "every_session"),
        (10, "皮帶輪壓入尺寸", "高度規", "24.5±0.3mm", "numeric", 1, 24.2, 24.8, "every_session"),
        (11, "皮帶輪高度", "高度規", "24.5±0.3mm", "numeric", 1, 24.2, 24.8, "every_session"),
        (12, "馬達高度", "高度規", "105.2 ± 0.4mm", "numeric", 1, 104.8, 105.6, "every_session"),
        (13, "位置度", "CMM", "依圖面規範", "numeric", 1, 0.0, 999.0, "once_day"),
        (14, "熱合後本體外徑量測", "游標尺", "63±0.3 mm", "numeric", 1, 62.7, 63.3, "every_session"),
        (15, "標籤確認", "目視檢查", "標籤與外箱相同", "visual", 1, 0, 0, "every_session"),
        (16, "OP5090清潔度檢查", "光學顯微鏡", "SPEC TP401300-B", "visual", 1, 0, 0, "periodic"),
        (17, "OP7035清潔檢查", "光學顯微鏡", "SPEC TA100947", "visual", 1, 0, 0, "periodic"),
        (18, "OP7190清潔檢查", "光學顯微鏡", "SPEC TA100947", "visual", 1, 0, 0, "periodic"),
    ]

    total_items = len(items_def)

    # 初始化防呆
    for no, name, method, spec, itype, pts, min_v, max_v, freq in items_def:
        if no not in st.session_state.inspection_data:
            st.session_state.inspection_data[no] = {
                "status": "未填寫",
                "values": [],
                "remark": "",
            }

    completed_count = sum(
        1
        for v in st.session_state.inspection_data.values()
        if v["status"] in ["OK", "NG"]
    )
    st.progress(
        completed_count / total_items,
        text=f"總進度：已完成 {completed_count} / {total_items} 項",
    )
    st.info(
        "💡 提示：若需補登過去日期的資料，可直接上方調整『檢驗/補登日期』後填寫！"
    )

    for no, name, method, spec, itype, pts, min_v, max_v, freq in items_def:
        status = st.session_state.inspection_data[no]["status"]
        if status == "OK":
            badge = "🟢 OK"
        elif status == "NG":
            badge = "🔴 NG"
        else:
            badge = "⚪ 未填"

        freq_label = {
            "every_session": "🔥 每場必驗",
            "once_day": "⭐ 一天一次",
            "periodic": "🔬 週期補登",
        }.get(freq, "")

        c1, c2, c3 = st.columns([3, 1.5, 1.5])
        with c1:
            st.markdown(f"**{no}. {name}**")
            st.caption(f"{method} | {spec} | [{freq_label}]")
        with c2:
            st.markdown(f"**{badge}**")
        with c3:
            if st.button("填寫", key=f"b_{no}", use_container_width=True):
                st.session_state.current_item = {
                    "no": no,
                    "name": name,
                    "spec": spec,
                    "itype": itype,
                    "pts": pts,
                    "min": min_v,
                    "max": max_v,
                    "freq": freq,
                }
                st.session_state.page = "detail"
                st.rerun()
        st.divider()

    # 送出區
    if completed_count > 0:
        if st.button(
            "🚀 確認送出巡檢紀錄並更新 Raw Data",
            type="primary",
            use_container_width=True,
        ):
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rec_id = (
                f"REC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            target_date_str = str(meta["inspection_date"])

            key_prefix = f"{meta['lot_no']}_{target_date_str}"
            for item_no, data in st.session_state.inspection_data.items():
                if data["status"] in ["OK", "NG"]:
                    # 記錄到當日歷史中（依選擇的補登日期歸檔）
                    st.session_state.daily_history[
                        f"{key_prefix}_{item_no}"
                    ] = data

                    for idx, val in enumerate(data["values"]):
                        st.session_state.submitted_records.append(
                            {
                                "紀錄編號": rec_id,
                                "系統送出時間": current_time,
                                "指定檢驗日期": target_date_str,
                                "檢驗人員": meta["inspector"],
                                "班別": meta["shift"],
                                "時段": meta["session_time"],
                                "產線": meta["line"],
                                "機種": meta["model"],
                                "批號": meta["lot_no"],
                                "項次": item_no,
                                "量測點/型態": f"點 {idx+1}"
                                if isinstance(val, (int, float))
                                else "目視檢查",
                                "實測值/結果": val,
                                "判定結果": data["status"],
                                "異常備註": data["remark"],
                            }
                        )
            st.success(
                f"🎉 【{target_date_str}】的巡檢/補登紀錄已成功儲存並歸檔！"
            )
            st.session_state.page = "export"
            st.rerun()

    if st.button("🔄 重新設定基本資料", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()

# --- 3. 單一項目填寫頁面 ---
elif st.session_state.page == "detail":
    cur = st.session_state.current_item
    st.subheader(f"📝 填寫：項次 {cur['no']} - {cur['name']}")
    st.markdown(f"**規範要求：** `{cur['spec']}`")
    st.divider()

    saved = st.session_state.inspection_data[cur["no"]]

    with st.form("item_form"):
        entered_vals = []
        is_ng = False

        if cur["itype"] == "numeric":
            cols = st.columns(min(cur["pts"], 3))
            for p in range(cur["pts"]):
                with cols[p % 3]:
                    d_val = (
                        saved["values"][p]
                        if len(saved["values"]) == cur["pts"]
                        else float(cur["min"])
                    )
                    v = st.number_input(
                        f"點 {p+1}", value=d_val, step=0.01, key=f"p_{p}"
                    )
                    entered_vals.append(v)
            for v in entered_vals:
                if not (cur["min"] <= v <= cur["max"]):
                    is_ng = True
        else:
            d_choice = saved["values"][0] if saved["values"] else "OK"
            v = st.selectbox(
                "檢查結果",
                ["OK", "NG"],
                index=0 if d_choice == "OK" else 1,
            )
            entered_vals.append(v)
            if v == "NG":
                is_ng = True

        remark = st.text_area("異常備註 (若 NG 請填寫)", value=saved["remark"])

        c_save, c_back = st.columns(2)
        with c_save:
            save_ok = st.form_submit_button(
                "💾 儲存並返回", type="primary", use_container_width=True
            )
        with c_back:
            back_ok = st.form_submit_button(
                "↩️ 取消返回", use_container_width=True
            )

        if save_ok:
            st.session_state.inspection_data[cur["no"]] = {
                "status": "NG" if is_ng else "OK",
                "values": entered_vals,
                "remark": remark,
            }
            st.session_state.page = "dashboard"
            st.rerun()
        if back_ok:
            st.session_state.page = "dashboard"
            st.rerun()

# --- 4. 數據匯出與完成頁面 ---
elif st.session_state.page == "export":
    st.title("📊 Raw Data 檢驗資料庫")
    st.success("巡檢數據已成功匯入結構化 Raw Data！")

    df_res = pd.DataFrame(st.session_state.submitted_records)
    st.dataframe(df_res, use_container_width=True)

    csv_data = df_res.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 下載 Raw Data (CSV 報表)",
        data=csv_data,
        file_name=f"IPQC_RawData_{datetime.date.today()}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button(
        "🔄 開始下一筆新的巡檢任務",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.inspection_data = {}
        st.session_state.page = "login"
        st.rerun()
