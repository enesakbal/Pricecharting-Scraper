class VideoGame:
    def __init__(self, title, console, loose_price, complete_price, new_price,
                 image_small=None, image_large=None):
        self.title = title
        self.console = console
        self.loose_price = loose_price
        self.complete_price = complete_price
        self.new_price = new_price
        self.image_small = image_small
        self.image_large = image_large

    def getTitle(self):
        return self.title

    def getConsole(self):
        return self.console

    def getLoosePrice(self):
        return self.loose_price

    def getCompletePrice(self):
        return self.complete_price

    def getNewPrice(self):
        return self.new_price

    def getImageSmall(self):
        return self.image_small

    def getImageLarge(self):
        return self.image_large

    def to_dict(self):
        """Serializes the game for the JSON output.

        The console is intentionally omitted — it is carried by the output
        filename (DD-MM-YYYY-<console>.json), so repeating it on every game
        would be redundant. Returns "image": null when no cover was found.
        """
        if self.image_small or self.image_large:
            image = {"small": self.image_small, "large": self.image_large}
        else:
            image = None

        return {
            "game": self.title,
            "loose": self.loose_price,
            "complete": self.complete_price,
            "new": self.new_price,
            "image": image,
        }

    def __repr__(self):
        return (
            f"Title: {self.title}\n"
            f"Console: {self.console}\n"
            f"Loose: ${self.loose_price}\n"
            f"Complete: ${self.complete_price}\n"
            f"New: ${self.new_price}\n"
        )
