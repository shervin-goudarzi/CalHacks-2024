import reflex as rx
from openai import AsyncOpenAI
import os
import firebase_admin
from dotenv import load_dotenv

load_dotenv()

class State(rx.State):
    # The current question being asked
    question: str
    prev_question: str = ""

    immigration_status: str = ""
    when_moved: str = ""
    education: str = ""
    skills: str = ""
    location: str = ""

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

    async def verify_input(self, question: str, answer: str) -> tuple[bool, str]:
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        response = await client.chat.completions.create(
            model="gpt-4",  # Use the appropriate model
            messages=[
                {"role": "system", "content": "You are a very understanding and empathetic AI assistant verifying user input for an immigration survey. Respond with only the word 'valid' verbatim if the input is appropriate for the question, otherwise explain to the user what they should type instead very empathetically and very clearly. Assume these individuals don't speak English as a first language."},
                {"role": "user", "content": f"Question: {question}\nUser's answer: {answer}\nIs this a valid response?"}
            ],
            temperature=0.7
        )
        
        verification_result = response.choices[0].message.content
        is_valid = verification_result.lower().startswith("valid")
        return is_valid, verification_result

    async def answer(self):
        if not self.question:
            return
        
        validity, interpretation = await self.verify_input(self.questions[self.current_question_index], self.question)
        if not validity:
            self.chat_history.append(("", interpretation))
            yield
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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a very understanding, compassionate, and empathetic AI assistant conducting an immigration survey. Provide helpful responses based on the user's answers."},
                {"role": "user", "content": f"User's response to '{self.questions[self.current_question_index]}': {self.question}"},
                {"role": "system", "content": system_message}
            ],
            temperature=0.7,
            stream=True,
        )

        # Add to the answer as the chatbot responds.
        answer = ""

        # Clear the question input.
        self.prev_question = self.question
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

        if not self.current_question_index:
            self.immigration_status = self.prev_question
        elif self.current_question_index == 1:
            self.when_moved = self.prev_question
        elif self.current_question_index == 2:
            self.education = self.prev_question
        elif self.current_question_index == 3:
            self.skills = self.prev_question
        else:
            self.location = self.prev_question

        # Move to the next question after processing the current one
        self.current_question_index += 1

        # If we've finished the survey, disable further input
        if self.current_question_index >= len(self.questions):
            self.current_question_index = -1 