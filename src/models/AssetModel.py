from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DatabaseEnum import DatabaseEnum
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from sqlalchemy.future import select
from sqlalchemy import func, delete

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = self.db_client
    
    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient):
        instance = cls(db_client=db_client)
        return instance 

    async def create_asset(self, asset: Asset):
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        return asset
    
    async def get_project_assets(self, asset_project_id: str, asset_file_type: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == asset_project_id,
                    Asset.asset_type == asset_file_type)
                assets = (await session.execute(query)).scalars().all()
        return assets
    
    
    async def get_asset_id(self, asset_project_id: str, asset_name: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == asset_project_id,
                    Asset.asset_name == asset_name)
                asset = (await session.execute(query)).scalar_one_or_none()
        return asset.asset_id
