#!/usr/bin/env python3

import json
from pathlib import Path
from doc_analysis import load_document_analysis


correct_classifications = {
    'alpha/deltio-telon-alpha-misthodosia.pdf': 'DeltioPliroforisisPeriTelon',
    'alpha/deltio-telon-loipon-logariasmon-me-myalpha-benefit.pdf': 'DeltioPliroforisisPeriTelon',
    'alpha/deltio-telon-loipon-logariasmon-xoris-myalpha-benefit.pdf': 'DeltioPliroforisisPeriTelon',
    'alpha/dikaiologitika-idioton.pdf': 'CustomerGuide',
    'alpha/oroi-sunallagon-epitokia-katatheseon-xorigiseon.pdf': 'InterestRates',
    'alpha/oroi-sunallagon-promithies-loipa-eksoda.pdf': 'PriceList',
    'alpha/Plaisio_synergasias_Alpha_Bank.pdf': 'GeneralTermsContract',
    'alpha/pliromes-pros-etaireies.pdf': 'PaymentFees',
    'alpha/timologio-gold-personal-banking.pdf': 'PriceListExclusive',
    'alpha/vasiko_timologio_private_banking.pdf': 'PriceListExclusive',

    'attica/202503_genikoi_oroi_synallagon.pdf': 'GeneralTermsContract',
    'attica/cut_off_times.pdf': 'CustomerGuide',
    'attica/symmetechouses-etaireies-dias-direct-debit_20250602_el.pdf': 'PaymentFees',
    'attica/symmetechouses-etaireies-sto-dias-credit-transfer-entoles-pliromis_20250602_el.pdf': 'PaymentFees',
    'attica/timologio-trapezikon-ergasion-promitheies-exoda-se-ischy-clean.pdf': 'PriceList',

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
    'eurobank/genikoi-oroi-sunallagon.pdf': 'GeneralTermsContract',
    'eurobank/oroi-ependutikon-upiresion.pdf': 'GeneralTermsContract',
    'eurobank/plan-alternative-benchmarks-eurobank-global-markets-gr.pdf': 'Disclosure',
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

    'nbg/web_portal_elliniko_epitokia-timologio_daneiwn.pdf': 'PriceList',
    'nbg/web_portal_elliniko_epitokia-timologio_kartwn.pdf': 'PriceList',
    'nbg/web_portal_elliniko_epitokia-timologio_katathesewn.pdf': 'PriceList',
    'nbg/web_portal_elliniko_timologio_loipwn_ergasiwn.pdf': 'PriceList',
    'nbg/web_portal_elliniko_timologio_private_banking.pdf': 'PriceListExclusive',

    'piraeus/104651-28_03_25-GR.pdf': 'GeneralTermsContract',
    'piraeus/CSDR_Euroclear.pdf': 'Disclosure',
    'piraeus/CSDR_XAK.pdf': 'Disclosure',
    'piraeus/CSDR-_Clearstream-Banking-SA.pdf': 'Disclosure',
    'piraeus/CSDR-_ELKAT.pdf': 'Disclosure',
    'piraeus/Deposit-Accounts-Interest-Rates_14022023_Gr.pdf': 'InterestRates',
    'piraeus/Disclosure_Protection_Segregations_Levels.pdf': 'Disclosure',
    'piraeus/PaymentServices-Terms-and-Conditions-504801-Gr.pdf': 'GeneralTermsContract',
    'piraeus/PBOdigos31082017.pdf': 'CustomerGuide',
    'piraeus/price-12062025.pdf': 'PriceList',
    'piraeus/PRICE-29052025.pdf': 'PriceList',
    'piraeus/pricing_list_16052025.pdf': 'PriceList',
    'piraeus/Rates_el_27052025.pdf': 'InterestRates',
    'piraeus/Savings-Account-Fee-Information-Document-2023.pdf': 'DeltioPliroforisisPeriTelon',
}


def load_classification_results(data_dir: Path) -> dict[str, str]:
  """
  Load classification results from DocumentAnalysis files.
  """
  classifications = {}
  
  # Iterate through all subdirectories (banks)
  for bank_dir in data_dir.iterdir():
    if bank_dir.is_dir() and not bank_dir.name.startswith('_'):
      # Iterate through PDF files in each bank directory
      for pdf_file in bank_dir.glob('*.pdf'):
        try:
          doc_analysis = load_document_analysis(pdf_file)
          relative_path = f"{bank_dir.name}/{pdf_file.name}"
          classifications[relative_path] = doc_analysis.category.value
        except Exception as e:
          print(f"Error loading analysis for {pdf_file}: {e}")
  
  return classifications


def compare_classifications(correct: dict[str, str], loaded: dict[str, str]) -> None:
  """
  Compare the correct classifications with the loaded classifications and print the results.
  """
  correct_count = 0
  incorrect = 0
  not_classified = 0
  for file_name, correct_category in correct.items():
    loaded_category = loaded.get(file_name)
    if loaded_category is None:
      print(f"{file_name}: Not classified")
      not_classified += 1
    elif loaded_category == correct_category:
      correct_count += 1
    else:
      print(f"{file_name}: Incorrectly classified as {loaded_category}, should be {correct_category}")
      incorrect += 1
  total = correct_count + incorrect + not_classified
  print("Correctness: {:.2f}%".format(
      (correct_count / total) * 100 if total > 0 else 0))


def main():
  # Define the path to the data directory
  data_dir = Path.cwd() / "data_new"

  # Load the classification results from DocumentAnalysis files
  loaded_classifications = load_classification_results(data_dir)

  # Compare the classifications
  compare_classifications(correct_classifications, loaded_classifications)


if __name__ == "__main__":
  main()
