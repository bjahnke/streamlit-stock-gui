from invoke.tasks import task
from vector_db.build_script import IndexBuilder

@task
def build_vector(_):
    builder = IndexBuilder(
        project_dir="/home/brian/repos/streamlit-stock-gui",
        chroma_dir="/home/brian/chroma_storage",
        collection_name="my_codebase",
        model_name="all-MiniLM-L6-v2",
        ignore_file="./vector-db/.llamaignore",
    )
    builder.build()

@task
def interact_with_vector(_):
    builder = IndexBuilder(
        project_dir="/home/brian/repos/streamlit-stock-gui",
        chroma_dir="/home/brian/chroma_storage",
        collection_name="my_codebase",
        model_name="all-MiniLM-L6-v2",
        ignore_file="./vector-db/.llamaignore",
    )
    builder.interact()


@task
def activate(ctx):
    ctx.run("source venv/bin/activate")

@task 
def run_app(ctx):
    ctx.run('streamlit run main.py')