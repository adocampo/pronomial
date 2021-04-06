import unittest
from pronomial import replace_corefs


class TestCorefPT(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lang = "pt"

    def test_female(self):
        self.assertEqual(
            replace_corefs("A ana gosta de cães. Ela tem dois", lang="pt"),
            "A ana gosta de cães . ana tem dois"
        )

    def test_male(self):
        self.assertEqual(
            replace_corefs("o João gosta de gatos. Ele tem quatro", lang="pt"),
            "o João gosta de gatos . João tem quatro"
        )

    def test_plural(self):
        self.assertEqual(
            replace_corefs("Os americanos foram á lua. Eles são fodidos",
                           lang="pt"),
            "Os americanos foram á lua . americanos são fodidos"
        )