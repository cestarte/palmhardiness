from prepare_database import create_tables
from application import app

def main():
    # always create the database
    create_tables('palmhardiness.db')
    app.run(debug=True)

if __name__ == "__main__":
    main()
