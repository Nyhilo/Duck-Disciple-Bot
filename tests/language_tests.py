import core.language
from importlib import reload

def run_tests():
    reload(core.language)
    test_get_string()
    test_get_string_key_error()
    test_get_string_incomplete_path()


def test_get_string():
    # Arrange
    culture = core.language.Culture('core.reminders')

    # Act
    localization = culture.get_string('timestamped.reminder1', True)

    # Assert
    assert(localization == "I'll remind you about this at about ")
    print('test_get_string Passed')


def test_get_string_key_error():
    # Arrange
    culture = core.language.Culture('core.reminders')

    # Act
    try:
        localization = culture.get_string('timestamped.reminderNot1', True)
    
    # Assert
    except KeyError as e:
        assert(str(e) == "'Path does not exist in lang file'")

    print('test_get_string_key_error Passed')

def test_get_string_incomplete_path():
    # Arrange
    culture = core.language.Culture('core.reminders')

    # Act
    try:
        localization = culture.get_string('timestamped', True)

    # Assert
    except KeyError as e:
        assert(str(e) == "'Key does not lead to a string'")
    
    print('test_get_string_incomplete_path Passed')
