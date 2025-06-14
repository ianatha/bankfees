import openparse
import fasttext
from huggingface_hub import hf_hub_download

# path = hf_hub_download("facebook/fasttext-el-vectors", "model.bin")
# model = fasttext.load_model(path)
# vec = model.get_word_vector("καλημέρα")

basic_doc_path = "./data/alpha/deltio-telon-alpha-misthodosia.pdf"
print("Initializing DocumentParser with custom table arguments...")
parser = openparse.DocumentParser(
	table_args={
        "table_output_format": "markdown",
		"parsing_algorithm": "table-transformers",
        # unitable doesn't work with Greek ocr
		"min_table_confidence": 0.8,
	},
)
parser._verbose = True
print("Parsing document:", basic_doc_path)
parsed_basic_doc = parser.parse(basic_doc_path)
print("Parsing completed.")

print()
print()
print("number of nodes:", len(parsed_basic_doc.nodes))
print()
i=0
for node in parsed_basic_doc.nodes:
	for elem in node.elements:
		i=i+1
		print(i)
		print(elem.variant)
		if isinstance(elem, openparse.TextElement):
			print(elem.text)
		elif isinstance(elem, openparse.TableElement):
			print(elem.text)
		else:
			print(elem)
		print()

	# if elem.type == "table":
	# 	print("Table found with", len(elem.rows), "rows and", len(elem.columns), "columns.")
	# 	for row in elem.rows:
	# 		print("Row:", [cell.text for cell in row.cells])
	# elif elem.type == "text":
	# 	print("Text element:", elem.text)
	# else:
	# 	print("Other element type:", elem.type)
