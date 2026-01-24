from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "qdrant"


class VectorDBDistantMetric(Enum):
    COSINE = "cosine"
    DOT = "dot"

    