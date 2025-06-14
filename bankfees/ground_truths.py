from ground_schemata import BanksDocumentRoots, Bank

BankRootUrls = BanksDocumentRoots.model_validate(
    {
        Bank.ALPHA: [
            "https://www.alpha.gr/el/idiotes/support-center/isxuon-timologio-kai-oroi-sunallagon"
        ],
		Bank.ATTICA: [
			"https://www.atticabank.gr/el/eidikoi-oroi-trapezikon-ergasion-timologio-ergasion/",
			"https://www.atticabank.gr/el/genikoi-oroi-synallagon/",
		],
        Bank.PIRAEUS: [
			"https://www.piraeusbank.gr/el/support/epitokia-deltia-timwn",
			"https://www.piraeusbank.gr/el/support/synallaktikoi-oroi",
		],
        Bank.NBG: [
            "https://www.nbg.gr/el/footer/timologia-ergasiwn",
			"https://www.nbg.gr/el/footer/deltio-plhroforhshs-peri-telwn",
        ],
        Bank.EUROBANK: [
            "https://www.eurobank.gr/el/timologia",
			"https://www.eurobank.gr/el/oroi-sunallagon",
        ],
    }
)