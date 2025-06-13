#!/usr/bin/env python3
# import camelot

from pdf2image import convert_from_path  # Convert PDF pages to PIL images
from transformers import (
    LayoutLMv3Processor,  # Processor for tokenizing and extracting layout features
    LayoutLMv3ForTokenClassification  # Model class for token classification tasks
)
from torch.nn.functional import softmax  # Function to convert logits to probabilities
import torch  # PyTorch library for tensor operations

# import pandas as pd  # (Optional) Uncomment to use pandas for DataFrame handling

def extract_fee_tables(pdf_path):  # Define a function that extracts fee info from a PDF
    print("converting PDF to images...")  # Log start of PDF-to-image conversion
    images = convert_from_path(pdf_path, dpi=300)  # Render each PDF page at 300 DPI into images
    print(f"Extracted {len(images)} pages from PDF.")  # Log number of pages processed

    processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")  # Load the pretrained processor
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        "microsoft/layoutlmv3-base",  # Pretrained model name
        num_labels=processor.tokenizer.vocab_size  # Set number of output labels (override if customized)
    )
    id2label = model.config.id2label  # Retrieve mapping from label IDs to label names

    print("Processing images with LayoutLMv2Processor...")  # Log start of preprocessing (note: message still references v2)
    encoded_pages = [processor(images=[img], return_tensors="pt") for img in images]  # Preprocess each page into tensors

    print("Processing complete. Extracting tokens and bounding boxes...")  # Log start of inference and extraction
    results = []  # Initialize list to store token-level results

    for enc in encoded_pages:  # Iterate over each preprocessed page
        outputs = model(**enc)  # Run token classification model on the page
        probs = softmax(outputs.logits, dim=-1)  # Convert raw logits to probabilities
        preds = torch.argmax(probs, dim=-1).squeeze().tolist()  # Select highest-probability label for each token

        tokens = processor.tokenizer.convert_ids_to_tokens(enc["input_ids"].squeeze())  # Decode token IDs to text
        boxes  = enc["bbox"].squeeze().tolist()  # Get bounding box coordinates for each token

        # Combine tokens, boxes, and predicted labels into result dicts
        for token, box, label_id in zip(tokens, boxes, preds):
            label = id2label[label_id]  # Lookup label name from ID
            results.append({  # Append a dict for this token
                "token": token,
                "box": box,
                "label": label
            })

    return results  # Return the list of token-level annotations

# Invoke the function on a sample PDF and print the extracted data
data = extract_fee_tables("data/alpha/deltio-telon-alpha-misthodosia.pdf")  # Replace with your PDF file path
print(data)  # Output the results to the console