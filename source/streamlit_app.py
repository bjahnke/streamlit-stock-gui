import streamlit as st
from pathlib import Path
from source.utils import save_ticker_args, load_ticker_args

def handle_page_input():
    st.session_state.page_name = st.session_state.page_name_input
    st.session_state.page_name_input = ''

def run():
    print("Running streamlit_app.py")
    st.set_page_config(layout="wide")
    if 'page_name' not in st.session_state:
        st.session_state.page_name = ''
    if 'ticker_args' not in st.session_state:
        load_ticker_args()

    with open("new_page_template.py", "r") as file:
        file_template = file.read()
        f"""{file_template}"""
        # Get page names from pages folder and store in list

    pages_folder = Path("source") / "views"
    page_files = pages_folder.glob("*.py")
    st.sidebar.text_input("New Page Name:", key="page_name_input", on_change=handle_page_input)

    if st.sidebar.button("Add Page"):
        if st.session_state.page_name:
            page_name = st.session_state.page_name
            st.session_state.ticker_args[page_name] = dict()
            st.session_state.ticker_args[page_name]["symbol"] = page_name
            st.session_state.ticker_args[page_name]["interval"] = '1 day'
            st.session_state.ticker_args[page_name]["chart_type"] = 'Candlestick'
            st.session_state.ticker_args[page_name]["indicators"] = []
            st.session_state.ticker_args[page_name]["bar_count"] = 365
            st.session_state.ticker_args[page_name]["source"] = 'yfinance'
            (pages_folder / f"{page_name}.py").write_text(
                    file_template.format(
                        new_page_name=page_name,
                        symbol='symbol'
                    ),
                    encoding="utf-8",
            )
            save_ticker_args()
            st.sidebar.text_input("New Page Name:", value="")
            st.rerun()

    top_pages = [
        st.Page(Path('source') / "streamlit_app.py"),
        st.Page(Path('source') / "tools" / "config.py"),
        st.Page(Path('source') / "tools" / "coinbase.py"),   
        st.Page(Path('source') / "tools" / "delete.py"),
    ]
    pages = []
    for file in page_files:
        if file.name != "__init__.py":
            f"""{(pages_folder / file.name).absolute()}"""
            pages.append(st.Page(pages_folder / file.name))
    
    pages.sort(key=lambda page: page.title)
    pages = top_pages + pages

    pg = st.navigation(pages)
    pg.run()


