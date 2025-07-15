from app.food_portion_identifier import detect_and_segment
import gradio as gr
import os

# --- Launch Gradio App ---
examples_list = [["app/assets/test6.jpg"]] if os.path.exists("app/assets/test6.jpg") else []
custom_css = """
    body { font-family: 'Inter', sans-serif; background-color: #0f1117; color: #e5e7eb; }
    .gr-button { background-color: #3b82f6; color: white; border-radius: 8px; padding: 10px 16px; font-weight: bold; transition: 0.3s ease; }
    .gr-button:hover { background-color: #2563eb; }
    .gr-box { border: 1px solid #1f2937; border-radius: 12px; padding: 16px; background-color: #1f2937; }
    .gr-image { border-radius: 12px; }
    .gr-interface-title { font-size: 28px; font-weight: bold; color: #f9fafb; margin-bottom: 8px; }
    .gr-interface-description { font-size: 16px; color: #d1d5db; }
"""

gr.Interface(
    fn=detect_and_segment,
    inputs=gr.Image(type="pil", label="Upload Food Image with a Coin"),
    outputs=[
        gr.Image(label="Coin Detection Results"),
        gr.Image(label="Food Segmentation Results"),
        gr.Image(label="Estimated Food Waste (g)"),
    ],
    title="\U0001f4ca ClearPlate",
    description=(
        "<p>Upload an image with food and a Singapore $1 coin. The system detects the coin, segments food, and estimates waste (in grams)."
        "<br><b>Notes:</b> Clear coin presence required.</p>"
    ),
    allow_flagging="never",
    examples=examples_list,
    css=custom_css,
).launch(server_name="0.0.0.0", server_port=7860, share=True)
