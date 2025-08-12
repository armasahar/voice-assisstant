from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import os

# Path to your recorded voice file
voice_path = os.path.join("sounds", "arma_reference.wav")

print(f"Loading your voice from: {voice_path}")
wav = preprocess_wav(voice_path)

print("Encoding your voice...")
encoder = VoiceEncoder()
embedding = encoder.embed_utterance(wav)

# Save your voice's unique embedding
np.save("arma_embedding.npy", embedding)
print("Voice embedding saved as arma_embedding.npy")

