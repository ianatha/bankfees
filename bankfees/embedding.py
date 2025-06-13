import numpy
import fasttext
from huggingface_hub import hf_hub_download

path = hf_hub_download("facebook/fasttext-el-vectors", "model.bin")
model = fasttext.load_model(path)
texts = [
	"καλημέρα καμηλιέρης",
	"τέλος έκδοσης πιστωτικής κάρτας",
	"αποστολή πιστωτικής κάρτας",
	"αποστολή πιστωτικής κάρτας σε πελάτη",
	"αποστολή πιστωτικής κάρτας σε πελάτη με αριθμό 1234567890",
	"αποστολή πιστωτικής κάρτας σε πελάτη με αριθμό 1234567890 και όνομα Γιώργος Παπαδόπουλος",
	"τελος έκδοσης χρεωστικής κάρτας",
	"αποστολή χρεωστικής κάρτας",
	"αποστολή χρεωστικής κάρτας σε πελάτη",
	"αποστολή χρεωστικής κάρτας σε πελάτη με αριθμό 1234567890",
	"αποστολή χρεωστικής κάρτας σε πελάτη με αριθμό 1234567890 και όνομα Μάριος Πισπιρίγκος",
]
print("Calculating word vectors for texts...")
vecs = [
	model.get_word_vector(text) for text in texts
]
# calculate pair-wise embedding affinity and distance by using numpy
import numpy as np
vecs = np.array(vecs)
if vecs.ndim == 1:
	vecs = vecs.reshape(1, -1)  # Ensure vecs is 2D for pairwise calculations
else:
	vecs = vecs.reshape(len(vecs), -1)
# Calculate cosine similarity and euclidean distances
X = np.vstack(vecs)  # shape: (N, D)
# Compute the L2 norms for each row
norms = np.linalg.norm(X, axis=1)  # shape: (N,)
# Outer product of norms to get all pairwise norm products
norm_matrix = np.outer(norms, norms)  # shape: (N, N)
# Dot product of all vectors with each other
dot_products = X @ X.T  # shape: (N, N)
# Cosine affinity (similarity) matrix
cosine_affinity = dot_products / norm_matrix

# (Optional) Cosine distance matrix
# cosine_distance = 1.0 - cosine_affinity

# Example: print the affinity matrix
print("Pairwise cosine affinity matrix:")
print(cosine_affinity)

# # Example: print the distance matrix
# print("\nPairwise cosine distance matrix:")
# print(cosine_distance)

