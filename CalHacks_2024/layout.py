import reflex as rx

def layout(content):
    return rx.box(
        rx.script(src="/my-custom.js"),
        content
    )