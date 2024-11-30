from app.database import Base, engine
from app.models import User  # Ensure all models are imported

# Create the database tables
Base.metadata.create_all(bind=engine)

print("Database initialized successfully.")