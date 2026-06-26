import sys
import tensorflow as tf

# Manually register the missing compatibility paths in the system's module cache
if 'tensorflow.compat.v1' not in sys.modules:
    try:
        # Check if it exists internally first
        import tensorflow._api.v2.compat.v1 as v1
        sys.modules['tensorflow.compat.v1'] = v1
    except ImportError:
        # If not, point it to the main tf module (which acts as v2/v1 bridge)
        sys.modules['tensorflow.compat.v1'] = tf.compat.v1 if hasattr(tf, 'compat') else tf