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
