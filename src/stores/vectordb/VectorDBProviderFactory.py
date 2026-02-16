from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums
from controllers import BaseController

class VectorDBProviderFactory:
    def __init__(self, config: dict):
        self.config = config
        self.base_controller = BaseController()

    def create_provider(self, provider_name: str):
        vectordb_path = self.base_controller.get_database_path(
            db_name=self.config.VECTORDB_DIR_PATH
        )

        if provider_name == VectorDBEnums.QDRANT.value:
            return QdrantDBProvider(
                db_path=vectordb_path
            )
        else: 
            return None