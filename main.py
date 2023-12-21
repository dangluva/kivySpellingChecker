import nltk
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from difflib import get_close_matches

nltk.download('wordnet')

all_words_set = set(word for synset in nltk.corpus.wordnet.all_synsets() for word in synset.lemma_names())


class HyperlinkLabel(Label):
    def __init__(self, text, on_click, **kwargs):
        super(HyperlinkLabel, self).__init__(**kwargs)
        self.text = f"[ref={text}]{text}[/ref]"
        self.bind(on_ref_press=on_click)


def get_part_of_speech(pos_code):
    pos_mapping = {
        'n': 'noun',
        'v': 'verb',
        'a': 'adjective',
        'r': 'adverb',
    }
    return pos_mapping.get(pos_code[0].lower(), '')


def get_suggestions(partial_word, search_word_callback):
    # Get close matches from the set of words based on the first two or more letters
    close_matches = [word for word in all_words_set if word.startswith(partial_word[:2].lower())]

    # Convert HyperlinkLabel instances to strings before adding to suggestions
    suggestions = [suggestion.text for suggestion in
                   [HyperlinkLabel(suggestion, on_click=search_word_callback) for suggestion in
                    get_close_matches(partial_word, close_matches)]]

    return suggestions


class WordInfoApp(App):
    def build(self):
        self.layout = FloatLayout()

        # Search word field and button on the same level
        self.user_input = TextInput(hint_text='Enter your word', multiline=False, size_hint=(None, None), width=300, height=30, pos_hint={'center_x': 0.5, 'top': 1})
        btn_search = Button(text='Search', size_hint=(None, None), width=100, height=30, pos_hint={'center_x': 0.5, 'top': 0.9})
        btn_search.bind(on_press=self.search_word)

        # Widgets for upper layout
        upper_layout = FloatLayout()
        upper_layout.add_widget(self.user_input)
        upper_layout.add_widget(btn_search)
        self.layout.add_widget(upper_layout)

        # Updated the label properties for centering text
        self.info_label = Label(text='', halign='left', valign='top', markup=True, size_hint=(None, None), width=Window.width - 20, height=Window.height - 100, pos_hint={'center_x': 0.5, 'y': 0})
        self.scrollview = ScrollView(size=(Window.width - 20, Window.height - 100), pos_hint={'center_x': 0.5, 'y': 0}, bar_width=10, size_hint_y=None, height=Window.height - 100)
        self.layout.add_widget(self.scrollview)
        self.layout.add_widget(self.info_label)

        return self.layout

    @staticmethod
    def get_word_info(word):
        synsets = nltk.corpus.wordnet.synsets(word)

        if not synsets:
            # If no exact match found, suggest close matches
            suggestions = WordInfoApp.get_suggestions(word)  # Pass search_word callback here
            if suggestions:
                return [f"No definitions found for '{word}'. Did you mean one of these:"] + [
                    f"{i}. {suggestion}" for i, suggestion in enumerate(suggestions, start=1)]
            else:
                return [f"No definitions found for '{word}' and no close matches."]

        info_list = []
        for index, synset in enumerate(synsets):
            # Get part of speech
            pos = get_part_of_speech(synset.pos())
            pos_text = f'({pos}) ' if pos else ''

            # Full definition
            full_definition = synset.definition()

            # Get antonyms
            antonyms = []
            for lemma in synset.lemmas():
                if lemma.antonyms():
                    antonyms.extend((antonym, lemma.synset().pos()) for antonym in lemma.antonyms())

            if antonyms:
                # Filter antonyms based on part of speech
                antonyms_text = f"(antonym: {', '.join(antonym.name() for antonym, antonym_pos in antonyms if get_part_of_speech(antonym_pos) == pos)})"
            else:
                antonyms_text = ""

            info_list.append(f"{index + 1}. {pos_text}{full_definition} {antonyms_text}")

            examples = ". ".join(synset.examples())

            if examples:
                # Split examples into one sentence per line
                example_sentences = examples.split(". ")
                info_list.append('Examples:')
                info_list.extend([
                    f"{i + 1}: {sentence.capitalize()}" if ',' in sentence or '!' in sentence else f"{i + 1}: {sentence.capitalize()}."
                    for i, sentence in enumerate(example_sentences)])
                info_list.append('\n')  # Added a new empty line
            else:
                info_list.append("No examples.\n")

        return info_list

    def search_word(self, instance):
        user_word = self.user_request()
        info_list = self.get_word_info(user_word)
        self.info_label.text = '\n'.join(info_list)
        self.scrollview.scroll_y = 1  # Scroll to the top

    def user_request(self):
        user_request_text = self.user_input.text.strip()
        return user_request_text

    @staticmethod
    def get_suggestions(partial_word):
        # Get close matches from the set of words based on the first two or more letters
        close_matches = [word for word in all_words_set if word.startswith(partial_word[:2].lower())]

        return [suggestion.text for suggestion in
                [HyperlinkLabel(suggestion, on_click=lambda x: None) for suggestion in
                 get_close_matches(partial_word, close_matches)]]


if __name__ == '__main__':
    WordInfoApp().run()
