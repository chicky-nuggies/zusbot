import pandas as pd
from db_models import Outlet, Base
from sqlalchemy.orm import sessionmaker

def insert_outlets_from_csv(file_path):
    """Insert outlet data from CSV file into the database"""
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    print(f"Found {len(df)} outlets in CSV file")
    
    # Create database session
    Session = sessionmaker(bind=database.engine)
    session = Session()
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(database.engine)
        
        # Check if outlets already exist
        existing_count = session.query(Outlet).count()
        print(f"Current outlets in database: {existing_count}")
        
        # Clear existing outlets (optional - remove this if you want to append)
        if existing_count > 0:
            confirm = input("Database already has outlets. Clear existing data? (y/n): ")
            if confirm.lower() == 'y':
                session.query(Outlet).delete()
                session.commit()
                print("Cleared existing outlet data")
        
        # Insert new outlets
        outlets_added = 0
        for index, row in df.iterrows():
            # Check if outlet already exists
            existing_outlet = session.query(Outlet).filter_by(name=row['name']).first()
            
            if not existing_outlet:
                outlet = Outlet(
                    name=row['name'],
                    address=row['address']
                )
                session.add(outlet)
                outlets_added += 1
            else:
                print(f"Outlet '{row['name']}' already exists, skipping...")
        
        # Commit the transaction
        session.commit()
        print(f"✅ Successfully inserted {outlets_added} new outlets into the database!")
        
        # Verify the insertion
        total_outlets = session.query(Outlet).count()
        print(f"Total outlets in database: {total_outlets}")
        
        # Show a few sample outlets
        sample_outlets = session.query(Outlet).limit(5).all()
        print("\nSample outlets:")
        for outlet in sample_outlets:
            print(f"- {outlet.name}")
            print(f"  Address: {outlet.address[:100]}...")
            print()
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting outlets: {e}")
        
    finally:
        session.close()

# Run the function
insert_outlets_from_csv("zus_coffee_outlets_export.csv")