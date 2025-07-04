import os
import random
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Config
IMG_SIZE = 160
BATCH_SIZE = 16
EPOCHS = 25
DATA_DIR = "extracted_faces"

# Preprocessing
def preprocess_image(img_path):
    img = load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img = img_to_array(img) / 255.0
    return img

# Triplet generation
def generate_triplets(data_dir):
    triplets = []
    persons = [p for p in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, p))]
    for person in persons:
        person_path = os.path.join(data_dir, person)
        imgs = os.listdir(person_path)
        if len(imgs) < 2:
            continue
        for _ in range(min(3, len(imgs) - 1)):
            anchor, positive = random.sample(imgs, 2)
            other_people = [
                p for p in persons
                if p != person and os.path.isdir(os.path.join(data_dir, p)) and len(os.listdir(os.path.join(data_dir, p))) > 0
            ]
            if not other_people:
                continue
            negative_person = random.choice(other_people)
            negative_imgs = os.listdir(os.path.join(data_dir, negative_person))
            negative = random.choice(negative_imgs)
            triplets.append((
                os.path.join(person_path, anchor),
                os.path.join(person_path, positive),
                os.path.join(data_dir, negative_person, negative)
            ))
    return triplets

# Triplet data generator
def triplet_generator(triplets, batch_size):
    while True:
        batch = random.sample(triplets, min(batch_size, len(triplets)))
        anchor_imgs, pos_imgs, neg_imgs = [], [], []
        for a, p, n in batch:
            anchor_imgs.append(preprocess_image(a))
            pos_imgs.append(preprocess_image(p))
            neg_imgs.append(preprocess_image(n))
        yield (
            (
                np.array(anchor_imgs, dtype=np.float32),
                np.array(pos_imgs, dtype=np.float32),
                np.array(neg_imgs, dtype=np.float32)
            ),
            np.zeros((len(batch),), dtype=np.float32)
        )

# Wrap generator for tf.data
def wrapped_generator():
    return triplet_generator(triplets, BATCH_SIZE)

# Create Dataset
def create_dataset(triplets):
    return tf.data.Dataset.from_generator(
        wrapped_generator,
        output_signature=(
            (
                tf.TensorSpec(shape=(None, IMG_SIZE, IMG_SIZE, 3), dtype=tf.float32),
                tf.TensorSpec(shape=(None, IMG_SIZE, IMG_SIZE, 3), dtype=tf.float32),
                tf.TensorSpec(shape=(None, IMG_SIZE, IMG_SIZE, 3), dtype=tf.float32)
            ),
            tf.TensorSpec(shape=(None,), dtype=tf.float32)
        )
    ).repeat().prefetch(tf.data.AUTOTUNE)

# Build embedding model
def build_embedding_model(input_shape=(IMG_SIZE, IMG_SIZE, 3)):
    base = tf.keras.applications.MobileNetV2(input_shape=input_shape, include_top=False, pooling='avg')
    base.trainable = False
    input_layer = layers.Input(shape=input_shape)
    x = base(input_layer)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Lambda(lambda x: tf.math.l2_normalize(x, axis=1))(x)
    return models.Model(input_layer, x)

# Siamese Network with Triplet Loss
class SiameseModel(tf.keras.Model):
    def __init__(self, embedding_model, margin=0.5):
        super().__init__()
        self.embedding = embedding_model
        self.margin = margin
        self.loss_tracker = tf.keras.metrics.Mean(name="loss")

    def call(self, inputs):
        a, p, n = inputs
        a = self.embedding(a)
        p = self.embedding(p)
        n = self.embedding(n)
        return a, p, n

    def train_step(self, data):
        inputs, _ = data
        with tf.GradientTape() as tape:
            a, p, n = self(inputs, training=True)
            pos_dist = tf.reduce_sum(tf.square(a - p), axis=1)
            neg_dist = tf.reduce_sum(tf.square(a - n), axis=1)
            loss = tf.maximum(pos_dist - neg_dist + self.margin, 0.0)
            loss = tf.reduce_mean(loss)
        grads = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.trainable_variables))
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}

    @property
    def metrics(self):
        return [self.loss_tracker]

# ==== MAIN TRAINING START ====
triplets = generate_triplets(DATA_DIR)
if len(triplets) < BATCH_SIZE:
    raise ValueError("Not enough valid triplets to start training. Please add more data.")

embedding_model = build_embedding_model()
siamese_model = SiameseModel(embedding_model)
siamese_model.compile(optimizer=optimizers.Adam(0.0001))

dataset = create_dataset(triplets)
steps_per_epoch = len(triplets) // BATCH_SIZE

history = siamese_model.fit(
    dataset,
    steps_per_epoch=steps_per_epoch,
    epochs=EPOCHS
)

# Save model
embedding_model.save("face_embedding_model.h5")

# Plot training loss
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Training Loss', color='blue')
plt.title('Siamese Network Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("training_loss_plot.png")
plt.show()
