"""
Create HBase Tables
"""
import happybase

# HBase Configuration
HBASE_HOST = 'hbase'
HBASE_PORT = 9090

def create_tables():
    try:
        connection = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT)
        print("Connected to HBase")
        
        tables = connection.tables()
        print(f"Existing tables: {tables}")
        
        # Create 'movielens:movies'
        # Note: happybase usually handles 'table_name' directly. 
        # If namespace is used, it might be part of the name if configured.
        # But standard HBase thrift usually treats 'namespace:table' as the table name.
        
        table_name = 'movies'
        if table_name.encode() not in tables:
            print(f"Creating table {table_name}")
            connection.create_table(
                table_name,
                {'info': dict()}
            )
        else:
            print(f"Table {table_name} already exists")
            
        # Create 'ratings'
        table_name = 'ratings'
        if table_name.encode() not in tables:
            print(f"Creating table {table_name}")
            connection.create_table(
                table_name,
                {'info': dict()}
            )
        else:
            print(f"Table {table_name} already exists")
            
        connection.close()
        print("Tables created successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_tables()
