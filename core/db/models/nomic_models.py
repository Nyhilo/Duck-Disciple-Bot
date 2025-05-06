from typing import Union, List
from datetime import datetime


class Rule():
        def __init__(
            self,

            id: int = -1,
            active: Union[int, bool] = True) -> None:
        pass


class Ruleset():
    def __init__(
            self,
            gameId: int,
            rules: List[Rule],
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        pass


class Section():
    def __init__(
            self,
            name: str,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        pass


class NumericSection(Section):
    def __init__(
            self,
            name: str,
            section: int,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        super().__init__(name,id, active)
        pass


class TextSection(Section):
    def __init__(
            self,
            name: str,
            section: int,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        super().__init__(name,id, active)
        pass


class ListSection(Section):
    def __init__(
            self,
            name: str,
            section: int,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        super().__init__(name,id, active)
        pass


class TableSection(Section):
    def __init__(
            self,
            name: str,
            section: int,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        super().__init__(name,id, active)
        pass


class Gamestate():
    def __init__(
            self,
            gameId: int,
            sections: List[Section],
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        pass


class Playerstate():
    def __init__(
            self,
            name: str,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        pass


class NumericPlayerstate(Playerstate):
    def __init__(
            self,
            name: str,
            state: int,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        super().__init__(name,id, active)
        pass


class TextPlayerstate(Playerstate):
    def __init__(
            self,
            name: str,
            state: int,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        super().__init__(name,id, active)
        pass


class ListPlayerstate(Playerstate):
    def __init__(
            self,
            name: str,
            state: int,
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        super().__init__(name,id, active)
        pass


class Player():
    def __init__(
            self,
            guid: int,
            username: str,
            name: str,
            states: List[Playerstate],
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        pass


class Game():
    def __init__(
            self,
            guildId: int,
            name: str,
            subtitle: str,
            startTime: Union[int, datetime],
            endTime: Union[int, datetime],
            ruleset: Ruleset,
            gamestate: Gamestate,
            players: List[Player],
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        pass
