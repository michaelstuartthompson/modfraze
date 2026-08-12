from db.database import engine
from db.models import Base


def main():
    Base.metadata.create_all(bind=engine)
    print("DB initialized OK ✅ (modfraze.db + trends table)")


if __name__ == "__main__":
    main()
 