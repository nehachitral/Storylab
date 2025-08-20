import os
import time
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoProcessor, AutoTokenizer, AutoModelForCausalLM
from langgraph.graph import StateGraph
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"


# --- Model and Workflow Setup ---
model_id = "ibm-granite/granite-4.0-tiny-preview"

processor = AutoProcessor.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

def generate_with_granite(prompt: str, max_tokens: int = 200, use_gpu: bool = USE_GPU) -> str:

    device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
    model.to(device)

    messages = [{"role": "user", "content": prompt}]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt"
    ).to(device)

    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
    )

    generated = tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True)
    return generated.strip()


def select_genre_node(state: dict) -> dict:
    prompt = f"""
You are a creative assistant. The user wants to write a short animated story.
Based on the following input, suggest a suitable genre and tone for the story.
User Input: {state['user_input']}
Respond in this format:
Genre: <genre>
Tone: <tone>
""".strip()
    response = generate_with_granite(prompt)
    genre, tone = None, None
    for line in response.splitlines():
        if "Genre:" in line:
            genre = line.split("Genre:")[1].strip()
        elif "Tone:" in line:
            tone = line.split("Tone:")[1].strip()
    state["genre"] = genre
    state["tone"] = tone
    return state

def generate_outline_node(state: dict) -> dict:
    prompt = f"""
You are a creative writing assistant helping to write a short animated screenplay.
The user wants to write a story with the following details:
Genre: {state.get('genre')}
Tone: {state.get('tone')}
Idea: {state.get('user_input')}
Write a brief plot outline (3–5 sentences) for the story.
""".strip()
    response = generate_with_granite(prompt, max_tokens=250)
    state["outline"] = response
    return state

def generate_scene_node(state: dict) -> dict:
    prompt = f"""
You are a screenwriter.
Based on the following plot outline, write a key scene from the story.
Focus on a turning point or climax moment. Make the scene vivid, descriptive, and suitable for an animated short film.
Genre: {state.get('genre')}
Tone: {state.get('tone')}
Outline: {state.get('outline')}
Write the scene in prose format (not screenplay format).
""".strip()
    response = generate_with_granite(prompt, max_tokens=300)
    state["scene"] = response
    return state

def write_dialogue_node(state: dict) -> dict:
    prompt = f"""
You are a dialogue writer for an animated screenplay.
Below is a scene from the story:
{state.get('scene')}
Write the dialogue between the characters in screenplay format.
Keep it short, expressive, and suitable for a short animated film.
Use character names (you may invent them if needed), and format as:
CHARACTER:
Dialogue line
CHARACTER:
Dialogue line
""".strip()
    response = generate_with_granite(prompt, max_tokens=200)
    state["dialogue"] = response
    return state

def with_progress(fn, label, index, total):
    def wrapper(state):
        print(f"\n[{index}/{total}] Starting: {label}")
        start = time.time()
        result = fn(state)
        duration = time.time() - start
        print(f"[{index}/{total}] Completed: {label} in {duration:.2f} seconds")
        return result
    return wrapper

def build_workflow():
    graph = StateGraph(dict)
    graph.add_node("select_genre", with_progress(select_genre_node, "Select Genre", 1, 4))
    graph.add_node("generate_outline", with_progress(generate_outline_node, "Generate Outline", 2, 4))
    graph.add_node("generate_scene", with_progress(generate_scene_node, "Generate Scene", 3, 4))
    graph.add_node("write_dialogue", with_progress(write_dialogue_node, "Write Dialogue", 4, 4))

    graph.set_entry_point("select_genre")
    graph.add_edge("select_genre", "generate_outline")
    graph.add_edge("generate_outline", "generate_scene")
    graph.add_edge("generate_scene", "write_dialogue")
    graph.set_finish_point("write_dialogue")

    return graph.compile()

workflow = build_workflow()

# --- Flask App ---
app = Flask(__name__)
CORS(app)

@app.route("/generate-story", methods=["POST"])
def generate_story():
    data = request.get_json()
    user_input = data.get("user_input")

    if not user_input:
        return jsonify({"error": "Missing 'user_input' in request."}), 400

    initial_state = {"user_input": user_input}
    final_state = workflow.invoke(initial_state)

    return jsonify({
        "genre": final_state.get("genre"),
        "tone": final_state.get("tone"),
        "outline": final_state.get("outline"),
        "scene": final_state.get("scene"),
        "dialogue": final_state.get("dialogue")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
