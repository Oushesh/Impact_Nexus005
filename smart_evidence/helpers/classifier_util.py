import numpy as np

BOOLQA_PRED2LABEL = {0: "NEGATIVE", 1: "POSITIVE", 2: "NOT_RELATED"}
BOOLQA_LABEL2PRED = {"NEGATIVE": 0, "POSITIVE": 1, "NOT_RELATED": 2}
INSIGHT_CLASSIFIER_PRED2LABEL = {0: "HIDDEN", 1: "FEATURED"}
INSIGHT_CLASSIFIER_LABEL2PRED = {"HIDDEN": 0, "FEATURED": 1}


def _get_deduplicated_concept_pairs(company_concepts, impact_concepts):
    concept_pairs = []
    _seen_concept_pairs = set()
    for company_concept in company_concepts:
        for impact_concept in impact_concepts:
            concept_id_pair = (
                company_concept.id,
                impact_concept.id,
            )
            if concept_id_pair in _seen_concept_pairs:
                continue
            concept_pairs.append((company_concept, impact_concept,))
            _seen_concept_pairs.add(concept_id_pair)
    return concept_pairs


def _get_labels_with_groups(concept_pairs):
    candidate_labels = []
    label_groups = []
    groups = {}
    for label_group, (company_concept, impact_concept) in enumerate(concept_pairs):
        groups[label_group] = (company_concept, impact_concept)

        company_concept_text = company_concept.label
        impact_concept_text = impact_concept.label

        for label in [
            f"{company_concept_text} has positive impact on {impact_concept_text}",
            f"{company_concept_text} has negative impact on {impact_concept_text}",
            f"This is an example of how {company_concept_text} impacts {impact_concept_text}",
        ]:
            candidate_labels.append(label)
            label_groups.append(label_group)

    return candidate_labels, label_groups, groups


def _results_to_predictions(result, groups):
    # group x [contradiction, entailment] x labels
    group_scores = np.swapaxes(
        np.array(result["scores"]).reshape((len(groups), 3, 2)), 1, 2
    )

    predictions = []
    for group, group_score in enumerate(group_scores):
        logit = None
        label = "CONTRADICTION"

        contradiction_score = group_score.argmax(-1)
        polarity_score = group_score[:, :2].argmax(-1)

        if contradiction_score[1] == 2:
            label = "NOT_RELATED"
            logit = group_scores[group, 0, 2].item()
        elif np.array_equal(contradiction_score, [0, 0]):
            label = "POSITIVE_CONTRADICTION"
        elif np.array_equal(contradiction_score, [1, 1]):
            label = "NEGATIVE_CONTRADICTION"
        elif polarity_score[1] == 0 and polarity_score[0] != 0:
            label = "POSITIVE"
            logit = group_scores[group, 1, 0].item()
        elif polarity_score[1] == 1 or (
            group_score[0, 0] < group_score[0, 1]
            and group_score[1, 0] > group_score[1, 1]
        ):
            label = "NEGATIVE"
            logit = group_scores[group, 1, 1].item()

        predictions.append(
            {
                "company_concept": groups[group][0],
                "impact_concept": groups[group][1],
                "relation": label,
                "logit": logit,
            }
        )
    return predictions


def _get_qa_style_text_pairs(concept_pairs, text):
    text_concept_pairs = []
    for _, (company_concept, impact_concept) in enumerate(concept_pairs):
        text_concept_pairs.append(
            [
                f"What is the effect of {company_concept.label} on {impact_concept.label}?",
                text,
            ]
        )
    return text_concept_pairs


def _boolqa_results_to_predictions(concept_pairs, results):
    predictions = []
    for concept_pair, result in zip(concept_pairs, results,):
        company_concept, impact_concept = concept_pair
        predictions.append(
            {
                "company_concept": company_concept,
                "impact_concept": impact_concept,
                "relation": BOOLQA_PRED2LABEL[result.argmax()],
                "logit": results.max(),
            }
        )

    return predictions
