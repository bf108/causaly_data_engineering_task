import dataclasses


@dataclasses.dataclass
class KeywordPair:
    nlm_dcms_id: str
    keyword_1: str | None
    keyword_2: str | None
