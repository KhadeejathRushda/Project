import cv2
import numpy as np
import tensorflow as tf
from lime import lime_image
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt

# Import the model object directly from ml_model
# This works because ml_model.py runs the load_model and patch on startup
from .ml_model import model

# Initialize the explainer
explainer = lime_image.LimeImageExplainer()

def generate_lime_explanation(image_path, save_path):
    """
    Generates a LIME explanation heatmap for a given X-ray image 
    and saves it to the specified path.
    """
    # 1. Load and Resize image (300x300 matches your model training)
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img, (300, 300))

    # 2. Prediction wrapper for LIME
    def predict_fn(images):
        # Apply the same scaling used during model training/prediction
        images_scaled = tf.keras.applications.efficientnet_v2.preprocess_input(images)
        return model.predict(images_scaled, verbose=0)

    # 3. Run LIME Explainer
    # We use 500 samples for a balance between speed and quality
    explanation = explainer.explain_instance(
        img_resized.astype('double'), 
        predict_fn, 
        top_labels=1, 
        hide_color=0, 
        num_samples=500
    )

    # 4. Extract the mask (the "heatmap") for the top predicted class
    temp, mask = explanation.get_image_and_mask(
        explanation.top_labels[0], 
        positive_only=False, 
        num_features=10, 
        hide_rest=False
    )

    # 5. Overlay boundaries and save to the media folder
    # We divide by 255.0 to normalize the image for matplotlib saving
    explanation_image = mark_boundaries(temp / 255.0, mask)
    plt.imsave(save_path, explanation_image)