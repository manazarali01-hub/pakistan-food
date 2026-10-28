"""Regression tests for recipe FAQ validation."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from faq_validation import validate_faqs


def faq(question, answer):
    return {"question": question, "answer": answer}


class ValidateFaqsTests(unittest.TestCase):
    def test_missing_optional_faqs_are_accepted(self):
        self.assertEqual(validate_faqs("test-recipe", None), [])

    def test_fewer_than_three_faqs_are_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Answer one."),
            faq("Question two?", "Answer two."),
        ])
        self.assertTrue(any("at least 3" in error for error in errors), errors)

    def test_non_list_faqs_are_rejected(self):
        errors = validate_faqs("test-recipe", "not a list")
        self.assertTrue(any("at least 3" in error for error in errors), errors)

    def test_non_object_faq_entry_is_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Answer one."),
            "not an object",
            faq("Question three?", "Answer three."),
        ])
        self.assertTrue(any("FAQ 2 must be an object" in error for error in errors), errors)

    def test_non_string_question_or_answer_is_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Answer one."),
            faq(None, "Answer two."),
            faq("Question three?", "Answer three."),
        ])
        self.assertTrue(any("question and answer must be strings" in error for error in errors), errors)

    def test_empty_question_or_answer_is_rejected(self):
        errors = validate_faqs("test-recipe", [
            faq("Question one?", "Answer one."),
            faq("   ", "Answer two."),
            faq("Question three?", ""),
        ])
        self.assertTrue(any("empty question or answer" in error for error in errors), errors)

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
            faq("Question one?", "Cook   until\\n tender."),
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
