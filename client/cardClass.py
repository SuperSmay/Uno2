import storage.cardDictionaries as cardDictionaries

class Card:
    def __init__(self, color: str, face, returnable: bool = True):
        '''
        A card object for Uno.\n
        Attributes:
            - color: str; The color of the card
            - returnable: bool; Whether or not the card should be put back in the deck when played
            - face: str or int; The number or type of the card
            - image: str; A link to the image for the card
            - emoji: str; The emoji code for the card
        '''
        self.color = color  #The color of the card stored as a string.
        self.returnable = returnable  #Boolean used to define if the card is one that should be returned the the deck. Default true.
        self.face = face  #The face of the card, either its number or the name of its type. Ex: 1, 7, "skip", "plus4"
        self.image = cardDictionaries.cardImages[str(face) + "_" + color]  #Gets the image for the card as a link
        self.emoji = cardDictionaries.cardEmoji[str(face) + "_" + color]  #Gets the emojo tag for the card
        self.colorCode = self._getColorCode()  #Gets the color code of the card, used for embed colors

    def _getColorCode(self) -> int:
        '''
        Returns: int; The color code for the this card
        '''
        if self.color == "blue": return 29372               
        elif self.color == "green": return 5876292
        elif self.color == "yellow": return 16768534
        elif self.color == "red": return 15539236
        else: return 4802889

    def __str__(self) -> str:  #When this object is cast to a string, this is what it well show as
        return f"{self.color} {self.face}"