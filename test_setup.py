"""
Test script to validate the LLM Analysis Quiz setup
"""
import asyncio
import sys
from config import Config
from browser_handler import BrowserHandler
from llm_handler import LLMHandler
from submission_handler import SubmissionHandler


async def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        config = Config()
        print(f"✓ Email: {config.EMAIL}")
        print(f"✓ Secret: {'*' * len(config.SECRET)}")
        print(f"✓ LLM Provider: {config.DEFAULT_LLM_PROVIDER}")
        print(f"✓ Quiz Timeout: {config.QUIZ_TIMEOUT}s")
        
        # Validate API keys
        if config.DEFAULT_LLM_PROVIDER == "anthropic":
            if config.ANTHROPIC_API_KEY:
                print(f"✓ Anthropic API Key: {'*' * 10}")
            else:
                print("✗ Anthropic API Key: Missing!")
                return False
        elif config.DEFAULT_LLM_PROVIDER == "openai":
            if config.OPENAI_API_KEY:
                print(f"✓ OpenAI API Key: {'*' * 10}")
            else:
                print("✗ OpenAI API Key: Missing!")
                return False
        
        print("✓ Configuration loaded successfully\n")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {str(e)}\n")
        return False


async def test_browser():
    """Test browser functionality"""
    print("Testing browser handler...")
    try:
        config = Config()
        browser = BrowserHandler(config)
        
        # Test with a simple page
        content = await browser.fetch_quiz_page("https://example.com")
        if content and "Example Domain" in content:
            print("✓ Browser can fetch and render pages")
        else:
            print("✗ Browser failed to fetch content")
            return False
        
        await browser.close()
        print("✓ Browser handler working\n")
        return True
    except Exception as e:
        print(f"✗ Browser error: {str(e)}\n")
        return False


async def test_llm():
    """Test LLM handler"""
    print("Testing LLM handler...")
    try:
        config = Config()
        llm = LLMHandler(config)
        
        # Simple test content
        test_quiz = """
        Q1. What is 2 + 2?
        Post your answer to https://example.com/submit with this JSON:
        {
            "email": "test@test.com",
            "secret": "test",
            "url": "https://example.com/quiz",
            "answer": 4
        }
        """
        
        result = await llm.solve_quiz(test_quiz, "https://example.com/quiz")
        
        if result:
            print(f"✓ LLM returned solution")
            print(f"  Submit URL: {result.get('submit_url')}")
            print(f"  Answer: {result.get('answer')}")
        else:
            print("✗ LLM failed to solve test quiz")
            return False
        
        await llm.close()
        print("✓ LLM handler working\n")
        return True
    except Exception as e:
        print(f"✗ LLM error: {str(e)}\n")
        return False


async def test_submission():
    """Test submission handler"""
    print("Testing submission handler...")
    try:
        config = Config()
        submitter = SubmissionHandler(config)
        
        print("✓ Submission handler initialized")
        await submitter.close()
        print("✓ Submission handler working\n")
        return True
    except Exception as e:
        print(f"✗ Submission error: {str(e)}\n")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("LLM Analysis Quiz - System Test")
    print("=" * 60 + "\n")
    
    results = {
        "Configuration": await test_config(),
        "Browser Handler": await test_browser(),
        "LLM Handler": await test_llm(),
        "Submission Handler": await test_submission()
    }
    
    print("=" * 60)
    print("Test Results:")
    print("=" * 60)
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! System is ready.")
        print("=" * 60)
        return 0
    else:
        print("Some tests failed. Please fix the issues above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
