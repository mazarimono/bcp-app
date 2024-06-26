import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime

# ChatGPT: https://chat.openai.com/share/5d3a8f51-4edd-411a-9c62-e153c7f2d673


st.set_page_config(
    page_title="長目: BCPチェッカー", page_icon="img/chomoku-favicon.png"
)

df = pd.read_csv("./data/bcp_test.csv")

if "current_num" not in st.session_state:
    st.session_state["current_num"] = 0

if "answers" not in st.session_state:
    st.session_state["answers"] = {}


def increment_session(answer):
    st.session_state["answers"][st.session_state["current_num"]] = answer
    if st.session_state["current_num"] < len(df):
        st.session_state["current_num"] += 1


def modoru_func():
    if st.session_state["current_num"] > 1:
        st.session_state["current_num"] -= 1


def susumu_func():
    if st.session_state["current_num"] > 0 or st.session_state["current_num"] < len(df):
        st.session_state["current_num"] += 1


def reset_func():
    st.session_state["current_num"] = 0
    st.session_state["answers"] = {}


def agg_answers():
    ans = list(st.session_state["answers"].values())
    nums = list(st.session_state["answers"].keys())
    df = pd.DataFrame()
    df["ans"] = ans
    df["nums"] = nums
    df["cat"] = pd.NA
    df.loc[0, "cat"] = "人的資源"
    df.loc[4, "cat"] = "物的資源"
    df.loc[8, "cat"] = "資金資源"
    df.loc[12, "cat"] = "情報資源"
    df.loc[16, "cat"] = "体制など"
    df = df.ffill()
    score = df["ans"].sum()
    dfg = df.groupby("cat", as_index=False).sum()
    dfg["ans_str"] = dfg["ans"].map(lambda x: f"{x} / 4")
    return df, score, dfg


def situation_check(score):
    if score < 6:
        return st.write(
            """緊急事態に遭遇すると、あなたの会社の事業は長期間停止し、
    廃業に追い込まれる恐れがあります。１からBCPの策定・運用に
    取り組んでください。まずは、中小企業庁の基本コースを読んでみましょう。
    https://www.chusho.meti.go.jp/bcp/contents/level_a/bcpgl_01.html
    """
        )
    elif score < 16:
        return st.write(
            """緊急事態に備える意識は高いですが、まだまだ改善点があります。
    実践的なBCPを策定し、平常時から運用を進めましょう。
    中小企業庁のBCP中級編を読んでみましょう。
    https://www.chusho.meti.go.jp/bcp/contents/level_b/bcpgl_01.html
    """
        )
    else:
        return st.write(
            """BCPの考え方に則った取り組みが進んでいるようです。
            中小企業庁のBCP中級編、上級編をチェックしてみましょう。
            https://www.chusho.meti.go.jp/bcp/contents/level_b/bcpgl_01.html
        """
        )


def show_chart(df):
    fig = px.line_polar(df, r="ans", theta="cat", line_close=True)
    fig.update_traces(fill="toself")
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 4], "color": "black"}},
        autosize=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def display_results():
    st.header("BCPチェッカー", divider="rainbow")

    st.write("## 全ての質問に回答しました")
    st.write("### 回答結果")
    df, score, dfg = agg_answers()
    today_date = datetime.now().date()
    st.write(f"#### {today_date}時点の")
    st.write(f"御社の得点は {score} です。（20点満点中）")

    if score < 18:
        st.write("BCP取り組みの改善を行い、またチャレンジしてください！")

    situation_check(score)

    show_chart(dfg)

    st.write("**右上のケバブメニュー（３つの点）のPrintから内容をPDFで出力できます。**")
    st.button("もう一度", on_click=reset_func)

    st.divider()
    st.write(
        "このBCPチェックアプリは、中小企業庁: BCP取り組み状況チェックを基に作成しています"
    )
    st.write("https://www.chusho.meti.go.jp/bcp/contents/level_a/bcpgl_01_3.html")
    st.write("回答されたデータは保存されません")
    st.write("作成: 合同会社長目 https://www.chomoku.info")
    # for i, answer in enumerate(st.session_state["answers"], start=1):
    #     st.write(f"質問 {i}: {answer}")


def show_quiz():
    quiz_num = st.session_state["current_num"] + 1
    quiz = df.loc[st.session_state["current_num"], "質問"]
    st.header("BCPチェッカー", divider="rainbow")

    st.title(f"質問: {quiz_num}")
    st.write(f"{quiz}")
    st.button("はい", on_click=increment_session, args=(1,))
    st.button("いいえ", on_click=increment_session, args=(0,))
    st.button("?", on_click=increment_session, args=(0,))

    progress = (st.session_state["current_num"] + 1) / len(df)

    st.progress(progress)
    st.write(f"{quiz_num} / {len(df)}")

    st.divider()
    st.write(
        "このBCPチェックアプリは、中小企業庁: BCP取り組み状況チェックを基に作成しています"
    )
    st.write("https://www.chusho.meti.go.jp/bcp/contents/level_a/bcpgl_01_3.html")
    st.write("作成: 合同会社長目 https://www.chomoku.info")


if st.session_state["current_num"] < len(df):
    show_quiz()
else:
    display_results()
