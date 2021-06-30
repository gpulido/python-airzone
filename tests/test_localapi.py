"""Local Api tests."""
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
polls_test_path = os.path.join(THIS_DIR, "data/polls_test.csv")


def test_create_machine():
    """Test the creation of a machine and zones with a valid json."""
    pass
