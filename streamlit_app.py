import asyncio
import subprocess
import sys

import ollama
import textwrap
import streamlit as st
from mcp import Client, StdioServerParameters


# ============================================================
# CONFIG
# ============================================================

MODEL = "qwen2.5-coder:1.5b"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Autonomous Coding Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(99, 102, 241, 0.12),
                transparent 35%
            ),
            radial-gradient(
                circle at top right,
                rgba(168, 85, 247, 0.10),
                transparent 30%
            );
    }

    /* Main content */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hero */
    .hero {
        padding: 30px;
        border-radius: 22px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(79, 70, 229, 0.25),
                rgba(124, 58, 237, 0.18)
            );
        border: 1px solid rgba(139, 92, 246, 0.35);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 17px;
        opacity: 0.8;
    }

    /* Section cards */
    .section-card {
        padding: 22px;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        background: rgba(15, 23, 42, 0.45);
        margin-bottom: 20px;
    }

    /* Status cards */
    .status-card {
        padding: 18px;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        background: rgba(15, 23, 42, 0.55);
        text-align: center;
        min-height: 105px;
    }

    .status-icon {
        font-size: 28px;
    }

    .status-title {
        font-size: 14px;
        font-weight: 600;
        margin-top: 7px;
    }

    .status-ok {
        color: #4ade80;
        font-size: 13px;
        margin-top: 4px;
    }

    /* MCP tools */
    .tool {
        display: inline-block;
        padding: 8px 13px;
        margin: 5px;
        border-radius: 10px;
        background: rgba(79, 70, 229, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        font-family: monospace;
        font-size: 13px;
    }

    /* Hide Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    textwrap.dedent("""
        <div class="hero">
            <div class="hero-title">
                🤖 Autonomous Coding Agent
            </div>
            <div class="hero-subtitle">
                AI-powered software development using
                <b>Ollama</b> • <b>Qwen</b> • <b>Ops Crew</b> • <b>MCP</b>
            </div>
        </div>
    """),
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ System")

    st.success("🟢 Agent Online")

    st.markdown("---")

    st.markdown("### 🧠 AI Model")

    st.code(MODEL)

    st.markdown("### 🔧 Architecture")

    st.write("🧠 Planner")
    st.write("💻 Coder")
    st.write("🔍 Reviewer")
    st.write("🔌 MCP")
    st.write("▶️ Executor")

    st.markdown("---")

    st.caption(
        "Autonomous Coding Agent\n"
        "Built with Python + Streamlit + Ollama + MCP"
    )


# ============================================================
# USER INPUT
# ============================================================

st.markdown("## 📝 Create Something")

task = st.text_area(
    "What should the coding agent build?",
    placeholder=(
        "Example: Calculate the average of three numbers"
    ),
    height=120
)

program_input = st.text_area(
    "⌨️ Program input",
    placeholder="Example:\n10\n20\n30",
    height=100
)


# ============================================================
# AGENT FUNCTION
# ============================================================

def run_agent(role, task_text):

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": role
            },
            {
                "role": "user",
                "content": task_text
            }
        ]
    )

    return response["message"]["content"]


# ============================================================
# MCP
# ============================================================

async def run_mcp_operations(code):

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"]
    )

    async with Client(server_params) as client:

        tools_result = await client.list_tools()

        tool_names = [
            tool.name
            for tool in tools_result.tools
        ]

        await client.call_tool(
            "write_project_file",
            {
                "file_path": "projects/generated_code.py",
                "content": code
            }
        )

        await client.call_tool(
            "read_project_file",
            {
                "file_path": "projects/generated_code.py"
            }
        )

        return tool_names


# ============================================================
# RUN BUTTON
# ============================================================

if st.button(
    "🚀  Run Autonomous Coding Agent",
    type="primary",
    use_container_width=True
):

    if not task.strip():

        st.warning(
            "⚠️ Please enter a coding task first."
        )

    else:

        # ====================================================
        # PLANNER
        # ====================================================

        with st.spinner("🧠 Planner is designing the solution..."):

            plan = run_agent(
                "You are the planning agent. "
                "Create a simple step-by-step plan. "
                "Do not write code.",
                task
            )

        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.subheader("🧠 Planner")

        st.write(plan)

        st.markdown("</div>", unsafe_allow_html=True)


        # ====================================================
        # CODER
        # ====================================================

        with st.spinner("💻 Coder is generating Python code..."):

            code = run_agent(
                "You are the coding agent. "
                "Write valid Python code based on the task and plan. "
                "If the task requires user values, use input() "
                "to collect those values. "
                "Do not hardcode example values unless explicitly asked. "
                "Return only valid Python code.",
                f"""
Task:
{task}

Plan:
{plan}
"""
            )

        code = code.replace("```python", "")
        code = code.replace("```", "")
        code = code.strip()

        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.subheader("💻 Generated Code")

        st.code(
            code,
            language="python"
        )

        st.markdown("</div>", unsafe_allow_html=True)


        # ====================================================
        # REVIEWER
        # ====================================================

        with st.spinner("🔍 Reviewer is checking the code..."):

            review = run_agent(
                "You are a code reviewer. "
                "Check this Python code for errors and possible bugs. "
                "Give a concise review.",
                f"""
Task:
{task}

Generated code:
{code}
"""
            )

        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.subheader("🔍 Code Review")

        st.write(review)

        st.markdown("</div>", unsafe_allow_html=True)


        # ====================================================
        # MCP
        # ====================================================

        with st.spinner("🔌 Connecting to MCP server..."):

            try:

                tool_names = asyncio.run(
                    run_mcp_operations(code)
                )

                st.success(
                    "🔌 Real MCP connection successful!"
                )

                st.markdown(
                    '<div class="section-card">',
                    unsafe_allow_html=True
                )

                st.subheader("🔌 MCP Tools")

                for tool in tool_names:

                    st.markdown(
                        f'<span class="tool">🔧 {tool}</span>',
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as error:

                st.error(
                    f"MCP connection failed: {error}"
                )

                st.stop()


        # ====================================================
        # EXECUTOR
        # ====================================================

        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.subheader("▶️ Execution")

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    "projects/generated_code.py"
                ],
                input=program_input,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:

                st.success(
                    "✅ Program completed successfully!"
                )

                if result.stdout:

                    st.code(
                        result.stdout,
                        language="text"
                    )

            else:

                st.error(
                    "❌ Program execution failed."
                )

                if result.stderr:

                    st.code(
                        result.stderr,
                        language="text"
                    )

        except subprocess.TimeoutExpired:

            st.error(
                "⏱️ Program took too long to finish."
            )

        st.markdown("</div>", unsafe_allow_html=True)


        # ====================================================
        # OPS CREW STATUS
        # ====================================================

        st.divider()

        st.subheader("🚀 Ops Crew Pipeline")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:

            st.markdown(
                """
                <div class="status-card">
                    <div class="status-icon">🧠</div>
                    <div class="status-title">Planner</div>
                    <div class="status-ok">✓ Complete</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                """
                <div class="status-card">
                    <div class="status-icon">💻</div>
                    <div class="status-title">Coder</div>
                    <div class="status-ok">✓ Complete</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                """
                <div class="status-card">
                    <div class="status-icon">🔍</div>
                    <div class="status-title">Reviewer</div>
                    <div class="status-ok">✓ Complete</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:

            st.markdown(
                """
                <div class="status-card">
                    <div class="status-icon">🔌</div>
                    <div class="status-title">MCP</div>
                    <div class="status-ok">✓ Connected</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col5:

            st.markdown(
                """
                <div class="status-card">
                    <div class="status-icon">▶️</div>
                    <div class="status-title">Executor</div>
                    <div class="status-ok">✓ Complete</div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🤖 Autonomous Coding Agent • "
    "Ollama + Qwen + Ops Crew + Model Context Protocol"
)