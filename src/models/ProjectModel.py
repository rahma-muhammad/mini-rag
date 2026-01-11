from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DatabaseEnum import DatabaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.PROJECTS_COLLECTION.value]

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
                project_id=project_id
            )
        return Project(**record)
    
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        skips = page_size * (page - 1)
        projects = []
        cursor = await self.collection.find({}).skip(skips).limit(page_size)
        async for document in cursor:
            projects.append(Project(document))
        return projects