import reflex as rx
from rxconfig import config
from jobs.job_apify_scraper import State
from chatapp import style

def jobs() -> rx.Component:
    return rx.center(
        rx.text(State.job_results),
        width="100%",
    )

