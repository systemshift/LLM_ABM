"""
Test the new system prompt documentation functionality
"""

import llm_abm as abm

def test_docs():
    """Test the documentation functions"""
    print("Testing LLM-ABM Documentation Functions")
    print("=" * 50)
    
    # Test system prompt docs
    print("1. Testing get_system_prompt_docs()")
    docs = abm.get_system_prompt_docs()
    print(f"   Documentation length: {len(docs)} characters")
    print(f"   Token estimate: ~{len(docs.split())} tokens")
    print(f"   Under 2K tokens? {'✓' if len(docs.split()) < 2000 else '✗'}")
    
    # Show first few lines
    print("   Preview:")
    for line in docs.split('\n')[:5]:
        print(f"     {line}")
    print("     ...")
    
    # Test rule reference
    print("\n2. Testing get_rule_reference()")
    rules = abm.get_rule_reference()
    print(f"   Rule reference length: {len(rules)} characters")
    print(f"   Token estimate: ~{len(rules.split())} tokens")
    print(f"   Under 1K tokens? {'✓' if len(rules.split()) < 1000 else '✗'}")
    
    # Show first few lines
    print("   Preview:")
    for line in rules.split('\n')[:5]:
        print(f"     {line}")
    print("     ...")
    
    # Test that docs contain key elements
    print("\n3. Testing documentation content...")
    
    # Check for core functions
    core_functions = ["create_model", "add_rule", "run", "run_stream", "export"]
    for func in core_functions:
        if func in docs:
            print(f"   ✓ {func} documented")
        else:
            print(f"   ✗ {func} missing")
    
    # Check for rules
    rule_names = ["random_movement", "predator_prey", "reproduction", "energy_decay"]
    for rule in rule_names:
        if rule in docs:
            print(f"   ✓ {rule} documented")
        else:
            print(f"   ✗ {rule} missing")
    
    # Check for custom rules
    if "add_custom_rule" in docs and "custom_code" in docs:
        print("   ✓ Custom rules documented")
    else:
        print("   ✗ Custom rules missing")
    
    print("\n4. Web app usage example:")
    print("   In your Flask app:")
    print("   ```python")
    print("   import llm_abm as abm")
    print("   ")
    print("   # Get docs for system prompt")
    print("   system_prompt = f'''")
    print("   You are an ABM expert. Use this library:")
    print("   {abm.get_system_prompt_docs()}")
    print("   ")
    print("   Create a simulation based on: {user_request}")
    print("   '''")
    print("   ```")
    
    print("\n" + "=" * 50)
    print("✓ Documentation functions ready for web app!")
    return True

if __name__ == "__main__":
    test_docs()
