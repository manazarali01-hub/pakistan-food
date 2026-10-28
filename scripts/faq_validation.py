"""Pure validation helpers for recipe FAQ data."""


def validate_faqs(slug, faqs):
    """Return validation errors for optional FAQ data on one recipe."""
    errors = []
    if faqs is None:
        return errors
    if not isinstance(faqs, list) or len(faqs) < 3:
        return [f"{slug}: faqs must contain at least 3 recipe-specific entries"]

    seen_questions = set()
    seen_answers = set()
    for faq_index, faq in enumerate(faqs, start=1):
        if not isinstance(faq, dict):
            errors.append(f"{slug}: FAQ {faq_index} must be an object")
            continue
        raw_question = faq.get("question")
        raw_answer = faq.get("answer")
        if not isinstance(raw_question, str) or not isinstance(raw_answer, str):
            errors.append(f"{slug}: FAQ {faq_index} question and answer must be strings")
            continue

        question = " ".join(raw_question.split())
        answer = " ".join(raw_answer.split())
        if not question or not answer:
            errors.append(f"{slug}: FAQ {faq_index} has an empty question or answer")

        normalized_question = question.casefold()
        normalized_answer = answer.casefold()
        if normalized_question and normalized_question in seen_questions:
            errors.append(f"{slug}: duplicate FAQ question: {question}")
        if normalized_answer and normalized_answer in seen_answers:
            errors.append(f"{slug}: duplicate FAQ answer: {answer}")
        seen_questions.add(normalized_question)
        seen_answers.add(normalized_answer)
    return errors
