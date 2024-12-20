import streamlit as st
from pathlib import Path
from source.tools.utils import save_ticker_args, load_ticker_args

top_pages = [
    st.Page(Path('source') / "streamlit_app.py"),
    st.Page(Path('source') / "tools" / "config.py"),
    st.Page(Path('source') / "tools" / "coinbase.py"),
    st.Page(Path('source') / "tools" / 'coingecko' / "coingecko.py"),
    st.Page(Path('source') / "tools" / "watchlist.py"),   
    st.Page(Path('source') / "tools" / "delete.py"),
]

def handle_page_input():
    st.session_state.page_name = st.session_state.page_name_input
    # st.session_state.page_name_input = ''


def init_session_state():
    st.session_state.watchlist = dict()

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
            (pages_folder / f"{page_name}.py").write_text(
                    file_template.format(
                        new_page_name=page_name,
                        symbol='symbol'
                    ),
                    encoding="utf-8",
            )
            st.sidebar.text_input("New Page Name:", value="")
            st.rerun()


    pages = []
    for file in page_files:
        if file.name != "__init__.py":
            f"""{(pages_folder / file.name).absolute()}"""
            pages.append(st.Page(pages_folder / file.name))
    
    pages.sort(key=lambda page: page.title)
    pages = top_pages + pages

    pg = st.navigation(pages)
    pg.run()



