"""Database connection test for the new structure."""
import asyncio
from sqlalchemy import text
from app.core.config import settings
from app.core.supabase import supabase
from app.db import engine, AsyncSessionLocal


async def test_database():
    """Test database connection."""
    print("\n=== Testing Database Connection ===")
    print(f"Database URL: {settings.ASYNC_DATABASE_URL[:50]}...")
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✓ PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def test_session():
    """Test session factory."""
    print("\n=== Testing Session Factory ===")
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.scalars().all()
            
            print(f"✓ Session factory works!")
            print(f"  Tables found: {len(tables)}")
            for table in tables:
                print(f"    - {table}")
            return True
    except Exception as e:
        print(f"✗ Session query failed: {e}")
        return False


def test_supabase():
    """Test Supabase client."""
    print("\n=== Testing Supabase Client ===")
    print(f"Supabase URL: {settings.SUPABASE_URL}")
    print(f"Client created: {supabase is not None}")
    return supabase is not None


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Peer Evaluation - Database Connection Test")
    print("=" * 60)
    
    results = {
        "Supabase Client": test_supabase(),
        "Database Connection": await test_database(),
        "Session Factory": await test_session(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("⚠ Some tests failed.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
