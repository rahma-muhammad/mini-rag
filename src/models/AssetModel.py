from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DatabaseEnum import DatabaseEnum
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.ASSETS_COLLECTION.value]
    
    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance 

    async def init_collection(self):
        # Only run this if the collection does not exist yet
        collection_names = await self.db_client.list_collection_names()
        if DatabaseEnum.ASSETS_COLLECTION.value not in collection_names:
            self.collection = self.db_client[DatabaseEnum.ASSETS_COLLECTION.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )
    async def create_asset(self, asset: Asset):
        record = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.asset_id = record.inserted_id
        return asset
    
    async def get_project_assets(self, asset_project_id: str, assset_file_type: str):
        records = await self.collection.find({
            "asset_project_id": asset_project_id,
            "asset_type": assset_file_type
        }).to_list(length=None)
        return [Asset(**record) for record in records]
    
    async def get_asset_id(self, asset_project_id: str, asset_name: str):
        record = await self.collection.find_one({
            "asset_project_id": asset_project_id,
            "asset_name": asset_name
        })
        return record["_id"] if record else None
