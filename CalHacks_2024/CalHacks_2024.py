import functools
import json
import os
import time

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import reflex as rx

from .react_oauth_google import (
    GoogleOAuthProvider,
    GoogleLogin,
)

CLIENT_ID = "1015718854739-uhoa4d0mu7geqhumisq993171fqedf3d.apps.googleusercontent.com"


class State(rx.State):
    id_token_json: str = rx.LocalStorage()

    def on_success(self, id_token: dict):
        self.id_token_json = json.dumps(id_token)
        return rx.redirect("/home")

    @rx.var(cache=True)
    def tokeninfo(self) -> dict[str, str]:
        try:
            return verify_oauth2_token(
                json.loads(self.id_token_json)[
                    "credential"
                ],
                requests.Request(),
                CLIENT_ID,
            )
        except Exception as exc:
            if self.id_token_json:
                print(f"Error verifying token: {exc}")
        return {}

    def logout(self):
        self.id_token_json = ""
        return rx.redirect("/")

    @rx.var
    def token_is_valid(self) -> bool:
        try:
            return bool(
                self.tokeninfo
                and int(self.tokeninfo.get("exp", 0))
                > time.time()
            )
        except Exception:
            return False

    @rx.var(cache=True)
    def protected_content(self) -> str:
        if self.token_is_valid:
            return f"This content can only be viewed by a logged in User. Nice to see you {self.tokeninfo['name']}"
        return "Not logged in."


def user_info(tokeninfo: dict) -> rx.Component:
    return rx.hstack(
        rx.avatar(
            name=tokeninfo["name"],
            src=tokeninfo["picture"],
            size="2",
        ),
    )

def login() -> rx.Component:
    return rx.vstack(
        GoogleLogin.create(on_success=State.on_success),
    )


def require_google_login(page) -> rx.Component:
    @functools.wraps(page)
    def _auth_wrapper() -> rx.Component:
        return GoogleOAuthProvider.create(
            rx.cond(
                State.is_hydrated,
                rx.cond(
                    State.token_is_valid, page(), login()
                ),
                rx.spinner(),
            ),
            client_id=CLIENT_ID,
        )

    return _auth_wrapper


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Welcome to Immigrant Support Portal", size="2xl", color="teal.500"),
            rx.text(
                "This website is dedicated to providing resources and support for immigrants. "
                "Our goal is to help you navigate the complexities of immigration and find the assistance you need.",
                font_size="lg",
                padding="20px",
                text_align="center",
            ),
            rx.link("Login with Google", href="/home", font_size="lg", color="blue.500"),
            spacing="20px",
        ),
        padding="50px",
    )


def navbar_link(name: str, href: str) -> rx.Component:
    return rx.link(
        name,
        href=href,
        font_size="lg",
        color="white",
        padding="10px",
    )

def NavBar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.text("Product_Name", font_size="2xl", color="white", font_weight="bold", padding="10px"),
                    align_items="center",
                ),
                rx.hstack(
                    navbar_link("Home", "/home"),
                    navbar_link("Chatbot", "/chatbot"),
                    navbar_link("Settings", "/settings"),
                    spacing="20px",
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        user_info(State.tokeninfo),
                    ),
                    rx.menu.content(
                        rx.menu.item(
                            rx.button("Logout", on_click=State.logout)
                        ),
                    ),
                    justify="end",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(
                    rx.text("Product_Name", font_size="2xl", color="white", font_weight="bold", padding="10px"),
                    align_items="center",
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        user_info(State.tokeninfo),
                    ),
                    rx.menu.content(
                        rx.menu.item(
                            rx.button("Logout", on_click=State.logout)
                        ),
                    ),
                    justify="end",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        padding="10px",
        width="100%",
    )




@rx.page(route="/home")
@require_google_login
def protected() -> rx.Component:
    return rx.vstack(
        NavBar(),
    )


@rx.page(route="/chatbot")
@require_google_login
def chatbot() -> rx.Component:
    return rx.vstack(
        NavBar(),
        rx.text("put chatbot here"),
    )


app = rx.App(
        theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="blue",
    )
)
app.add_page(index)
app.add_page(protected)
app.add_page(chatbot)