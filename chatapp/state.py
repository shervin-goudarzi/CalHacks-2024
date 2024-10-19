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

    questions: list[str] = [
        "What's your current immigration status?",
        "What date did you come to the US?",
        "What is your education level?",
        "What skills do you have?",
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

        # Move to the next question after processing the current one
        self.current_question_index += 1

        # If we've finished the survey, disable further input
        if self.current_question_index >= len(self.questions):
            self.current_question_index = -1