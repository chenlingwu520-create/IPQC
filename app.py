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

# --- 1. 登入與巡檢基本設定頁面 ---
if st.session_state.page == "login":
    st.title("🏭 IPQC 行動巡檢系統")
    st.markdown("### 請設定本次檢驗基本資訊")

    with st.form("login_form"):
        inspector = st.text_input("檢驗人員", value="")
        shift = st.selectbox("班別", ["早班", "中班", "夜班"])
        line = st.selectbox("產線", ["AKC"])
        model = st.selectbox("機種", ["BLM243"])
        lot_no = st.text_input("生產批號 / 批量", value="LOT-20261016-01")

        submitted = st.form_submit_button("🚀 進入 16 項巡檢主選單")
        if submitted:
            st.session_state.meta = {
                "inspector": inspector,
                "shift": shift,
                "line": line,
                "model": model,
                "lot_no": lot_no,
            }
            # 初始化 16 個項目狀態
            for i in range(1, 17):
                if i not in st.session_state.inspection_data:
                    st.session_state.inspection_data[i] = {
                        "status": "未填寫",
                        "values": [],
                        "remark": "",
                    }
            st.session_state.page = "dashboard"
            st.rerun()

# --- 2. 主選單儀表板 (16項清單，隨點隨填，不卡關) ---
elif st.session_state.page == "dashboard":
    meta = st.session_state.meta
    st.title(f"📋 {meta['line']}產線 - {meta['model']} 巡檢選單")
    st.caption(
        f"人員：{meta['inspector']} | 班別：{meta['shift']} | 批號：{meta['lot_no']}"
    )

    # 計算完成進度
    completed_count = sum(
        1
        for v in st.session_state.inspection_data.values()
        if v["status"] in ["OK", "NG"]
    )
    st.progress(
        completed_count / 16,
        text=f"總進度：已完成 {completed_count} / 16 項",
    )
    st.info(
        "💡 提示：您可以依照個人習慣自由點選下方項目填寫，隨時可返回或修改。"
    )

    # 16項檢驗項目完整定義
    items_def = [
        (1, "厚度", "高度規", "6x 2.18~2.58mm", "numeric", 6, 2.18, 2.58),
        (
            2,
            "三相端子點焊脫拔力",
            "拉力計",
            "3x 10 Kgf Min",
            "numeric",
            3,
            10.0,
            999.0,
        ),
        (3, "定部扭轉脫拔力", "扭力板手", "20 Nm Min", "numeric", 1, 20.0, 999.0),
        (4, "磁鐵脫拔力", "萬材機", "5 Kgf Min", "numeric", 1, 5.0, 999.0),
        (5, "軸與轉子堆疊角度(第一層)", "投影機", "0°±0.25°", "numeric", 1, -0.25, 0.25),
        (5.1, "軸與轉子堆疊角度(第二層)", "投影機", "5.5°±0.25°", "numeric", 1, 5.25, 5.75),
        (5.2, "軸與轉子堆疊角度(第三層)", "投影機", "11°±0.25°", "numeric", 1, 10.75, 11.25),
        (6, "皮帶輪扭轉脫拔力", "扭力板手", "20Nm Min", "numeric", 1, 20.0, 999.0),
        (7, "三相端子高度", "高度規", "3x 24.2~25.2mm", "numeric", 3, 24.2, 25.2),
        (8, "皮帶輪壓入尺寸", "高度規", "24.5±0.3mm", "numeric", 1, 24.2, 24.8),
        (9, "皮帶輪高度", "高度規", "24.5±0.3mm", "numeric", 1, 24.2, 24.8),
        (10, "馬達高度", "高度規", "105.2 ± 0.4mm", "numeric", 1, 104.8, 105.6),
        (11, "位置度", "CMM", "依圖面規範", "numeric", 1, 0.0, 999.0),
        (12, "熱合後本體外徑量測", "游標尺", "63±0.3 mm", "numeric", 1, 62.7, 63.3),
        (13, "標籤確認", "目視檢查", "標籤與外箱相同", "visual", 1, 0, 0),
        (14, "OP5090清潔度檢查", "光學顯微鏡", "SPEC TP401300-B", "visual", 1, 0, 0),
        (15, "OP7035清潔檢查", "光學顯微鏡", "SPEC TA100947", "visual", 1, 0, 0),
        (16, "OP7190清潔檢查", "光學顯微鏡", "SPEC TA100947", "visual", 1, 0, 0),
    ]

    for no, name, method, spec, itype, pts, min_v, max_v in items_def:
        status = st.session_state.inspection_data[no]["status"]
        if status == "OK":
            badge = "🟢 OK"
        elif status == "NG":
            badge = "🔴 NG"
        else:
            badge = "⚪ 未填"

        c1, c2, c3 = st.columns([3, 1.5, 1.5])
        with c1:
            st.markdown(f"**{no}. {name}**")
            st.caption(f"{method} | {spec}")
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
                }
                st.session_state.page = "detail"
                st.rerun()
        st.divider()

    # 底部送出區
    if completed_count == 16:
        if st.button(
            "🚀 16項全部完成，正式送出並產生 Raw Data",
            type="primary",
            use_container_width=True,
        ):
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rec_id = (
                f"REC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            )

            for item_no, data in st.session_state.inspection_data.items():
                for idx, val in enumerate(data["values"]):
                    st.session_state.submitted_records.append(
                        {
                            "紀錄編號": rec_id,
                            "檢驗時間": current_time,
                            "檢驗人員": meta["inspector"],
                            "班別": meta["shift"],
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
            st.success("🎉 檢驗紀錄已成功儲存！")
            st.session_state.page = "export"
            st.rerun()
    else:
        st.warning(
            f"⚠️ 還有 {16 - completed_count} 項尚未填寫完畢，填完後即可送出。"
        )

    if st.button("🔄 重新設定基本資料", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()

# --- 3. 單一項目填寫與自動判定頁面 ---
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
    st.success("本次巡檢數據已成功轉化為結構化 Raw Data！")

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
