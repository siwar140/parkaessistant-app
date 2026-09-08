import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import librosa
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# PARAMÈTRES EXACTS (SPECTROGRAMME LINÉAIRE)
# ==========================================================
IMG_HEIGHT = 257
IMG_WIDTH = 59
DURATION = 1.0
SR_TARGET = 8000
N_FFT = 512
HOP_LENGTH = 128

TRAIN_MEAN = -42.3466
TRAIN_STD = 19.0233
THRESHOLD = 0.2

WEIGHTS_PATH = os.getenv("MODEL_PATH", "./models_ia/parkinson_cnn+aug_off_weights_bst.h5")

# ==========================================================
# ARCHITECTURE DU MODÈLE
# ==========================================================
def create_model():
    model = models.Sequential([
        layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 1)),
        
        layers.Conv2D(16, (3,3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2,2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(32, (3,3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2,2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(64, (3,3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2,2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(64, (3,3), padding="same", activation="relu"),
        layers.Dropout(0.25),
        
        layers.GlobalAveragePooling2D(),
        
        layers.Dense(32, activation="relu"),
        layers.Dense(1, activation="sigmoid")
    ])
    return model

# ==========================================================
# CHARGEMENT DU MODÈLE
# ==========================================================
model = None

def load_model_once():
    global model
    if model is None:
        if not os.path.exists(WEIGHTS_PATH):
            raise FileNotFoundError(f"Fichier de poids non trouvé: {WEIGHTS_PATH}")
        
        model = create_model()
        model.load_weights(WEIGHTS_PATH)
        model.compile(optimizer='adam', loss='binary_crossentropy')
        
        print(f"[OK] Modèle chargé depuis: {WEIGHTS_PATH}")
    return model


# ==========================================================
# CRÉATION DU SPECTROGRAMME LINÉAIRE
# ==========================================================
def create_spectrogram(file_path):
    try:
        # Charger l'audio à 8000 Hz
        audio, sr = librosa.load(
            file_path,
            sr=SR_TARGET,
            mono=True,
            duration=None
        )
        
        # Garantir qu'on a au moins 1 seconde de signal (8000 échantillons)
        target_length = int(SR_TARGET * DURATION)
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')
        else:
            audio = audio[:target_length]
        
        stft = librosa.stft(
            y=audio,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )
        
        spec = np.abs(stft)
        spec_db = librosa.amplitude_to_db(spec, ref=np.max)
        
        if spec_db.shape[1] < IMG_WIDTH:
            pad_width = IMG_WIDTH - spec_db.shape[1]
            spec_db = np.pad(spec_db, ((0, 0), (0, pad_width)), mode='constant')
        else:
            spec_db = spec_db[:, :IMG_WIDTH]
        
        spec_norm = (spec_db - TRAIN_MEAN) / TRAIN_STD
        spec_norm = spec_norm[..., np.newaxis].astype(np.float32)
        spec_norm = np.expand_dims(spec_norm, axis=0)
        
        return spec_norm
        
    except Exception as e:
        raise ValueError(f"Erreur lors du traitement audio: {e}")


# ==========================================================
# PRÉDICTION
# ==========================================================
def predict(file_path):
    """Effectue la prédiction sur un fichier audio."""
    try:
        model = load_model_once()
        spectrogram = create_spectrogram(file_path)
        prediction = model.predict(spectrogram, verbose=0)
        probability = float(prediction[0][0])
        
        result = "Malade" if probability > THRESHOLD else "Sain"
        confidence = probability if probability > THRESHOLD else 1 - probability
        
        return {
            "result": result,
            "confidence": confidence,
            "probability": probability
        }
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la prédiction: {e}")

# ==========================================================
# ALIAS POUR COMPATIBILITÉ AVEC prediction.py
# ==========================================================
def predict_file(file_path):
    """Alias de predict pour la compatibilité avec l'API."""
    return predict(file_path)