from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('mysql+pymysql://root:123456789@localhost:3306/ecommerce')

# engine = create_engine('postgresql://neondb_owner:npg_OMLQ5gTVWyx9@ep-hidden-dawn-a47ppa0k-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require')

# engine = create_engine('postgresql://ecommercedb_owner:npg_YA9SQxO0iHMv@ep-empty-pond-a52pesoh.us-east-2.aws.neon.tech/ecommercedb?sslmode=require')

SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

