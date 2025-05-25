from app.db.mongo import db
from app.models.age_group import AgeGroupCreate

async def init_db():
    # Verifica se já existem age groups
    if db.age_groups.count_documents({}) == 0:
        # Cria alguns age groups iniciais
        initial_age_groups = [
            AgeGroupCreate(min_age=0, max_age=12),
            AgeGroupCreate(min_age=13, max_age=17),
            AgeGroupCreate(min_age=18, max_age=25),
            AgeGroupCreate(min_age=26, max_age=35),
            AgeGroupCreate(min_age=36, max_age=50),
            AgeGroupCreate(min_age=51, max_age=100)
        ]
        
        for age_group in initial_age_groups:
            db.age_groups.insert_one(age_group.model_dump())
        
        print("Age groups iniciais criados com sucesso!")
    else:
        print("Age groups já existem no banco de dados.") 