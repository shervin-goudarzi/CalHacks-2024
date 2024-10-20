import functools
import json
import jwt
import os
import time
import warnings
warnings.filterwarnings("ignore")
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
import firebase_admin
from firebase_admin import credentials, firestore

import reflex as rx
from chatapp.chatbot import chat, action_bar, chatmodel, reset_button
from chatapp.chatbot import State as ChatState
import chatapp.style as style
from typing import Dict, Any

from documentation.documentation_help import State as DocumentationState
from jobs.job_scraper import State as JobState
from documentation.documentation_components import documents
from jobs.jobs_components import jobs


from .react_oauth_google import (
    GoogleOAuthProvider,
    GoogleLogin,
)

CLIENT_ID = "1015718854739-uhoa4d0mu7geqhumisq993171fqedf3d.apps.googleusercontent.com"


class State(ChatState):
    db: int = 0

    def get_db(self):
        if self.db != 0:
            return self.db
        # Initialize Firebase (do this only once, typically at the start of your application)
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the credentials file
        cred_path = os.path.join(current_dir, "..", "firebase-credentials.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        return self.db

    id_token_json: str = rx.LocalStorage()
    user_id: str = ""
    old_user: bool = False

    def on_success(self, id_token: dict):
        self.id_token_json = json.dumps(id_token)
        id_token_data = json.loads(self.id_token_json)
        # Get the ID token
        id_token = id_token_data['credential']
        # Decode the token (without verification, as we trust the source)
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        # Extract the 'sub' claim
        self.user_id = decoded_token['sub']
        self.load_user_profile()
        return rx.redirect("/chatbot")

    @rx.var(cache=True)
    def tokeninfo(self) -> dict[str, str]:
        try:
            token_info = verify_oauth2_token(
                json.loads(self.id_token_json)[
                    "credential"
                ],
                requests.Request(),
                CLIENT_ID,
            )
            self.user_id = token_info.get('sub')
            return token_info
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
    
    def save_user_profile(self):
        user_data = {
            #'name': self.tokeninfo.get('name'),
            #'email': self.tokeninfo.get('email'),
            'location': self.location,
            'immigration_status': self.immigration_status,
            'when_moved': self.when_moved,
            'skills': self.skills,
            'education': self.education,
        }
        self.get_db().collection('users').document(self.user_id).set(user_data)
        self.old_user = True
        ChatState.current_question_index = 0
        return rx.redirect('/chatbot')

    def reset_user_profile(self):
        self.location = ''
        self.immigration_status = ''
        self.when_moved = ''
        self.skills = []
        self.education = ''
        ChatState.current_question_index = 0
        ChatState.chat_history = []

    def load_user_profile(self):
        user_id = self.tokeninfo.get('sub')
        doc_ref = self.get_db().collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            user_data = doc.to_dict()
            self.location = user_data.get('location', '')
            self.immigration_status = user_data.get('immigration_status', '')
            self.when_moved = user_data.get('when_moved', '')
            self.skills = user_data.get('skills', [])
            self.education = user_data.get('education', '')
            self.old_user = True
    
    def redirect_to_chatbot(self):
        return rx.redirect('/chatbot')


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
            rx.heading("Welcome to Product_Name", size="2xl", color="teal.500"),
            rx.text(
                """
                Immigrants and refugees face numerous challenges when settling in a new country, including language barriers, legal complexities, and difficulties in finding suitable employment and support networks. While existing resources like FindHello provide general information, there's a clear need for a more personalized, comprehensive, and long-term solution. 
                Our app aims to fill this gap by offering tailored assistance throughout the integration process, helping immigrants and refugees thrive in their new home in the long term.
                """,
                font_size="lg",
                padding="20px",
                text_align="center",
            ),
            rx.link("Login with Google", href="/chatbot", font_size="lg", color="blue.500"),
            spacing="20px",
        ),
        padding="50px",
        background="""radial-gradient(circle at 15% 8%, rgba(255, 193, 7, 0.2), hsla(0, 0%, 100%, 0) 25%),
            radial-gradient(circle at 75% 20%, rgba(33, 150, 243, 0.18), hsla(0, 0%, 100%, 0) 30%),
            radial-gradient(circle at 30% 65%, rgba(76, 175, 80, 0.22), hsla(0, 0%, 100%, 0) 45%),
            radial-gradient(circle at 85% 80%, rgba(233, 30, 99, 0.15), hsla(0, 0%, 100%, 0) 35%);"""
    )


def navbar_link(name: str, href: str) -> rx.Component:
    return rx.link(
        name,
        href=href,
        font_size="lg",
        padding="10px",
    )

def NavBar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.text("Product_Name", font_size="2xl", font_weight="bold", padding="10px"),
                align_items="center",
            ),
            rx.hstack(
                navbar_link("Profile", "/chatbot"),
                navbar_link("Documents", "/documents"),
                navbar_link("Job Postings", "/job_postings"),
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
        padding="10px",
        width="100%",
    )


@rx.page(route="/home")
@require_google_login
def protected() -> rx.Component:
    return rx.vstack(
        NavBar(),
    )

@rx.page(route="/documents",on_load=State.load_user_profile)
@require_google_login
def documents_page() -> rx.Component:
    return rx.vstack(
        NavBar(),
        rx.center(
            rx.vstack(
                rx.cond(
                    State.old_user,
                    rx.container(
                        documents(),
                        on_mount=DocumentationState.get_immigration_info(State.immigration_status),
                    ),
                    rx.container(
                        rx.text("Please complete your profile to view your documents."),
                        rx.button("Complete Profile", on_click=State.redirect_to_chatbot),
                    ),
                ),
                spacing="20px",
            ),
            padding="20px",
            width="100%",
        ),
        width="100%",
        spacing="20px",
    )

@rx.page(route="/chatbot",on_load=State.load_user_profile)
@require_google_login
def chatbot() -> rx.Component:
    return rx.vstack(
        NavBar(),
            rx.center(
                rx.vstack(
                    rx.container(
                        chat(),
                        rx.cond(
                            State.current_question_index >= 0,
                            action_bar(),
                            action_bar_after_done(),
                        ),
                        spacing="20px",
                    ),
                ),
                width="100%",
            ),
        width="100%",
        spacing="20px",
    )

@rx.page(route="/job_postings",on_load=State.load_user_profile)
@require_google_login
def jobs_page() -> rx.Component:
    return rx.vstack(
        NavBar(),
        rx.center(
            rx.vstack(
                rx.cond(
                    State.old_user,
                    rx.container(
                        jobs(),
                        on_mount=JobState.get_job_postings(State.skills, State.location, State.education, State.immigration_status)
                    ),
                    rx.container(
                        rx.text("Please complete your profile to view your recommended nearby job postings."),
                        rx.button("Complete Profile", on_click=State.redirect_to_chatbot),
                    ),
                ),
                spacing="20px",
            ),
            padding="20px",
            width="100%",
        ),
        width="100%",
        spacing="20px",
    )

def action_bar_after_done() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=State.question,
            placeholder="Answer the question above.",
            on_change=State.set_question,
            style=style.input_style,
        ),
        rx.button(
            "Finish",
            on_click=State.save_user_profile,
            style=style.button_style,
            color_scheme="green",
        ),
        reset_button()
    )


app = rx.App(
        theme=rx.theme(
        radius="large",
        accent_color="blue",
        style={
            "light": {
                "--text-color": "black",
                "--bg-color": "white",
            },
            "dark": {
                "--text-color": "white",
                "--bg-color": "black",
            },
        },
        appearance="light",
    )
)
app.add_page(index)
app.add_page(protected)
app.add_page(chatbot)