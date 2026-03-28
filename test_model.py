import tensorflow as tf
import pickle

model = tf.keras.models.load_model("problem_model_aug.h5")
print(model.input_shape)
print(model.output_shape)
with open("problem_classes.pkl", "rb") as f:
    classes = pickle.load(f)
print(classes)
