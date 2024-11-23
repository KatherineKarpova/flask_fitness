from import_exercises import validate_csv
import pytest

def test_validate_csv():
    assert validate_csv('dog.csv') == True
    assert validate_csv('dog.CSV') == True
    with pytest.raises(SystemExit) as e:
        validate_csv('file.txt')
    assert str(e.value) == 'Please provide a csv file'