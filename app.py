# import streamlit as st
from application import page_config, main, sidebar

# PAGE CONFIGURATION and STYLING
page_config.run()

# SIDEBAR SELECTION
selected_option = sidebar.run()

# MAIN SECTION
main.run(selected_option)
