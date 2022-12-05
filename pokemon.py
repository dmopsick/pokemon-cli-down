# This class holds the information for the Pokémon that will actually battle
class Pokemon:

    def __init__(self, id, speciesName, nickname, \
    level, maxHp, attack, defense, \
        spAtk, spDef, speed, movesList, typeList, \
        currentHp):
        self.id = id
        self.speciesName = speciesName
        self.nickname = nickname
        self.level = level
        self.maxHp = maxHp
        self.attack = attack
        self.defense = defense
        self.spAtk = spAtk
        self.spDef = spDef
        self.speed = speed
        self.movesList = movesList
        self.typeList = typeList
        self.currentHp = currentHp
