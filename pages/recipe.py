import streamlit as st
import os
import io
import json
import openai
from pydantic import BaseModel, Field
from PIL import Image
from stability_sdk import client as stability_client

class Ingredient(BaseModel):
    ingredient: str = Field(description="材料名", example=["鶏むね肉"])
    quantity: str = Field(description="分量", example=["200g"])

class Recipe(BaseModel):
    ingredients: list[Ingredient]
    instructions: list[str] = Field(description="作り方", example=["鶏むね肉を切る", "鶏むね肉を焼く"])
    muscle_benefits: str = Field(description="筋トレに良いポイント", example="鶏むね肉は高タンパクで脂肪が少ないため、筋肉の修復と成長に最適です。")
    in_english: str = Field(description="料理名(英語)", example="Chicken Breast")

OUTPUT_RECIPE_FUNCTION = {
    "name": "generate_recipe",
    "description": "レシピの出力",
    "parameters": Recipe.model_json_schema(),
}

PROMPT_TEMPLATE = """筋トレに効果的な料理のレシピを考えてください。

料理名：{dish}

料理に含まれる筋トレに良いポイントについても説明してください。
"""

st.title("筋トレレシピ生成AI")

dish = st.text_input(label="料理名")

if dish:
    with st.spinner("AIがレシピを生成しています..."):

        messages = [
            {"role": "user",
             "content": PROMPT_TEMPLATE.format(dish=dish),
             }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=[OUTPUT_RECIPE_FUNCTION],
            function_call={"name": OUTPUT_RECIPE_FUNCTION["name"]}
        )

        response_message = response.choices[0].message
        function_call_args = response_message.function_call.arguments

        recipe = json.loads(function_call_args)
        st.write(f"## レシピ: {dish}")
        st.write("## 材料")
        st.table(recipe["ingredients"])

        st.write("## 作り方")
        for i, instruction in enumerate(recipe["instructions"]):
            st.write(instruction)
        
        st.write("## 筋トレに良いポイント")
        st.write(recipe["muscle_benefits"])

        stability_api = stability_client.StabilityInference(
            key = os.environ["STABILITY_API_KEY"],engine="stable-diffusion-xl-1024-v1-0"
        )

        answers = stability_api.generate(
            prompt = recipe["in_english"],height=512, width=512, samples=1
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == stability_client.generation.FILTER:
                    st.warning("画像を生成できませんでした。")

                if artifact.type == stability_client.generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    st.image(img)
