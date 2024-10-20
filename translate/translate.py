# import reflex as rx

# class LanguageToggle(rx.State):
#     current_language: str = "en"

#     @classmethod
#     def change_language(cls, lang: str):
#         cls.current_language = lang
#         return cls.update_language(lang)

#     @rx.background
#     async def update_language(cls, lang: str):
#         yield rx.set_value("google_translate_element", lang)
#         yield rx.script(f"""
#             var select = document.querySelector('.goog-te-combo'); 
#             if (select) {{
#                 select.value = '{lang}'; 
#                 select.dispatchEvent(new Event('change')); 
#             }}
#         """)

# def translate_component():
#     return rx.box(id="google_translate_element")

# def language_toggles():
#     return rx.hstack(
#         rx.button("English", on_click=lambda: LanguageToggle.change_language("en")),
#         rx.button("Spanish", on_click=lambda: LanguageToggle.change_language("es")),
#         rx.button("French", on_click=lambda: LanguageToggle.change_language("fr")),
#         rx.button("German", on_click=lambda: LanguageToggle.change_language("de")),
#         rx.button("Chinese", on_click=lambda: LanguageToggle.change_language("zh-CN")),
#         rx.button("Hindi", on_click=lambda: LanguageToggle.change_language("hi")),
#         spacing="1em",
#     )

# def LanguageToggleComponent():
#     return rx.vstack(
#         translate_component(),
#         language_toggles(),
#         rx.text("This is some sample text that will be translated."),
#         rx.script(src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"),
#         rx.script("""
#         function googleTranslateElementInit() {
#             new google.translate.TranslateElement(
#                 {pageLanguage: 'en', layout: google.translate.TranslateElement.InlineLayout.SIMPLE},
#                 'google_translate_element'
#             );
#         }
#         """),
#         spacing="2em",
#     )

# language_toggle/state.py
import reflex as rx
from googletrans import Translator
from typing import Dict, Optional
from functools import lru_cache

class LanguageState(rx.State):
    """Global state for language management."""
    current_language: str = "en"
    translations_cache: Dict[str, Dict[str, str]] = {}
    
    @lru_cache(maxsize=1)
    def get_translator(self) -> Translator:
        """Singleton translator instance."""
        return Translator()
    
    def get_translation(self, text_id: str, original_text: str) -> str:
        """Get cached translation or translate and cache."""
        if self.current_language == "en":
            return original_text
            
        cache_key = f"{text_id}:{self.current_language}"
        if cache_key not in self.translations_cache:
            try:
                translated = self.get_translator().translate(
                    original_text,
                    dest=self.current_language
                )
                self.translations_cache[cache_key] = translated.text
            except Exception as e:
                print(f"Translation error for {text_id}: {e}")
                return original_text
                
        return self.translations_cache.get(cache_key, original_text)
    
    def change_language(self, lang_code: str):
        """Update current language."""
        self.current_language = lang_code

# language_toggle/constants.py
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko"
}

# language_toggle/components.py
import reflex as rx
from .state import LanguageState
from .constants import LANGUAGES

def translatable_text(
    text_id: str,
    content: str,
    component_type: rx.Component = rx.text,
    **kwargs
) -> rx.Component:
    """
    Create a translatable text component.
    
    Args:
        text_id: Unique identifier for this text
        content: Original text content
        component_type: rx.Component to render the text (default: rx.text)
        **kwargs: Additional props to pass to the component
    """
    return component_type(
        rx.bind(LanguageState.get_translation, text_id, content),
        id=f"translate_{text_id}",
        **kwargs
    )

def language_toggle(
    size: str = "md",
    variant: str = "solid",
    spacing: str = "2",
    show_flags: bool = False
) -> rx.Component:
    """
    Create a language toggle component.
    
    Args:
        size: Button size (sm, md, lg)
        variant: Button variant (solid, outline, ghost)
        spacing: Space between buttons
        show_flags: Whether to show language flags (if available)
    """
    return rx.box(
        rx.hstack(
            *[
                rx.button(
                    rx.hstack(
                        # Optional flag emoji (if show_flags is True)
                        rx.text("🏳️" if not show_flags else {
                            "en": "🇺🇸",
                            "es": "🇪🇸",
                            "fr": "🇫🇷",
                            "de": "🇩🇪",
                            "zh-CN": "🇨🇳",
                            "ja": "🇯🇵",
                            "ko": "🇰🇷"
                        }.get(lang_code, "🏳️")),
                        rx.text(lang_name),
                        spacing="2"
                    ),
                    on_click=LanguageState.change_language(lang_code),
                    size=size,
                    variant=variant if LanguageState.current_language != lang_code else "solid",
                    color_scheme="blue" if LanguageState.current_language == lang_code else "gray",
                )
                for lang_name, lang_code in LANGUAGES.items()
            ],
            spacing=spacing,
            overflow_x="auto",
            py="2",
        ),
        width="100%",
    )

# Example usage in any page:
"""
from language_toggle.components import language_toggle, translatable_text

def your_component():
    return rx.vstack(
        # Basic usage
        language_toggle(),
        translatable_text("welcome", "Welcome!"),
        
        # Advanced usage
        language_toggle(
            size="sm",
            variant="outline",
            spacing="4",
            show_flags=True
        ),
        translatable_text(
            "title",
            "This is a heading",
            component_type=rx.heading,
            size="lg"
        ),
        translatable_text(
            "button_text",
            "Click me",
            component_type=rx.button,
            color_scheme="blue"
        )
    )
"""