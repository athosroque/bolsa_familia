import unittest
import sys
import os
from datetime import datetime
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.connection import get_connection

class TestProjectSetup(unittest.TestCase):

    def test_database_connection(self):
        """Test if we can connect to Postgres"""
        conn = get_connection()
        self.assertIsNotNone(conn, "Failed to connect to Database")
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            conn.close()
            self.assertEqual(result[0], 1, "Database query failed")
            print("✅ Database Connection: FAST & OK")

    def test_table_existence(self):
        """Test if raw_bolsa_familia table exists"""
        conn = get_connection()
        self.assertIsNotNone(conn)
        if conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'raw_bolsa_familia'
                );
            """)
            exists = cur.fetchone()[0]
            conn.close()
            self.assertTrue(exists, "Table raw_bolsa_familia does not exist")
            print("✅ Database Schema: OK")

if __name__ == '__main__':
    print("🧪 Running System Verification Tests...")
    unittest.main(verbosity=2)
