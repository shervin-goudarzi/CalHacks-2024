import reflex as rx
from openai import AsyncOpenAI
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
load_dotenv()

class State(rx.State):
    # The current question being asked.
    question: str = ""

    user_id: str = ""
    immigration_status: str = ""
    arrival_date: str = ""
    education_level: str = ""
    skills: str = ""
    zipcode: str = ""

    def __init__(self):
        super().__init__()
        # Initialize Firebase
        cred = credentials.Certificate("../firebase-credentials.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    questions: list[str] = [
        "What's your current immigration status?",
        "What date did you come to the US?",
        "What is your education level?",
        "What skills do you have?",
        "What is your current zipcode?"
    ]

    async def save_user_profile(self):
        if self.user_id:
            user_data = {
                "immigration_status": self.immigration_status,
                "arrival_date": self.arrival_date,
                "education_level": self.education_level,
                "skills": self.skills,
                "zipcode": self.zipcode,
            }
            await self.db.collection("users").document(self.user_id).set(user_data)

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = [("", "What's your current immigration status?")]

    # Index of the current question
    current_question_index: int = 0

    async def answer(self):
        if not self.question:
            return

        # Add user's response to chat history
        self.chat_history.append((self.question, ""))
        
        client = AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )

        # Prepare the next question or finish the survey
        if self.current_question_index < len(self.questions) - 1:
            next_question = self.questions[self.current_question_index + 1]
            system_message = f"Ask the user: {next_question}"
        else:
            system_message = "Thank the user for completing the survey and provide a brief summary of their responses."

        session = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant conducting an immigration survey. Provide helpful responses based on the user's answers."},
                {"role": "user", "content": f"User's response to '{self.questions[self.current_question_index]}': {self.question}"},
                {"role": "system", "content": system_message}
            ],
            temperature=0.7,
            stream=True,
        )

        # Add to the answer as the chatbot responds.
        answer = ""

        # Clear the question input.
        self.question = ""
        # Yield here to clear the frontend input before continuing.
        yield

        async for item in session:
            if hasattr(item.choices[0].delta, "content"):
                if item.choices[0].delta.content is None:
                    break
                answer += item.choices[0].delta.content
                self.chat_history[-1] = (
                    self.chat_history[-1][0],
                    answer,
                )
                yield

        # Process the user's answer and update the corresponding field
        if self.current_question_index == 0:
            self.immigration_status = self.question
        elif self.current_question_index == 1:
            self.arrival_date = self.question
        elif self.current_question_index == 2:
            self.education_level = self.question
        elif self.current_question_index == 3:
            self.skills = self.question
        elif self.current_question_index == 4:
            self.zipcode = self.question

        # Move to the next question after processing the current one
        self.current_question_index += 1

        # If we've finished the survey, disable further input
        if self.current_question_index >= len(self.questions):
            self.current_question_index = -1 

def chatmodel(chatbot_state: State = State()) -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.foreach(
                chatbot_state.chat_history,
                lambda messages: rx.vstack(
                    rx.box(
                        rx.text(messages[0]),
                        background_color="lightgrey",
                        padding="1em",
                        border_radius="5px",
                    ),
                    rx.box(
                        rx.text(messages[1]),
                        background_color="lightblue",
                        padding="1em",
                        border_radius="5px",
                    ),
                    width="100%",
                ),
            ),
            padding="1em",
            height="60vh",
            overflow="auto",
        ),
        rx.form(
            rx.input(
                placeholder="Type your answer here...",
                id="question",
                on_blur=chatbot_state.set_question,
                is_disabled=chatbot_state.current_question_index == -1,
            ),
            rx.button("Send", type="submit", on_click=chatbot_state.answer),
            width="100%",
        ),
    )