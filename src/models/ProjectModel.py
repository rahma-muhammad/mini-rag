from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DatabaseEnum import DatabaseEnum
from motor.motor_asyncio import AsyncIOMotorClient

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.PROJECTS_COLLECTION.value]
    
    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance 

    async def init_collection(self):
        # Only run this if the collection does not exist yet
        collection_names = await self.db_client.list_collection_names()
        if DatabaseEnum.PROJECTS_COLLECTION.value not in collection_names:
            self.collection = self.db_client[DatabaseEnum.PROJECTS_COLLECTION.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )

    async def create_project(self, project: Project):
        record = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project._id = record.inserted_id
        return project
    
    async def get_project_or_create_one(self, project_id):
        record = await self.collection.find_one({
            "project_id": project_id
        })
        if record is None:
            return await self.create_project(
                project=Project(project_id=project_id)
            )
        return Project(**record)
    
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        skips = page_size * (page - 1)
        projects = []
        cursor = await self.collection.find({}).skip(skips).limit(page_size)
        async for document in cursor:
            projects.append(Project(document))
        return projects