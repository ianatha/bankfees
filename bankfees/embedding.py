#!/usr/bin/env python3
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, HDBSCAN
import pandas as pd
import json
from utils import extract_pages_text
from time import sleep
import numpy as np
import fasttext
from huggingface_hub import hf_hub_download
from tqdm import tqdm
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

path = hf_hub_download("facebook/fasttext-el-vectors", "model.bin")
# path = hf_hub_download("nlpaueb/bert-base-greek-uncased-v1", "pytorch_model.bin")
# print("Loading FastText model from:", path)
model = fasttext.load_model(path)
# model = SentenceTransformer('dimitriz/st-greek-media-bert-base-uncased')

print("Model loaded successfully.")
root_dir = Path.cwd() / "data_new"


def weighted_mean_pooling(embeddings, decay_rate: float = 0.5, max_pages: int = 5) -> np.ndarray:
  # take up to max_pages
  selected = embeddings[:max_pages]
  # compute weights
  weights = np.exp(-decay_rate * np.arange(len(selected)))
  weights /= weights.sum()
  emb_mat = np.stack(selected)           # shape (n_pages, 768)
  return emb_mat.T @ weights             # (768, n_pages) @ (n_pages,) → (768,)


# subjects = [
#     "Δελτίο Πληροφόρησης Περί Τελών Δελτίο Πληροφόρησης Περί Τελών Δελτίο Πληροφόρησης Περί Τελών Δελτίο Πληροφόρησης Περί Τελών Δελτίο Πληροφόρησης Περί Τελών",
#     "Τιμολόγιο Εργασιών",
#     "Γενικοί Όροι Συναλλαγών",
#     # "Ειδικοί Όροι Τραπεζικών Εργασιών",
#     "Δελτίο Επιτοκίων",
# ]

# subject_vecs = [
#     model.encode(subject) for subject in subjects
# ]

pdf_fnames = {}

for bank_folder in tqdm(list(root_dir.iterdir()), desc="Banks", unit="bank", leave=True):
  if not bank_folder.is_dir():
    continue
  bank_name = bank_folder.name

  for pdf_file in tqdm(list(bank_folder.glob("*.pdf")), desc=f"  Processing PDFs in {bank_name}", unit="pdf", leave=False):
    if not pdf_file.is_file() or pdf_file.name.startswith("_"):
      continue

    pages_text = extract_pages_text(pdf_file, indent_level=2, limit=2)
    pages_vecs = []
    for p in pages_text:
      line_vecs = []
      for line in p.split("\n"):
        line_vecs.append(model.get_word_vector(line))
      pages_vecs.append(np.mean(line_vecs, axis=0))
    # pages_vecs = [
    #     model.get_sentence_vector(text) for text in tqdm(pages_text, desc=f"    Embedding pages in {pdf_file.name}", leave=False)
    # ]
    single_page_vec = np.mean(pages_vecs, axis=0)
    print(single_page_vec)
    # weighted_mean_pooling(
        # pages_vecs, decay_rate=0.7, max_pages=10)
    # find which subject is closest to the single_page_vec
    # subject_affinities = [
    #     np.dot(single_page_vec, subject_vec) for subject_vec in subject_vecs
    # ]
    # closest_subject_idx = np.argmax(subject_affinities)
    # closest_subject = subjects[closest_subject_idx]
    pdf_fnames[bank_name + "/" + pdf_file.name] = {
        # "closest_subject": closest_subject,
        "page_vec": single_page_vec,
    }

doc_names = list(pdf_fnames.keys())
doc_vecs = np.array([pdf_info["page_vec"] for pdf_info in pdf_fnames.values()])


def affinities(names, vecs):
  vecs = np.array(doc_vecs)
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
  return cosine_affinity


affinities = affinities(doc_names, doc_vecs)
print("Pairwise cosine affinities calculated.")
print(affinities)

tags = [
    "Disclosure",
    "DeltioPliroforisisPeriTelon",
    "PriceList",
    "PriceListExclusive",
    "GeneralTermsContract",
    "PaymentFees",
]

correct_tags = {
    'alpha/deltio-telon-alpha-misthodosia.pdf': 'DeltioPliroforisisPeriTelon',
    'alpha/deltio-telon-loipon-logariasmon-me-myalpha-benefit.pdf': 'DeltioPliroforisisPeriTelon',
    'alpha/deltio-telon-loipon-logariasmon-xoris-myalpha-benefit.pdf': 'DeltioPliroforisisPeriTelon',
    'alpha/dikaiologitika-idioton.pdf': 'PrivateCustomerDocumentation',
    'alpha/oroi-sunallagon-epitokia-katatheseon-xorigiseon.pdf': 'InterestRates',
    'alpha/oroi-sunallagon-promithies-loipa-eksoda.pdf': 'TransactionTermsFeesExpenses',
    'alpha/Plaisio_synergasias_Alpha_Bank.pdf': 'CooperationFramework',
    'alpha/pliromes-pros-etaireies.pdf': 'PaymentFees',
    'alpha/timologio-gold-personal-banking.pdf': 'PriceListExclusive',
    'alpha/vasiko_timologio_private_banking.pdf': 'PriceListExclusive',

    'attica/202503_genikoi_oroi_synallagon.pdf': 'GeneralTerms',
    'attica/cut_off_times.pdf': 'CutOffTimes',
    'attica/symmetechouses-etaireies-dias-direct-debit_20250602_el.pdf': 'PaymentFees',
    'attica/symmetechouses-etaireies-sto-dias-credit-transfer-entoles-pliromis_20250602_el.pdf': 'PaymentFees',
    'attica/timologio-trapezikon-ergasion-promitheies-exoda-se-ischy-clean.pdf': 'TimologioBankOperationsFees',

    'eurobank/csdr-gr.pdf': 'Disclosure',
    'eurobank/deltio-pliroforisis-peri-telon-tamieutirio-trexoumeno-blue.pdf': 'DeltioPliroforisisPeriTelon',
    'eurobank/deltio-pliroforisis-peri-telon-tamieutirio-trexoumeno-gold.pdf': 'DeltioPliroforisisPeriTelon',
    'eurobank/deltio-pliroforisis-peri-telon-tamieutirio-trexoumeno-platinum.pdf': 'DeltioPliroforisisPeriTelon',
    'eurobank/deltio-pliroforisis-peri-telon-tamieutirio-trexoumeno-silver.pdf': 'DeltioPliroforisisPeriTelon',
    'eurobank/deltio-pliroforisis-peri-telon.pdf': 'DeltioPliroforisisPeriTelon',
    'eurobank/emir.pdf': 'Disclosure',
    'eurobank/enimerosi-pelati-gia-apeutheias-upoboli-sunallagon.pdf': 'Disclosure',
    'eurobank/esa-warning-consumers-on-risks-of-crypto-assets.pdf': 'Disclosure',
    'eurobank/esms-final-erb-web.pdf': 'Disclosure',
    'eurobank/genikoi-oroi-sunallagon.pdf': 'GeneralTerms',
    'eurobank/oroi-ependutikon-upiresion.pdf': 'InvestmentServicesTerms',
    'eurobank/plan-alternative-benchmarks-eurobank-global-markets-gr.pdf': 'AlternativeBenchmarksPlan',
    'eurobank/timologio-personal-banking.pdf': 'PriceListExclusive',
    'eurobank/timologio-private-banking.pdf': 'PriceListExclusive',
    'eurobank/timologio-trapezikon-ergasion.pdf': 'PriceList',

    'nbg/Current_ProfPlus_FarmersPlus-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/e-Value-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/FinancialsupportFarmers-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/Premium-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/SalaryReward-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/SalaryValue-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/Savings_eur_Savings_Children_FamilyFast_ForeignCurrency-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/Student-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/Value-GR.pdf': 'DeltioPliroforisisPeriTelon',
    'nbg/Value-Plus-GR.pdf': 'DeltioPliroforisisPeriTelon',

    'nbg/web_portal_elliniko_epitokia-timologio_daneiwn.pdf': 'InterestRates',
    'nbg/web_portal_elliniko_epitokia-timologio_kartwn.pdf': 'InterestRates',
    'nbg/web_portal_elliniko_epitokia-timologio_katathesewn.pdf': 'InterestRates',
    'nbg/web_portal_elliniko_timologio_loipwn_ergasiwn.pdf': 'PriceList',
    'nbg/web_portal_elliniko_timologio_private_banking.pdf': 'PriceListExclusive',

    'piraeus/104651-28_03_25-GR.pdf': 'GeneralNotice',
    'piraeus/CSDR_Euroclear.pdf': 'Disclosure',
    'piraeus/CSDR_XAK.pdf': 'Disclosure',
    'piraeus/CSDR-_Clearstream-Banking-SA.pdf': 'Disclosure',
    'piraeus/CSDR-_ELKAT.pdf': 'Disclosure',
    'piraeus/Deposit-Accounts-Interest-Rates_14022023_Gr.pdf': 'InterestRates',
    'piraeus/Disclosure_Protection_Segregations_Levels.pdf': 'DisclosureProtectionSegregations',
    'piraeus/PaymentServices-Terms-and-Conditions-504801-Gr.pdf': 'PaymentServicesTermsAndConditions',
    'piraeus/PBOdigos31082017.pdf': 'Guide',
    'piraeus/price-12062025.pdf': 'PriceList',
    'piraeus/PRICE-29052025.pdf': 'PriceList',
    'piraeus/pricing_list_16052025.pdf': 'PriceList',
    'piraeus/Rates_el_27052025.pdf': 'InterestRates',
    'piraeus/Savings-Account-Fee-Information-Document-2023.pdf': 'SavingsAccountFeeInformation',
}
print()
print()
# print number of unique values in correct_tags
print(
    f"Number of unique tags in correct_tags: {len(set(correct_tags.values()))}")
# print tags
print("Unique tags in correct_tags:")
for tag in set(correct_tags.values()):
  print(f"  {tag}")
print()
print()
# ensure that all keys in pdf_fnames are in correct_tags
for fname in pdf_fnames.keys():
  if fname not in correct_tags:
    print(f"Warning: {fname} not found in correct_tags. Skipping...")
    continue
  pdf_fnames[fname]["correct_tag"] = correct_tags[fname]

# ensure that no extraneous keys are in correct_tags
for fname in correct_tags.keys():
  if fname not in pdf_fnames:
    print(
        f"Warning: {fname} found in correct_tags but not in pdf_fnames. Skipping...")
    continue

# clusterer = HDBSCAN(min_cluster_size=2, metric='euclidean')
clusterer = AgglomerativeClustering(
  n_clusters=len(tags),
  metric='cosine',  # 'euclidean', 'manhattan', 'cosine'
  linkage='average',  # 'ward', 'complete', 'average', 'single'
)
  # eps=0.19503186880121837, min_samples=4,     metric='cosine')
doc_vecs_norm = normalize(doc_vecs, norm='l2')

labels = clusterer.fit_predict(doc_vecs_norm)
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt

nbrs = NearestNeighbors(n_neighbors=4, metric='cosine').fit(doc_vecs_norm)
dists, _ = nbrs.kneighbors(doc_vecs_norm)
k_dist = np.sort(dists[:, 3])

from kneed import KneeLocator

x = range(len(k_dist))
kl = KneeLocator(x, k_dist, curve='convex', direction='increasing')
eps = k_dist[kl.knee]
print("Auto-detected eps:", eps)

plt.plot(k_dist)
plt.ylabel("4th NN cosine distance")
plt.xlabel("Points sorted")
plt.show()
print(labels)
unique_labels = np.unique(labels)
for label in unique_labels:
  cluster_texts = [doc_names[i]
                   for i in range(len(doc_names)) if labels[i] == label]
  print(f"Cluster {label}: {cluster_texts}")


raise "error"
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
