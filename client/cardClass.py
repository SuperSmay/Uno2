import storage.cardDictionaries as cardDictionaries

class Card:
    def __init__(self, color, face, isColorChoice = False, returnable = True):
        self.isColorChoice = isColorChoice
        self.color = color
        self.returnable = returnable
        self.face = face
        self.image = cardDictionaries.cardImages[str(face) + "_" + color]
        self.emoji = cardDictionaries.cardEmoji[str(face) + "_" + color]
        self.colorCode = self.getColorCode()

    def getColorCode(self):
        if self.color == "blue": return 29372               
        elif self.color == "green": return 5876292
        elif self.color == "yellow": return 16768534
        elif self.color == "red": return 15539236
        else: return 4802889

    ##def __eq__(self, card):
        return (self.face + self.color) == (card.face + card.color)

    def __str__(self):
        return f"{self.color} {self.face}"

class FakeCard:
    def __init__(self, card):
        self.isColorChoice = card.isColorChoice
        self.color = card.color
        self.returnable = False
        self.face = card.face
        self.image = cardDictionaries.cardImages[str(card.face) + "_" + card.color]
        self.emoji = cardDictionaries.cardEmoji[str(card.face) + "_" + card.color]
        self.colorCode = self.getColorCode()

    def getColorCode(self):
        if self.color == "blue": return 29372               
        elif self.color == "green": return 5876292
        elif self.color == "yellow": return 16768534
        elif self.color == "red": return 15539236
        else: return 4802889
