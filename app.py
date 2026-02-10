import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. 数据存储配置 ---
PROJECT_FILE = 'projects.csv'
EXPENSE_FILE = 'expenses.csv'

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        return pd.DataFrame(columns=columns)

# --- 2. 界面初始化 ---
st.set_page_config(page_title="经费管理", layout="wide")

# --- 3. 侧边栏导航 ---
menu = st.sidebar.radio("功能菜单", ["项目档案管理", "日常支出记录", "数据统计看板"])

# --- 模块 A：项目档案管理 ---
if menu == "项目档案管理":
    st.title("📂 项目档案管理")
    df_projects = load_data(PROJECT_FILE, ['项目名称', '简称', '合同金额'])

    with st.sidebar.form("add_project_form", clear_on_submit=True):
        st.header("🆕 新增立项")
        p_name = st.text_input("项目全称")
        p_short = st.text_input("项目简称")
        p_amount = st.number_input("合同金额 (元)", min_value=0.0)
        submit_p = st.form_submit_button("确认创建")

    if submit_p and p_name and p_short:
        new_p = pd.DataFrame([[p_name, p_short, p_amount]], columns=df_projects.columns)
        df_projects = pd.concat([df_projects, new_p], ignore_index=True)
        df_projects.to_csv(PROJECT_FILE, index=False)
        st.success(f"项目 {p_short} 已保存")

    st.dataframe(df_projects, use_container_width=True)

# --- 模块 B：日常支出记录 ---
elif menu == "日常支出记录":
    st.title("💸 支出流水记录")
    df_projects = load_data(PROJECT_FILE, ['项目名称', '简称', '合同金额'])
    df_expenses = load_data(EXPENSE_FILE, ['日期', '关联项目', '金额', '类别', '报销状态', '备注'])

    if df_projects.empty:
        st.warning("请先去『项目档案管理』录入至少一个项目！")
    else:
        with st.sidebar.form("add_expense_form", clear_on_submit=True):
            st.header("➕ 记一笔支出")
            e_date = st.date_input("支出日期", value=datetime.now())
            e_project = st.selectbox("选择关联项目", df_projects['简称'].tolist())
            e_amount = st.number_input("支出金额 (元)", min_value=0.0)
            e_category = st.selectbox("支出类别", ["差旅费", "招待费(请客)", "材料费", "劳务费", "其他"])
            e_status = st.selectbox("报销状态", ["未报销", "报销中", "已结清"])
            e_note = st.text_input("备注(具体干了啥)")
            submit_e = st.form_submit_button("保存记录")

        if submit_e:
            new_e = pd.DataFrame([[e_date, e_project, e_amount, e_category, e_status, e_note]], 
                                columns=df_expenses.columns)
            df_expenses = pd.concat([df_expenses, new_e], ignore_index=True)
            df_expenses.to_csv(EXPENSE_FILE, index=False)
            st.success("记录已保存！")

    st.dataframe(df_expenses, use_container_width=True)

# --- 模块 C：数据统计看板 ---
elif menu == "数据统计看板":
    st.title("📊 经费使用统计")
    df_projects = load_data(PROJECT_FILE, ['项目名称', '简称', '合同金额'])
    df_expenses = load_data(EXPENSE_FILE, ['日期', '关联项目', '金额', '类别', '报销状态', '备注'])
    
    if not df_expenses.empty:
        # 简单统计：每个项目花了多少钱
        stats = df_expenses.groupby('关联项目')['金额'].sum().reset_index()
        st.write("### 各项目已支出总额")
        st.bar_chart(stats.set_index('关联项目'))
        
        # 统计待报销总额
        unpaid = df_expenses[df_expenses['报销状态'] != "已结清"]['金额'].sum()
        st.metric("待收回(未报销)总金额", f"¥{unpaid:,.2f}")
    else:
        st.info("暂无支出数据，无法生成统计。")