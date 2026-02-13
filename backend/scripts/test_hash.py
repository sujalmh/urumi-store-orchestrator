import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password, verify_password

def test_hashing():
    # Test with a long password > 72 bytes
    long_password = "a" * 100
    print(f"Testing password length: {len(long_password)}")
    
    try:
        hashed = hash_password(long_password)
        print("Hashing successful!")
        
        is_valid = verify_password(long_password, hashed)
        print(f"Verification successful: {is_valid}")
        
        if not is_valid:
            print("ERROR: Verification failed!")
            exit(1)
            
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    test_hashing()
