import re
from spacy.language import Language
from spacy.pipeline import EntityRuler
from spacy.tokens import Span


@Language.factory(
    "ix_entity_ruler_filter",
)
def create_ix_entity_ruler_component(
    nlp: Language,
    name: str,
):
    return IXEntityRulerFilter(nlp, name)


class IXEntityRulerFilter:
    PARENTHESES = ["(", "[", ")", "]"]
    REFERENCE_WORDS = [
        "figure",
        "fig",
        "table",
        "annex",
        "chapter",
        "section",
        "box",
        "page",
        "pp",
    ]

    def __init__(
        self,
        nlp: Language,
        name: str = "keyword_ruler",
    ):
        pass

    def __call__(self, doc):
        new_ents = []
        for ent in doc.ents:
            if ent.label_ == "REFERENCE_VALUE":
                # filter: table 10.2
                if any(
                    (
                        tok.lower_ in self.REFERENCE_WORDS
                        or ent[0].head.lower_ in self.REFERENCE_WORDS
                        for tok in ent
                    )
                ):
                    continue

                # filter: Figure in 1.10.2
                if re.match(r"\d+\.\d+\.\d+", ent.text):
                    continue

                # filter: 1.10.2 Chapter 1
                if ent.start == 0:
                    continue

                # match: [10% of global supply]
                preps = []
                for tok in ent:
                    preps += [c for c in tok.children if c.dep_ == "prep"]
                    if (
                        tok.dep_ == "pobj"
                        and tok.head.dep_ == "prep"
                        and tok.head.head.pos_ == "NOUN"
                    ):
                        preps += [tok.head.head]
                for prep in preps:
                    ent.start = min([ent.start] + [t.i for t in prep.subtree])
                    ent.end = max([ent.end] + [t.i + 1 for t in prep.subtree])

                # exclude: only [10%]
                if doc[ent.start].lower_ == "only":
                    ent.start += 1

                if ent.start > 0 and doc[ent.start - 1].pos_ == "DET":
                    ent.start -= 1

            new_ents.append(ent)
        try:
            doc.ents = new_ents
        except:
            pass
        return doc


def _build_sdg_patterns(base_patterns):
    goal_patterns = []

    for goal_num in range(1, 18):
        goal_patterns.extend(
            [
                {
                    "label": "SDG",
                    "pattern": pattern,
                    "id": f"sdg_{goal_num};SDG {goal_num}",
                }
                for pattern in [
                    [{"LOWER": "sdg"}, {"LOWER": {"REGEX": f"^{goal_num}\)?$"}}],
                    [
                        {"LOWER": "sdg", "OP": "?"},
                        {"LOWER": "goal"},
                        {"LOWER": {"REGEX": f"^{goal_num}\)?$"}},
                    ],
                    [
                        {"LOWER": "sdg", "OP": "?"},
                        {"LOWER": "target"},
                        {"LOWER": {"REGEX": f"^{goal_num}\.\d+\)?$"}},
                    ],
                    [
                        {"LOWER": "sdg", "OP": "?"},
                        {"LOWER": "indicator"},
                        {"LOWER": {"REGEX": f"^{goal_num}\.(\d+|[a-z]).\d+\)?$"}},
                    ],
                ]
            ]
        )

    return base_patterns + goal_patterns


BASE_SDG_PATTERNS = [
    {"label": "SDG", "pattern": [{"LOWER": {"IN": ["sdg", "sdgs"]}}], "id": "sdg;SDG"},
    {
        "label": "SDG",
        "pattern": [
            {"LOWER": "sustainable"},
            {"LOWER": "development"},
            {"LOWER": {"IN": ["goals", "goal"]}},
        ],
        "id": "sdg;SDG",
    },
]


@Language.factory("ix_entity_ruler")
def make_optional_pattern_component(nlp: Language, name: str):
    """Construct a RelationExtractor component."""
    ruler = EntityRuler(nlp, name=name, overwrite_ents=True)
    ruler.add_patterns(_build_sdg_patterns(BASE_SDG_PATTERNS))
    ruler.add_patterns(REFERENCE_VALUE_PATTERNS)
    return ruler


UNIT_LOWERS = [
    "metre",
    "meter",
    "m",
    "l",
    "mg" "square metre",
    "m2",
    "cubic meter",
    "m3",
    "kilogram",
    "kg",
    "tonne",
    "ton",
    "hectare",
    "liter",
    "litre",
    "g",
    "cm",
    "c",
    "°",
    "/",
    "km",
    "db",
    "mtco2e",
    "mtco",
    "tco",
    "kgco",
    "kgco2e",
    "tco2e",
    "eq",
    "CO",
    "2"
    # currencies
    "pesos",
    "reais",
]

COMPARATIVES = [
    "double",
    "doubled",
    "triple",
    "tripled",
    "quadruple",
    "quadrupled",
]

COMPARE_WORDS = [
    "more",
    "less",
    "greater",
    "smaller",
    "than",
    "per",
    "below",
    "over",
    "under",
    "down",
    "up",
    "much",
    "least",
    "higher",
    "lower",
    "far",
    "larger",
    "almost",
    "above",
    "fewer",
    "few",
    "bigger",
    "most",
    "mostly",
    "significantly",
    "considerably",
    "increasing",
    "decreasing",
    "every",
    "additional",
    "roughly",
    "approximately",
    "around",
    "just",
    "average",
    "rather",
    "so",
]

TERMS_LOWERS = ["emmissions", "ghg", "share", "cagr", "agr"]


REFERENCE_VALUE_PATTERNS = [
    {
        "label": "REFERENCE_VALUE",
        "pattern": [{"ENT_TYPE": "PERCENT", "OP": "+"}],
    },
    {"label": "REFERENCE_VALUE", "pattern": [{"ENT_TYPE": "MONEY", "OP": "+"}]},
    {
        "label": "REFERENCE_VALUE",
        "pattern": [{"ENT_TYPE": "CARDINAL", "OP": "+"}],
    },
    {
        "label": "REFERENCE_VALUE",
        "pattern": [{"ENT_TYPE": "QUANTITY", "OP": "+"}],
    },
    # one-third lighter
    {
        "label": "REFERENCE_VALUE",
        "pattern": [{"ENT_TYPE": "CARDINAL", "OP": "+"}, {"POS": "ADJ"}],
    },
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"LOWER": {"IN": ["usd", "$", "eur", "€"]}, "OP": "?"},
            {"ENT_TYPE": "MONEY", "OP": "+"},
            {"LOWER": {"IN": ["usd", "$", "eur", "€"]}, "OP": "?"},
        ],
    },
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"ENT_TYPE": "CARDINAL", "OP": "+"},
            {"LOWER": {"IN": UNIT_LOWERS + TERMS_LOWERS}},
        ],
    },
]

REFERENCE_VALUE_EXTEND_PATTERNS = [
    # 100 - 1200 $/kg
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"ENT_TYPE": "REFERENCE_VALUE"},
            {"ORTH": "-", "OP": "?"},
            {"ENT_TYPE": "REFERENCE_VALUE"},
            {"ORTH": "/", "OP": "?"},
            {"POS": "NOUN", "OP": "+"},
        ],
        "id": "quantity",
    },
    # 10EUR (10USD)
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"ENT_TYPE": "REFERENCE_VALUE", "OP": "+"},
            {"ORTH": {"IN": ["(", "]"]}},
            {"ENT_TYPE": "REFERENCE_VALUE", "OP": "+"},
            {"ORTH": {"IN": [")", "]"]}},
        ],
        "id": "quantity",
    },
    # around 5.2%
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"LOWER": {"IN": COMPARE_WORDS}, "OP": "+"},
            {"ENT_TYPE": "REFERENCE_VALUE"},
        ],
    },
    # CAGR of 5.2%
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"LOWER": {"IN": TERMS_LOWERS}},
            {"LOWER": "of"},
            {"ENT_TYPE": "REFERENCE_VALUE"},
        ],
    },
    # 5$/kg, 5kg, 5% CAGR
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"ENT_TYPE": "REFERENCE_VALUE"},
            {"ORTH": "/", "OP": "?"},
            {"LOWER": {"IN": UNIT_LOWERS + TERMS_LOWERS}, "OP": "+"},
        ],
    },
    # 5$/kg per year
    {
        "label": "REFERENCE_VALUE",
        "pattern": [
            {"ENT_TYPE": "REFERENCE_VALUE"},
            {"LOWER": "per"},
            {"LOWER": "year"},
        ],
    },
]


@Language.factory("reference_value_expansion")
def make_optional_pattern_component(nlp: Language, name: str):
    ruler = EntityRuler(nlp, name=name, overwrite_ents=True)
    ruler.add_patterns(REFERENCE_VALUE_EXTEND_PATTERNS)
    return ruler
