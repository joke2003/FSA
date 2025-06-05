import os
import streamlit as st
from langchain.llms.base import LLM
from typing import List, Dict

# Mock LLM using langchain base class
class MockLLM(LLM):
    """A simple mock LLM returning placeholder analysis."""
    @property
    def _llm_type(self) -> str:
        return "mock"

    def _call(self, prompt: str, stop: List[str] | None = None) -> str:
        return f"模拟分析: {prompt[:60]}..."

def load_sample_files():
    files_dir = os.path.join(os.getcwd(), "files")
    sample = {}
    for name in os.listdir(files_dir):
        path = os.path.join(files_dir, name)
        if os.path.isfile(path):
            with open(path, "rb") as f:
                sample[name] = f.read()
    return sample

# Financial analysis modules
MODULES = {
    "第一部分：外部环境、战略定位与公司治理": [
        "1.1 宏观环境分析 (PESTEL)",
        "1.2 行业竞争环境分析 (波特五力模型)",
        "1.3 SWOT 分析",
        "1.4 公司治理与管理层素质评估",
    ],
    "第二部分：财务概览与经营业绩评估": [
        "2.0 财务报表概览与趋势分析",
        "2.1 综合比率分析",
        "2.2 杜邦分析",
        "2.3 营运资本与现金转换周期分析",
        "2.4 杠杆分析 (运营与财务)",
        "2.5 分部信息分析",
        "2.6 Piotroski F-Score 模型",
        "2.7 经济增加值 (EVA) 分析",
        "2.8 同行业基准比较分析",
    ],
    "第三部分：盈利质量与会计政策分析": [
        "3.1 财务报表附注深度解读与关键会计政策评估",
        "3.2 经营活动现金流量与净利润的比较分析",
        "3.3 应计项目分析",
        "3.4 盈余管理与财务舞弊风险模型 (Beneish, Dechow理念等)",
        "3.5 自由现金流量趋势与充足性分析",
    ],
    "第四部分：信用风险与偿债能力评估": [
        "4.1 营运资金充足性与短期流动性风险",
        "4.2 利息保障倍数及现金流偿债能力分析",
        "4.3 Altman Z-Score",
        "4.4 Ohlson O-Score (如适用)",
        "4.5 其他财务困境预测模型 (如Zmijewski X-Score, 可选)",
    ],
    "第五部分：增长潜力与可持续性分析": [
        "5.1 盈利与现金流增长匹配度分析",
        "5.2 再投资率 (RR) 与投入资本回报率 (ROIC) 分析",
        "5.3 可持续增长率模型 (SGR)",
        "5.4 内部增长率模型 (IGR)",
    ],
    "第六部分：财务预测与建模": [
        "6.0 统计预测与趋势外推 (可选)",
        "6.1 销售收入预测",
        "6.2 成本与费用结构预测",
        "6.3 资产负债表项目预测",
        "6.4 构建三表联动财务模型",
        "6.5 情景分析与敏感性测试",
    ],
    "第七部分：公司估值": [
        "7.1 公司自由现金流折现模型 (FCFF)",
        "7.2 股权自由现金流折现模型 (FCFE)",
        "7.3 股利贴现模型 (DDM)",
        "7.4 剩余收益模型 (RIM)",
        "7.5 可比公司分析 (市场乘数法)",
        "7.6 基于调整后账面价值的估值",
    ],
}

def generate_prompt(module: str, context: Dict[str, str]) -> str:
    """Generate a prompt string for a module."""
    header = f"请根据提供的财务报表和背景信息，完成以下分析模块：{module}。"
    params = "\n".join(f"{k}:{v}" for k, v in context.items())
    return f"{header}\n{params}"

def run_analysis(selected_modules: List[str], context: Dict[str, str]):
    llm = MockLLM()
    notes = []
    for module in selected_modules:
        prompt = generate_prompt(module, context)
        result = llm.invoke(prompt)
        notes.append(f"### {module}\n{result}")
    return "\n".join(notes)

def main():
    st.title("财务报表分析助手")
    if "uploaded" not in st.session_state:
        st.session_state.uploaded = {}
    if "params" not in st.session_state:
        st.session_state.params = {}
    if "plan" not in st.session_state:
        st.session_state.plan = []
    if "notes" not in st.session_state:
        st.session_state.notes = ""

    st.sidebar.header("分析参数")
    company = st.sidebar.text_input("公司名称")
    industry = st.sidebar.text_input("所属行业")
    listed = st.sidebar.selectbox("是否上市公司", ["是", "否"])
    ticker = st.sidebar.text_input("股票代码")
    angle = st.sidebar.selectbox("分析角度", ["债权投资", "股权投资", "债股双投"])

    ai_plan = st.sidebar.checkbox("使用AI规划分析方案", value=False)

    st.sidebar.button("一键测试准备", on_click=lambda: st.session_state.uploaded.update(load_sample_files()))

    uploaded_files = st.file_uploader(
        "上传财务报表及相关文件 (最多4期)",
        accept_multiple_files=True,
    )
    if uploaded_files:
        for f in uploaded_files:
            st.session_state.uploaded[f.name] = f.read()

    st.session_state.params = {
        "公司": company,
        "行业": industry,
        "是否上市": listed,
        "股票代码": ticker,
        "分析角度": angle,
    }

    st.write("## 已上传文件")
    for name in st.session_state.uploaded:
        st.write(name)

    if ai_plan:
        if st.button("生成分析方案"):
            st.session_state.plan = [m for sec in MODULES for m in MODULES[sec]][:3]
            st.write("AI规划的分析模块", st.session_state.plan)
        st.write("当前计划:", st.session_state.plan)
    else:
        st.session_state.plan = [m for sec in MODULES for m in MODULES[sec]]

    if st.button("开始分析"):
        st.session_state.notes = run_analysis(st.session_state.plan, st.session_state.params)

    st.write("## 核心底稿")
    st.markdown(st.session_state.notes)

if __name__ == "__main__":
    main()
