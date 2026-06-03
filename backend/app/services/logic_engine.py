from typing import Any

from app.models.survey import Question


def _matches(expected: Any, actual: Any) -> bool:
    if isinstance(actual, list):
        return expected in actual
    return expected == actual


def next_question_code(questions: list[Question], current_code: str, answer: Any) -> str | None:
    current_index = next((index for index, question in enumerate(questions) if question.code == current_code), None)
    if current_index is None:
        return questions[0].code if questions else None

    current_question = questions[current_index]
    for rule in current_question.branch_rules or []:
        if _matches(rule.get("answer"), answer):
            target = rule.get("go_to_code")
            if any(question.code == target for question in questions):
                return target

    next_index = current_index + 1
    return questions[next_index].code if next_index < len(questions) else None


def answer_visible(question: Question, answers: dict[str, Any]) -> bool:
    conditions = question.display_conditions or []
    if not conditions:
        return True
    for condition in conditions:
        source_code = condition.get("go_to_code")
        expected = condition.get("answer")
        if source_code in answers and _matches(expected, answers[source_code]):
            return True
    return False


def calculate_score(questions: list[Question], answers: dict[str, Any]) -> int | None:
    total = 0
    found = False
    for question in questions:
        answer = answers.get(question.code)
        rules = question.scoring_rules or {}
        if answer is None:
            continue
        if isinstance(answer, list):
            for item in answer:
                if str(item) in rules:
                    total += int(rules[str(item)])
                    found = True
        elif str(answer) in rules:
            total += int(rules[str(answer)])
            found = True
        elif question.question_type in {"rating", "nps"}:
            total += int(answer)
            found = True
    return total if found else None
