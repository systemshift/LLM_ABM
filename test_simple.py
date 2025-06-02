"""
Simple test to verify core LLM-ABM functionality
"""

import llm_abm as abm

def test_basic_functionality():
    """Test all core functions work"""
    print("Testing LLM-ABM Core Functionality")
    print("=" * 40)
    
    # Test 1: Model creation
    print("1. Testing model creation...")
    config = {
        "grid": {"width": 10, "height": 10},
        "agents": {
            "test_agent": {"count": 5, "energy": 10}
        }
    }
    
    model = abm.create_model(config)
    assert len(model["agents"]) == 5
    assert model["grid"]["width"] == 10
    print("   ✓ Model creation successful")
    
    # Test 2: Rule addition
    print("2. Testing rule addition...")
    model = abm.add_rule(model, "random_movement", {})
    model = abm.add_rule(model, "energy_decay", {"rate": 2})
    assert len(model["rules"]) == 2
    print("   ✓ Rule addition successful")
    
    # Test 3: Single step
    print("3. Testing single step...")
    initial_step = model["step"]
    model = abm.step(model)
    assert model["step"] == initial_step + 1
    print("   ✓ Single step successful")
    
    # Test 4: Multiple steps
    print("4. Testing run simulation...")
    results = abm.run(model, steps=5)
    assert results["final_step"] >= model["step"]
    assert "summary" in results
    assert "metrics" in results
    print("   ✓ Run simulation successful")
    
    # Test 5: Export functionality
    print("5. Testing export...")
    json_export = abm.export(results, format="json")
    csv_export = abm.export(results, format="csv")
    summary_export = abm.export(results, format="summary")
    
    assert isinstance(json_export, str)
    assert isinstance(csv_export, str)
    assert isinstance(summary_export, str)
    assert "step,total_agents" in csv_export
    print("   ✓ Export functionality successful")
    
    print("\n" + "=" * 40)
    print("All tests passed! ✓")
    print("LLM-ABM MVP implementation is working correctly.")

if __name__ == "__main__":
    test_basic_functionality()
