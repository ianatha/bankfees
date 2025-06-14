#!/usr/bin/env python3

from transformers import AutoProcessor
from pdf2image import convert_from_path
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from torch.nn.functional import softmax
import torch
import pytesseract

print("loading processor")
# processor = AutoProcessor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
print("loading memo")
model     = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")

def process_page(img):
    print("image_to_data pre")
    ocr = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    print(ocr)
    words, boxes = [], []
    for i, text in enumerate(ocr['text']):
        print(text)
        if text.strip():
            words.append(text)
            x, y, w, h = (ocr[k][i] for k in ['left','top','width','height'])
            boxes.append([x, y, x+w, y+h])

    # chunk into <=512‐token batches
    results = []
    for i in range(0, len(words), 512):
        batch_words = words[i:i+512]
        batch_boxes = boxes[i:i+512]
        encoding = processor(
            batch_words,
            boxes=batch_boxes,
            truncation=True,
            max_length=512,
            return_overflowing_tokens=False,
            return_tensors="pt"
        )
        pixel_values = processor.feature_extractor(
            img, return_tensors="pt"
        ).pixel_values

        out = model(
            input_ids=encoding.input_ids,
            bbox=encoding.bbox,
            pixel_values=pixel_values,
            attention_mask=encoding.attention_mask
        )
        probs = softmax(out.logits, dim=-1)
        preds = torch.argmax(probs, dim=-1).squeeze().tolist()

        toks = processor.tokenizer.convert_ids_to_tokens(
            encoding.input_ids.squeeze()
        )
        bbs  = encoding.bbox.squeeze().tolist()
        for t, bb, l in zip(toks, bbs, preds):
            results.append({"token": t, "box": bb, "label": model.config.id2label[l]})

    return results

# Example usage on the first page of your PDF
pages = convert_from_path("data/alpha/deltio-telon-alpha-misthodosia.pdf", dpi=300)
page0 = pages[0]
annotations = process_page(page0)
print(f"Got {len(annotations)} token annotations from page 0")