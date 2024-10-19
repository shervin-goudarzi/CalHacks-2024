import reflex as rx
from rxconfig import config
from chatapp.state import State
from chatapp import style

def qa(question: str, answer: str) -> rx.Component:
    return rx.cond(
        question == "",
        rx.box(
            rx.text(answer, style=style.answer_style),
            text_align="left",
        ),
        rx.box(
            rx.box(
                rx.text(question, style=style.question_style),
                text_align="right",
            ),
            rx.box(
                rx.text(answer, style=style.answer_style),
                text_align="left",
            ),
            margin_y="1em",
        )
    )

def chat() -> rx.Component:
    return rx.box(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        )
    )

def action_bar() -> rx.Component:
    return rx.cond(State.current_question_index >= 0,
        rx.hstack(
            rx.input(
                value=State.question,
                placeholder="Answer the question above.",
                on_change=State.set_question,
                style=style.input_style,
            ),
            rx.button(
                "Respond",
                on_click=State.answer,
                style=style.button_style,
            ),
        ),
        rx.button("Click Here to Proceed", on_click=State.save_user_profile())
    )

def chatmodel() -> rx.Component:
    return rx.center(
        rx.vstack(
            chat(),
            action_bar(),
            align="center",
            margin_top="20vh"
        )
    )

__all__ = ["chatmodel"]


# def chatmodel() -> rx.Component:
#     return rx.vstack(
#         rx.foreach(
#             State.chat_history,
#             lambda message: rx.box(
#                 rx.text(message[1] if message[1] else message[0]),
#                 text_align="left" if message[1] else "right",
#                 color="blue" if message[1] else "green",
#                 padding="1em",
#                 border_radius="0.5em",
#                 bg="lightgray" if message[1] else "lightgreen",
#                 margin_y="0.5em",
#             )
#         ),
#         rx.cond(
#             State.current_question_index >= 0,
#             rx.vstack(
#                 rx.input(
#                     value=State.question,
#                     placeholder="Type your answer here...",
#                     on_change=State.set_question,
#                 ),
#                 rx.button("Submit", on_click=State.answer),
#             ),
#             rx.text("Survey completed. Thank you for your responses!")
#         ),
#         spacing="4",
#         width="100%",
#         max_width="600px",
#     )
