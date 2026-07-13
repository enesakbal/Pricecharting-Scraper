import pytest
from videogame import VideoGame


def test_videogame_stores_values():
    game = VideoGame("Super Mario Bros", "nes", "5.99", "12.99", "N/A")
    assert game.getTitle() == "Super Mario Bros"
    assert game.getConsole() == "nes"
    assert game.getLoosePrice() == "5.99"
    assert game.getCompletePrice() == "12.99"
    assert game.getNewPrice() == "N/A"


def test_videogame_repr():
    game = VideoGame("Zelda", "nes", "10.00", "20.00", "30.00")
    output = repr(game)
    assert "Zelda" in output
    assert "nes" in output


def test_videogame_na_prices():
    game = VideoGame("Rare Game", "nintendo-64", "N/A", "N/A", "N/A")
    assert game.getLoosePrice() == "N/A"
    assert game.getCompletePrice() == "N/A"
    assert game.getNewPrice() == "N/A"


def test_videogame_stores_images():
    game = VideoGame("Zelda", "nes", "10.00", "20.00", "30.00",
                     "https://img/60.jpg", "https://img/240.jpg")
    assert game.getImageSmall() == "https://img/60.jpg"
    assert game.getImageLarge() == "https://img/240.jpg"


def test_to_dict_flat_shape_with_images():
    game = VideoGame("Jack Bros.", "virtual-boy", "867.90", "2000.00", "4000.00",
                     "https://img/60.jpg", "https://img/240.jpg")
    assert game.to_dict() == {
        "game": "Jack Bros.",
        "loose": "867.90",
        "complete": "2000.00",
        "new": "4000.00",
        "image": {"small": "https://img/60.jpg", "large": "https://img/240.jpg"},
    }


def test_to_dict_omits_console():
    # console is carried by the filename, so it must not appear in the object
    game = VideoGame("Zelda", "nes", "10.00", "20.00", "30.00")
    assert "console" not in game.to_dict()


def test_to_dict_image_null_when_missing():
    game = VideoGame("Rare Game", "nintendo-64", "N/A", "N/A", "N/A")
    assert game.to_dict()["image"] is None
