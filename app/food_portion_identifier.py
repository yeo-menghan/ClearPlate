import cv2
import numpy as np
import json
from PIL import Image
from ultralytics import YOLO
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# --- Configuration and Model Loading ---
try:
    coin_model = YOLO("app/models/coin_model.pt")
    food_model = YOLO("app/models/food_segmentation_model_2.pt")
except Exception as e:
    print(f"Error loading YOLO models: {e}")
    exit()

try:
    with open("app/assets/density.json", "r") as f:
        DENSITY = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    DENSITY = {}

COIN_REAL_AREA_MM2 = 380.0


# --- Helper Functions ---
def compute_category_areas(masks, class_ids, names):
    area_dict = defaultdict(int)
    if masks is not None and class_ids is not None:
        for mask, cls in zip(masks, class_ids):
            area = np.sum(mask)
            food_name = names.get(int(cls), f"Unknown ({int(cls)})")
            area_dict[food_name] += int(area)
    return dict(area_dict)


def compute_total_area(masks):
    if masks is not None and len(masks) > 0:
        return int(sum(np.sum(mask) for mask in masks))
    return 0


# --- Main Detection and Segmentation Logic ---
def detect_and_segment(image):
    image_np = np.array(image)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    coin_result_item = coin_model(image_bgr, conf=0.5)[0]
    coin_img_rgb = cv2.cvtColor(coin_result_item.plot(), cv2.COLOR_BGR2RGB)
    coin_masks = (
        coin_result_item.masks.data.cpu().numpy() if coin_result_item.masks else None
    )

    food_result_item = food_model(image_bgr)[0]
    food_img_rgb = cv2.cvtColor(food_result_item.plot(), cv2.COLOR_BGR2RGB)
    food_masks = (
        food_result_item.masks.data.cpu().numpy() if food_result_item.masks else None
    )
    food_classes = (
        food_result_item.boxes.cls.cpu().numpy() if food_result_item.boxes else None
    )
    food_names = food_result_item.names

    coin_area_px = compute_total_area(coin_masks)
    food_areas_px = compute_category_areas(food_masks, food_classes, food_names)

    weights = {}
    if coin_area_px > 0 and food_areas_px:
        px_to_mm2 = COIN_REAL_AREA_MM2 / coin_area_px
        for food, area_px in food_areas_px.items():
            density = DENSITY.get(food, {}).get("density_g_per_cm3", 1.0)
            mm2_area = area_px * px_to_mm2
            volume_cm3 = mm2_area / 100.0
            weight = round(volume_cm3 * density, 2)
            weights[food] = weight

    # --- Generate Horizontal Bar Chart ---
    bar_data = pd.DataFrame(weights.items(), columns=["Food", "Weight (g)"])
    bar_data = bar_data.sort_values(by="Weight (g)", ascending=True)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 6))
    if not bar_data.empty:
        sns.barplot(x="Weight (g)", y="Food", data=bar_data, palette="Spectral", ax=ax)
        ax.set_title("Food Thrown (g)", fontsize=16, color="white")
        ax.set_xlabel("Weight (g)", color="white")
        ax.set_ylabel("Food Item", color="white")
        ax.tick_params(colors="white")
        ax.grid(axis="x", linestyle="--", alpha=0.7, color="gray")
        ax.set_axisbelow(True)

        for p in ax.patches:
            width = p.get_width()
            ax.text(
                width + 0.005,
                p.get_y() + p.get_height() / 2,
                f"{width:.2f}",
                ha="left",
                va="center",
                color="white",
            )

        ax.set_xlim(0, bar_data["Weight (g)"].max() * 1.15)
    else:
        ax.text(
            0.5,
            0.5,
            "No food weights to display.",
            ha="center",
            va="center",
            fontsize=14,
            color="gray",
        )
        ax.axis("off")

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    bar_chart_image = Image.open(buf).copy()
    plt.close(fig)

    return Image.fromarray(coin_img_rgb), Image.fromarray(food_img_rgb), bar_chart_image
