"""Regression tests for recipe FAQ validation."""

import unittest

from faq_validation import validate_faqs


def faq(question, answer):
    return {"question": question, "answer": answer}


class ValidateFaqsTests(unittest.TestCase):
    def test_exact_duplicate_answers_are_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Boil until tender."),
            faq("Question two?", "Boil until tender."),
            faq("Question three?", "Serve while warm."),
        ])
        self.assertTrue(any("duplicate FAQ answer" in error for error in errors), errors)

    def test_case_insensitive_duplicate_answers_are_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Add fresh coriander."),
            faq("Question two?", "ADD FRESH CORIANDER."),
            faq("Question three?", "Serve immediately."),
        ])
        self.assertTrue(any("duplicate FAQ answer" in error for error in errors), errors)

    def test_whitespace_normalized_duplicate_answers_are_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Cook   until\n tender."),
            faq("Question two?", "Cook until tender."),
            faq("Question three?", "Season to taste."),
        ])
        self.assertTrue(any("duplicate FAQ answer" in error for error in errors), errors)

    def test_distinct_answers_are_accepted(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Soak the chickpeas overnight."),
            faq("Question two?", "Pressure-cook for 20 minutes."),
            faq("Question three?", "Add lemon juice just before serving."),
        ])
        self.assertFalse(any("duplicate FAQ answer" in error for error in errors), errors)

    def test_duplicate_questions_remain_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("How long should it cook?", "Cook until tender."),
            faq("  HOW long should it cook? ", "Season with salt."),
            faq("How should it be served?", "Serve warm."),
        ])
        self.assertTrue(any("duplicate FAQ question" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
