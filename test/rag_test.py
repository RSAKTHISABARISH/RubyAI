import unittest
import sys
import os
import shutil
from dotenv import load_dotenv

# Add project root to path to ensure modules are found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utiles.rag_utiles import RubyRAG

# Ensure env vars are loaded (for OpenAI API Key)
load_dotenv()

class TestRubyRAG(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Define test paths
        self.test_db_path = "test_rag_db"
        self.test_docs_path = "test_docs_folder"
        self.test_file = os.path.join(self.test_docs_path, "test_info.txt")
        
        # Create dummy directory and file
        os.makedirs(self.test_docs_path, exist_ok=True)
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Ruby is a sophisticated AI assistant designed for education.\n")
            f.write("Ruby supports English, Malayalam, and Tamil languages.\n")
            f.write("System architecture includes a Mainframe and various Tools.\n")
        
        # Initialize RAG instance
        # Note: We assume OPENAI_API_KEY is present in env variables
        self.rag = RubyRAG(db_path=self.test_db_path, chunk_size=100, chunk_overlap=10)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove the temporary vector DB folder
        if os.path.exists(self.test_db_path):
            shutil.rmtree(self.test_db_path)
        
        # Remove temporary docs
        if os.path.exists(self.test_docs_path):
            shutil.rmtree(self.test_docs_path)

    def test_01_initialization(self):
        """Test Case 1: System Initialization"""
        print("\n[Test 1] Verifying Initialization...")
        self.assertIsNotNone(self.rag)
        self.assertEqual(self.rag.db_path, self.test_db_path)
        # Vectorstore should be None initially as we point to a non-existent DB path
        self.assertIsNone(self.rag.vectorstore)

    def test_02_add_documents(self):
        """Test Case 2: Adding Documents to Knowledge Base"""
        print("\n[Test 2] Verifying Document Ingestion...")
        self.rag.add_documents(self.test_file)
        
        # Check if vectorstore was created
        self.assertIsNotNone(self.rag.vectorstore)
        
        # Check if persistence directory was created
        self.assertTrue(os.path.exists(self.test_db_path))
        self.assertTrue(os.path.exists(os.path.join(self.test_db_path, "index.faiss")))

    def test_03_query_system(self):
        """Test Case 3: Querying the System"""
        print("\n[Test 3] Verifying Info Retrieval...")
        self.rag.add_documents(self.test_file)
        
        response = self.rag.query("What languages does Ruby support?")
        print(f"   Query Response: {response[:100]}...") # Print preview
        
        # Assertions to check if relevant keywords are retrieved
        self.assertIn("Malayalam", response)
        self.assertIn("Tamil", response)

    def test_04_query_without_db_error(self):
        """Test Case 4: Error Handling for Missing DB"""
        print("\n[Test 4] Verifying Error Handling...")
        
        # Initialize a fresh unconnected instance
        empty_rag = RubyRAG(db_path="non_existent_db")
        
        # Should raise RuntimeError because no docs added and no DB exists
        with self.assertRaises(RuntimeError):
            empty_rag.query("Hello?")

    def test_05_persistence_and_loading(self):
        """Test Case 5: Persistence and State Loading"""
        print("\n[Test 5] Verifying Persistence...")
        
        # 1. Create and save data
        self.rag.add_documents(self.test_file)
        del self.rag # Simulate restart
        
        # 2. Reload from same path
        new_rag = RubyRAG(db_path=self.test_db_path)
        
        # Vectorstore should be loaded automatically
        self.assertIsNotNone(new_rag.vectorstore)
        
        # 3. Verify data is still accessible
        response = new_rag.query("What is Ruby designed for?")
        self.assertIn("education", response)

if __name__ == "__main__":
    unittest.main()
