# # state.py
# import os
# from openai import AsyncOpenAI
# import reflex as rx
# from dotenv import load_dotenv
# load_dotenv()

# class State(rx.State):
#     # The current question being asked.
#     # question: str

#     questions_to_ask = [
#             "What's your immigration status?", 
#             "What date did you come to the US?",
#             "What skills do you have?",
#             "What is your education level?",
#             "What is your current zipcode?"
#         ]

#     # Keep track of the chat history as a list of (question, answer) tuples.
#     chat_history: list[tuple[str, str]] = [("", "What's your current immigration status?")]

#     async def answer(self):
#         # Our chatbot has some brains now!
#         client = AsyncOpenAI(
#             api_key=os.environ["OPENAI_API_KEY"]
#         )

#         session = await client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Once the user gives a valid immigration status, ask them these question, in order: When did you move to the US?, What is your education level?, What are your skills?, What is your zipcode?"}
#             ],
#             stop=None,
#             temperature=0.7,
#             stream=True,
#         )

#         # Add to the answer as the chatbot responds.
#         answer = ""
#         self.chat_history.append((self.question, answer))

#         # Clear the question input.
#         self.question = ""
#         # Yield here to clear the frontend input before continuing.
#         yield

#         async for item in session:
#             if hasattr(item.choices[0].delta, "content"):
#                 if item.choices[0].delta.content is None:
#                     # presence of 'None' indicates the end of the response
#                     break
#                 answer += item.choices[0].delta.content
#                 self.chat_history[-1] = (
#                     self.chat_history[-1][0],
#                     answer,
#                 )
#                 yield

# chat_components.py

import reflex as rx
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

class State(rx.State):
    # The current question being asked.
    question: str = ""

    questions: list[str] = [
        "What's your current immigration status?",
        "What date did you come to the US?",
        "What skills do you have?",
        "What is your education level?",
        "What is your current zipcode?"
    ]

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = [("", "What's your current immigration status?")]

    # Index of the current question
    current_question_index: int = 0

    async def answer(self):
        if not self.question:
            return

        # Add user's response to chat history
        self.chat_history.append((self.question, ""))
        
        # Our chatbot has some brains now!
        client = AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )

        # Prepare the next question or finish the survey
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            next_question = self.questions[self.current_question_index]
            system_message = f"Ask the user: {next_question}"
        else:
            system_message = "Thank the user for completing the survey and provide a brief summary of their responses."

        session = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant conducting an immigration survey. Provide helpful responses based on the user's answers."},
                {"role": "user", "content": f"User's response to '{self.questions[self.current_question_index-1]}': {self.question}"},
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
                    # presence of 'None' indicates the end of the response
                    break
                answer += item.choices[0].delta.content
                self.chat_history[-1] = (
                    self.chat_history[-1][0],
                    answer,
                )
                yield

        # If we've finished the survey, disable further input
        if self.current_question_index >= len(self.questions):
            self.current_question_index = -1  # Use this as a flag to indicate survey completion

def chatmodel() -> rx.Component:
    return rx.vstack(
        rx.foreach(
            State.chat_history,
            lambda message: rx.box(
                rx.text(message[1] if message[1] else message[0]),
                text_align="left" if message[1] else "right",
                color="blue" if message[1] else "green",
                padding="1em",
                border_radius="0.5em",
                bg="lightgray" if message[1] else "lightgreen",
                margin_y="0.5em",
            )
        ),
        rx.cond(
            State.current_question_index >= 0,
            rx.vstack(
                rx.input(
                    value=State.question,
                    placeholder="Type your answer here...",
                    on_change=State.set_question,
                ),
                rx.button("Submit", on_click=State.answer),
            ),
            rx.text("Survey completed. Thank you for your responses!")
        ),
        spacing="4",
        width="100%",
        max_width="600px",
    )