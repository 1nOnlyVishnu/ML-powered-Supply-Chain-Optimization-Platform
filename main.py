import streamlit as st

from streamlit_option_menu import option_menu

import account , about 

st.set_page_config(page_title="Supply Chain Analytics", layout="wide")



class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self,title,function):
        self.apps.append({"title": title, "function": function})

    def run(self):
        with st.sidebar:
            selected = option_menu(
            menu_title="Main Menu",
            options=["Account", "Demand Forecasting", "Risk Management", "Inventory Optimization" , "About"],
            icons=["person-circle", "bar-chart", "shield-lock", "boxes" ," person-circle"],
            default_index=0,
    )
            
        if selected == "Account":
            account.account_page()
        elif selected == "About":
            about.about_page()
        

    run()

