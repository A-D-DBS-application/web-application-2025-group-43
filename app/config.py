class Config:
    SECRET_KEY = "dev123"

    # ⬇️ VUL HIER JE EIGEN SUPABASE WACHTWOORD IN
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres.unkubiidacwqgpzbiuzd:capenta_database_43"
        "@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
