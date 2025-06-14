from ground_schemata import BanksDocumentRoots, Bank

BankRootUrls = BanksDocumentRoots.model_validate(
    {
        Bank.ALPHA: [
            "https://www.alpha.gr/el/idiotes/support-center/isxuon-timologio-kai-oroi-sunallagon"
        ],
        Bank.PIRAEUS: [
			"https://www.piraeusbank.gr/el/support/epitokia-deltia-timwn"
		],
        Bank.NBG: [
            "https://www.nbg.gr/el/footer/timologia-ergasiwn",
        ],
        Bank.EUROBANK: [
            "https://www.eurobank.gr/el/timologia",
        ],
    }
)