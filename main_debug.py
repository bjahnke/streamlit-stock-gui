import source.streamlit_app as streamlit_app
import ptvsd
ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
ptvsd.wait_for_attach()
