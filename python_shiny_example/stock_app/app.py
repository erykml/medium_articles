from shiny import App, render, ui
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.h2("Stock price tracker"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select(
                "ticker", 
                "Select stock:", {"TSLA": "Tesla", 
                                  "AAPL": "Apple"}
            ),
            ui.input_date_range(
                "date_range", 
                "Date range input"
            ),
        ),
        ui.panel_main(
            ui.output_plot("plot"),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.plot(alt="Stock price over time")
    def plot():
        
        df = yf.download(input.ticker(), 
                         start=input.date_range()[0], 
                         end=input.date_range()[1], 
                         progress=False)

        fig, ax = plt.subplots()
        df["Close"].plot(title=f"{input.ticker()} - Stock price history", ax=ax)
        
        return fig


app = App(app_ui, server)