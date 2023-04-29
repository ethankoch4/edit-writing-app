"""Streamlit app for editing text with langchain."""
import time
import streamlit as st
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from nltk import sent_tokenize

LLM = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7, request_timeout=60)

edit_sentence_chain = LLMChain.from_string(
    llm=LLM,
    template="""
You are an highly skilled editor that follows commands. You are given a sentence and a command.
You must edit the sentence according to the command.

Here is the command:
```
{edit_command}
```

Answer in a single, complete sentence.

Here is the sentence:
```
{sentence}
```
""",
)

no_editing_returns = (
    "no editing needed",
    "no edits needed",
    "not need editing",
)

st.set_page_config(layout="wide")


how_to_edit_display = "Choose how to edit the sentence"
options_for_editing = (
    how_to_edit_display,
    "Fix any potential mistakes",
    "Make the sentence more concise",
    "Expand the sentence",
    "Use more formal language",
    "Use less formal language",
    "Make more vivid",
)

input_text = st.session_state.get("input_text") or (
    "It was a bright cold day in April, and the clocks were striking thirteen."
    " Winston Smith, his chin nuzzled into his chest in an effort to escape the vile ..."
)
input_writing = st.text_area(
    "input writing",
    input_text,
    label_visibility="collapsed",
)

if input_writing:
    st.session_state["input_text"] = input_writing
    sentences = sent_tokenize(input_writing)
    for i, sent in enumerate(sentences):
        sent_key = f"sent_{i}"
        st.session_state[sent_key] = sent
        this_button = st.button(sent)
        this_button_clicked = st.session_state.get(f"{sent_key}_button")
        if this_button or this_button_clicked:
            st.session_state[f"{sent_key}_button"] = True
            _, center_col, _ = st.columns([1, 3, 1])
            print("clicked")
            how_to_edit = center_col.selectbox(
                f'editing: "{sent}"',
                options_for_editing,
            )
            say_how = center_col.text_input(
                "Or write a custom edit command",
            )
            if (how_to_edit != how_to_edit_display) or say_how:
                print("WRITING")
                center_col.write("editing sentence...")
                edit_command = (
                    how_to_edit if how_to_edit != how_to_edit_display else say_how
                )
                new_sentence = edit_sentence_chain.run(
                    {
                        "edit_command": edit_command,
                        "sentence": sent,
                    }
                )
                print(new_sentence)
                editing_needed = True
                for no_editing_return in no_editing_returns:
                    if no_editing_return in new_sentence.lower():
                        center_col.write("no editing needed")
                        editing_needed = False
                        break
                if editing_needed:
                    st.session_state["input_text"] = st.session_state[
                        "input_text"
                    ].replace(sent, new_sentence)
                    sentences[i] = new_sentence
                    st.session_state[sent_key] = new_sentence
                    center_col.write(new_sentence)
                    center_col.write("done editing sentence")
                st.session_state.pop(f"{sent_key}_button")
                print("done")
                center_col.write("refreshing...")
                time.sleep(2)
                st.experimental_rerun()


st.markdown(
    """
    <style>
    button {
        background: none!important;
        border: none;
        padding: 0!important;
        color: black !important;
        text-decoration: none;
        cursor: pointer;
        border: none !important;
    }
    button:hover {
        text-decoration: none;
        color: black !important;
    }
    button:focus {
        outline: none !important;
        box-shadow: none !important;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
