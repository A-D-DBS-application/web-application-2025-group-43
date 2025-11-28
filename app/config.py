class Config:
    SECRET_KEY = "dev123"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://"
        "postgres.unkubiidacwqgpzbiuzd:capenta_database_43"
        "@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
