import pytest
from matrix_registration_bot.registration_api import RegistrationAPI

valid_tokens = ["TrwUI5zHm~Gn3M9Am", "gpWrPaFrbuP73A6N", "dada", "a", "1", "J_2NGPksUSbST1cp",
                "uERKLWlzIDhrVxQCSGLSmBdMEnKnnaOCNBUawgLgUyjjqnaIBFmMkJQATTpqhbXX"]
invalid_tokens = ["dajaj/aeofjj", "<script>alert(0)</script>", "&lt;script&gt;alert(&#39;1&#39;);&lt;/script&gt;",
                  "ɐuƃɐɯ", "register!", "uERKLWlzIDhrVxQCSGLSmBdMEnKnnaOCNBUawgLgUyjjqnaIBFmMkJQXAT65chars"]


def test_valid_token_format():
    for token in valid_tokens:
        if not RegistrationAPI.valid_token_format(token):
            raise AssertionError(f"Falsely said {token} is a invalid token")
    for token in invalid_tokens:
        if RegistrationAPI.valid_token_format(token):
            raise AssertionError(f"Falsely said {token} is a valid token")
