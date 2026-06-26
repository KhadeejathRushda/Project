import cv2
import numpy as np
import tensorflow as tf
import os
from django.conf import settings
from keras.src.layers import Dense
from keras.src.dtype_policies.dtype_policy import DTypePolicy

# --- COMPATIBILITY PATCH START ---
# These overrides prevent the 'quantization_config' and 'registered_name' errors
# by filtering out unrecognized arguments during model loading.
original_dense_init = Dense.__init__
Dense.__init__ = lambda self, *args, **kwargs: original_dense_init(
    self, *args, **{k: v for k, v in kwargs.items() if k != 'quantization_config'}
)

original_policy_init = DTypePolicy.__init__
DTypePolicy.__init__ = lambda self, *args, **kwargs: original_policy_init(
    self, *args, **{k: v for k, v in kwargs.items() if k != 'registered_name'}
)
# --- COMPATIBILITY PATCH END ---

# Load model once when server starts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'Lung_V5_Final.keras')
model = tf.keras.models.load_model(MODEL_PATH)

class_names = ['NORMAL', 'Nodule', 'PNEUMONIA', 'TUBERCULOSIS', 'UNKNOWN']

def predict_diagnosis(image_path):
    # Load and Preprocess
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Apply CLAHE (Matches Training pipeline)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Back to RGB and Resize for EfficientNetV2-B3 (300x300)
    img_rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    img_resized = cv2.resize(img_rgb, (300, 300))
    
    # Scale pixels and expand dimensions
    img_array = np.expand_dims(img_resized, axis=0).astype(np.float32)
    img_preprocessed = tf.keras.applications.efficientnet_v2.preprocess_input(img_array)

    # Run AI Prediction
    preds = model.predict(img_preprocessed, verbose=0)
    class_idx = np.argmax(preds[0])
    
    return class_names[class_idx], float(preds[0][class_idx])